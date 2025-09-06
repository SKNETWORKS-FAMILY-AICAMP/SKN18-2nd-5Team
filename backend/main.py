"""
호텔 예약 취소 예측 및 조식 예측 서비스 백엔드 API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from pydantic import BaseModel
import joblib
import os
from pathlib import Path

# ML 모델 관련 임포트
from ml_model import CancellationPredictor
from database import (
    load_hotel_data, 
    get_bookings_by_date,
    get_bookings_by_date_from_db,
    get_bookings_count_by_date
)

app = FastAPI(
    title="Hotel Booking Prediction API",
    description="호텔 예약 취소 예측 및 조식 준비 인원 예측 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React Vite 기본 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델들
class PredictionRequest(BaseModel):
    date: str  # YYYY-MM-DD 형식
    hotel_type: Optional[str] = "Resort Hotel"
    
class BookingFeatures(BaseModel):
    lead_time: int
    adults: int
    children: int
    babies: int
    meal: str
    country: str
    market_segment: str
    distribution_channel: str
    is_repeated_guest: int
    previous_cancellations: int
    previous_bookings_not_canceled: int
    booking_changes: int
    deposit_type: str
    days_in_waiting_list: int
    customer_type: str
    adr: float
    required_car_parking_spaces: int
    total_of_special_requests: int

class PredictionResponse(BaseModel):
    date: str
    total_reservations: int
    predicted_cancellations: int
    expected_checkins: int
    breakfast_recommendation: int
    confidence_level: float
    details: Dict

class DailyStatistics(BaseModel):
    date: str
    total_bookings: int
    cancellation_rate: float
    avg_party_size: float
    breakfast_count: int

# 전역 변수
model_predictor = None
hotel_data = None

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 연결 확인"""
    global hotel_data
    
    print("Loading hotel data...")
    hotel_data = load_hotel_data()
    
    print("Server startup complete! Ready to serve prediction results from MySQL.")

@app.get("/")
async def root():
    """API 헬스체크"""
    return {
        "status": "active",
        "message": "호텔 예약 예측 서비스 API",
        "version": "1.0.0"
    }

