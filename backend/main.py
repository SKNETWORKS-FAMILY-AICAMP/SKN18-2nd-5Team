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
from database import load_hotel_data, get_bookings_by_date

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
    """서버 시작 시 모델 및 데이터 로드"""
    global model_predictor, hotel_data
    
    print("Loading hotel data...")
    hotel_data = load_hotel_data()
    
    print("Initializing ML model...")
    model_predictor = CancellationPredictor()
    
    # 모델이 이미 학습되어 있는지 확인
    model_path = Path("models/cancellation_model.pkl")
    if model_path.exists():
        print("Loading pre-trained model...")
        model_predictor.load_model(str(model_path))
    else:
        print("Training new model...")
        model_predictor.train(hotel_data)
        model_path.parent.mkdir(exist_ok=True)
        model_predictor.save_model(str(model_path))
    
    print("Server startup complete!")

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
    """특정 날짜의 예약 취소 예측 및 조식 준비 인원 계산"""
    if model_predictor is None or hotel_data is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    try:
        # 날짜 파싱
        target_date = datetime.strptime(request.date, "%Y-%m-%d")
        
        # 해당 날짜의 예약 데이터 조회
        bookings = get_bookings_by_date(hotel_data, target_date, request.hotel_type)
        
        if len(bookings) == 0:
            # 예약 데이터가 없는 경우 과거 평균값으로 예측
            avg_bookings = 50  # 기본값
            avg_cancellation_rate = 0.37  # 전체 평균 취소율
            predicted_cancellations = int(avg_bookings * avg_cancellation_rate)
            expected_checkins = avg_bookings - predicted_cancellations
            
            return PredictionResponse(
                date=request.date,
                total_reservations=avg_bookings,
                predicted_cancellations=predicted_cancellations,
                expected_checkins=expected_checkins,
                breakfast_recommendation=int(expected_checkins * 0.7),  # 70%가 조식 이용 가정
                confidence_level=0.5,
                details={
                    "method": "historical_average",
                    "message": "해당 날짜의 예약 데이터가 없어 과거 평균값을 사용했습니다."
                }
            )
        
        # 각 예약에 대한 취소 확률 예측
        cancellation_probs = model_predictor.predict_batch(bookings)
        
        # 총 예약 수
        total_reservations = len(bookings)
        
        # 예상 취소 수 (확률 기반)
        predicted_cancellations = int(np.sum(cancellation_probs))
        
        # 예상 체크인 수
        expected_checkins = total_reservations - predicted_cancellations
        
        # 조식 준비 인원 계산
        # 체크인 예상 인원 중 조식 포함 예약 고려
        breakfast_bookings = bookings[bookings['meal'].isin(['BB', 'FB', 'HB'])]
        breakfast_guests = 0
        
        for idx, booking in breakfast_bookings.iterrows():
            if cancellation_probs[bookings.index.get_loc(idx)] < 0.5:  # 취소 확률이 50% 미만인 경우
                breakfast_guests += booking['adults'] + booking['children']
        
        # 신뢰도 계산 (예측 확률의 평균 확신도)
        confidence_level = float(np.mean([max(p, 1-p) for p in cancellation_probs]))
        
        return PredictionResponse(
            date=request.date,
            total_reservations=total_reservations,
            predicted_cancellations=predicted_cancellations,
            expected_checkins=expected_checkins,
            breakfast_recommendation=breakfast_guests,
            confidence_level=confidence_level,
            details={
                "hotel_type": request.hotel_type,
                "avg_cancellation_probability": float(np.mean(cancellation_probs)),
                "breakfast_bookings": len(breakfast_bookings),
                "total_guests": int(bookings['adults'].sum() + bookings['children'].sum())
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/predict/booking")
async def predict_single_booking(features: BookingFeatures):
    """개별 예약의 취소 확률 예측"""
    if model_predictor is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    try:
        # 예측
        cancellation_prob = model_predictor.predict_single(features.dict())
        
        return {
            "cancellation_probability": float(cancellation_prob),
            "risk_level": "높음" if cancellation_prob > 0.7 else "중간" if cancellation_prob > 0.3 else "낮음",
            "recommendation": "취소 가능성이 높으니 오버부킹을 고려하세요." if cancellation_prob > 0.7 else "정상적인 예약입니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