@app.get("/api/statistics/overview")
async def get_overview_statistics():
    """전체 데이터 통계 개요"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    total_bookings = len(hotel_data)
    cancellation_rate = hotel_data['is_canceled'].mean()
    avg_lead_time = hotel_data['lead_time'].mean()
    
    # 월별 취소율
    monthly_stats = []
    for month in hotel_data['arrival_date_month'].unique():
        month_data = hotel_data[hotel_data['arrival_date_month'] == month]
        monthly_stats.append({
            "month": month,
            "bookings": len(month_data),
            "cancellation_rate": month_data['is_canceled'].mean()
        })
    
    return {
        "total_bookings": total_bookings,
        "overall_cancellation_rate": float(cancellation_rate),
        "average_lead_time": float(avg_lead_time),
        "monthly_statistics": monthly_stats
    }

@app.post("/api/predict/date", response_model=PredictionResponse)
async def predict_by_date(request: PredictionRequest):
    """특정 날짜의 예약 취소 예측 및 조식 준비 인원 계산 (MySQL 예측 결과 기반)"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    try:
        # 날짜 파싱
        target_date = datetime.strptime(request.date, "%Y-%m-%d")
        year = target_date.year
        month = target_date.month
        day = target_date.day
        
        # MySQL에서 해당 날짜의 예약 데이터 조회 (예측 결과 포함)
        bookings = get_bookings_by_date_from_db(year, month, day, 0, 1000)  # 모든 예약 조회
        
        if len(bookings) == 0:
            return PredictionResponse(
                date=request.date,
                total_reservations=0,
                predicted_cancellations=0,
                expected_checkins=0,
                breakfast_recommendation=0,
                confidence_level=0.0,
                details={
                    "method": "mysql_results",
                    "message": "해당 날짜에 예약이 없습니다."
                }
            )
        
        # MySQL에 저장된 예측 결과 집계
        total_reservations = len(bookings)
        predicted_cancellations = sum(1 for b in bookings if b.get('predicted_is_canceled', 0) == 1)
        expected_checkins = total_reservations - predicted_cancellations
        
        # 조식 준비 인원 계산 (취소되지 않을 예약 중 조식 포함)
        breakfast_guests = sum(
            b.get('total_guests', 0) 
            for b in bookings 
            if b.get('predicted_is_canceled', 0) == 0 and b.get('meal', '') == '포함'
        )
        
        # 평균 신뢰도 계산
        avg_confidence = sum(b.get('predicted_probability', 0.5) for b in bookings) / len(bookings)
        
        return PredictionResponse(
            date=request.date,
            total_reservations=total_reservations,
            predicted_cancellations=predicted_cancellations,
            expected_checkins=expected_checkins,
            breakfast_recommendation=breakfast_guests,
            confidence_level=float(avg_confidence),
            details={
                "method": "mysql_results",
                "avg_cancellation_probability": float(avg_confidence),
                "total_guests": sum(b.get('total_guests', 0) for b in bookings)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 개별 예약 예측은 ML 폴더에서 이미 처리되어 MySQL에 저장됨

def calculate_daily_statistics(bookings: List[Dict]) -> Dict:
    """해당 날짜의 통계 정보 계산"""
    if not bookings:
        return {
            "search_date": "",
            "model_confidence": 0.0,
            "total_expected_guests": 0,
            "breakfast_preparation_count": 0
        }
    
    # 전체 통계 계산
    total_guests = sum(booking.get('total_guests', 0) for booking in bookings)
    
    # 평균 신뢰도 계산 (predicted_probability의 평균)
    probabilities = [booking.get('predicted_probability', 0.5) for booking in bookings]
    avg_confidence = sum(probabilities) / len(probabilities) if probabilities else 0.0
    
    # 조식 준비 인원수 계산 (조식 포함 예약의 성인+어린이 수)
    breakfast_count = 0
    for booking in bookings:
        if booking.get('meal') == '포함':
            # 성인 + 어린이 (아기는 조식 안 먹는다고 가정)
            adults = booking.get('total_guests', 0) - (booking.get('babies', 0) if 'babies' in booking else 0)
            breakfast_count += max(0, adults)  # 음수 방지
    
    return {
        "search_date": bookings[0].get('arrival_date', '') if bookings else '',
        "model_confidence": round(avg_confidence * 100, 1),  # 백분율로 변환
        "total_expected_guests": total_guests,
        "breakfast_preparation_count": breakfast_count
    }

@app.get("/api/calendar/monthly")
async def get_monthly_calendar(year: int, month: int):
    """월별 캘린더 데이터 (예약 현황 포함)"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    try:
        # 해당 월의 데이터 필터링
        month_name = datetime(year, month, 1).strftime("%B")
        month_data = hotel_data[
            (hotel_data['arrival_date_year'] == year) &
            (hotel_data['arrival_date_month'] == month_name)
        ]
        
        # 일별 통계 계산
        daily_stats = []
        for day in range(1, 32):
            try:
                date = datetime(year, month, day)
                day_data = month_data[month_data['arrival_date_day_of_month'] == day]
                
                if len(day_data) > 0:
                    daily_stats.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "day": day,
                        "bookings": len(day_data),
                        "cancellations": int(day_data['is_canceled'].sum()),
                        "cancellation_rate": float(day_data['is_canceled'].mean()),
                        "total_guests": int(day_data['adults'].sum() + day_data['children'].sum()),
                        "breakfast_count": len(day_data[day_data['meal'].isin(['BB', 'FB', 'HB'])])
                    })
                else:
                    daily_stats.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "day": day,
                        "bookings": 0,
                        "cancellations": 0,
                        "cancellation_rate": 0,
                        "total_guests": 0,
                        "breakfast_count": 0
                    })
            except ValueError:
                # 유효하지 않은 날짜 (예: 2월 30일)
                break
        
        return {
            "year": year,
            "month": month,
            "month_name": month_name,
            "daily_statistics": daily_stats,
            "summary": {
                "total_bookings": len(month_data),
                "total_cancellations": int(month_data['is_canceled'].sum()),
                "average_cancellation_rate": float(month_data['is_canceled'].mean()) if len(month_data) > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/trends/weekly")
async def get_weekly_trends():
    """주간 트렌드 분석"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # 요일별 취소율 분석
    hotel_data['arrival_date'] = pd.to_datetime(
        hotel_data['arrival_date_year'].astype(str) + '-' +
        hotel_data['arrival_date_month'] + '-' +
        hotel_data['arrival_date_day_of_month'].astype(str),
        errors='coerce'
    )
    
    hotel_data['weekday'] = hotel_data['arrival_date'].dt.day_name()
    
    weekday_stats = []
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        weekday_data = hotel_data[hotel_data['weekday'] == weekday]
        if len(weekday_data) > 0:
            weekday_stats.append({
                "day": weekday,
                "bookings": len(weekday_data),
                "cancellation_rate": float(weekday_data['is_canceled'].mean()),
                "avg_guests": float(weekday_data['adults'].mean() + weekday_data['children'].mean())
            })
    
    return {"weekly_trends": weekday_stats}

@app.get("/api/bookings/by-date")
async def get_bookings_by_date_api(
    year: int,
    month: int,
    day: int,
    offset: int = 0,
    limit: int = 10
):
    """특정 날짜의 예약 목록 조회 (고객 관리 페이지용)"""
    try:
        # MySQL에서 예약 데이터 조회
        bookings = get_bookings_by_date_from_db(year, month, day, offset, limit)
        
        # 전체 예약 수 조회
        total_count = get_bookings_count_by_date(year, month, day)
        
        # 통계 정보 계산
        statistics = calculate_daily_statistics(bookings)
        
        return {
            "success": True,
            "data": bookings,
            "total_count": total_count,
            "statistics": statistics,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings/search")
async def search_bookings(
    query: str = "",
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    offset: int = 0,
    limit: int = 10
):
    """예약 검색 API"""
    try:
        # 날짜가 지정된 경우 날짜별 조회
        if year and month and day:
            bookings = get_bookings_by_date_from_db(year, month, day, offset, limit)
            total_count = get_bookings_count_by_date(year, month, day)
        else:
            # 전체 검색 (추후 구현)
            bookings = []
            total_count = 0
        
        return {
            "success": True,
            "data": bookings,
            "total_count": total_count,
            "query": query,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings/count")
async def get_bookings_count(
    year: int,
    month: int,
    day: int
):
    """특정 날짜의 전체 예약 수 조회"""
    try:
        count = get_bookings_count_by_date(year, month, day)
        
        return {
            "success": True,
            "count": count,
            "date": f"{year}-{month:02d}-{day:02d}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
