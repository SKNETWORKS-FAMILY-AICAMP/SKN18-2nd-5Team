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

@app.get("/api/dates/available")
async def get_available_dates():
    """사용 가능한 날짜 범위 반환"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    try:
        # 데이터에서 사용 가능한 날짜들 추출
        available_dates = sorted(hotel_data['arrival_date_full'].unique().tolist())
        min_date = available_dates[0]
        max_date = available_dates[-1]
        
        return {
            "min_date": min_date,
            "max_date": max_date,
            "available_dates": available_dates,
            "total_dates": len(available_dates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    cancellation_rate = hotel_data['predicted_is_canceled'].mean()
    avg_lead_time = hotel_data['lead_time'].mean()
    
    # 월별 취소율
    monthly_stats = []
    for month in hotel_data['arrival_date_month'].unique():
        month_data = hotel_data[hotel_data['arrival_date_month'] == month]
        monthly_stats.append({
            "month": month,
            "bookings": len(month_data),
            "cancellation_rate": month_data['predicted_is_canceled'].mean()
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
        # 날짜로 해당 날짜의 모든 예약 데이터 조회
        date_bookings = hotel_data[hotel_data['arrival_date_full'] == request.date].copy()
        
        # 호텔 타입 필터링
        if request.hotel_type:
            date_bookings = date_bookings[date_bookings['hotel'] == request.hotel_type]
        
        if len(date_bookings) == 0:
            # 예약 데이터가 없는 경우
            return PredictionResponse(
                date=request.date,
                total_reservations=0,
                predicted_cancellations=0,
                expected_checkins=0,
                breakfast_recommendation=0,
                confidence_level=0.0,
                details={
                    "method": "no_data",
                    "message": "해당 날짜의 예약 데이터가 없습니다.",
                    "adults": 0,
                    "children": 0,
                    "babies": 0,
                    "total_guests": 0,
                    "breakfast_bookings": 0,
                    "avg_cancellation_probability": 0.0,
                    "expected_breakfast_guests": 0
                }
            )
        
        # 총 예약 건수
        total_reservations = len(date_bookings)
        
        # 성인, 아동, 유아 수 계산
        total_adults = int(date_bookings['adults'].sum())
        total_children = int(date_bookings['children'].sum()) 
        total_babies = int(date_bookings['babies'].sum())
        
        # 총 고객 수 (성인 + 아동만, 유아 제외)
        total_guests = total_adults + total_children
        
        # 조식 신청자 수 (BB, HB, FB 포함)
        breakfast_meals = ['BB', 'HB', 'FB']
        breakfast_bookings = date_bookings[date_bookings['meal'].isin(breakfast_meals)]
        breakfast_reservations = len(breakfast_bookings)
        breakfast_adults = int(breakfast_bookings['adults'].sum())
        breakfast_children = int(breakfast_bookings['children'].sum())
        breakfast_guests = breakfast_adults + breakfast_children
        
        # 취소 확률 계산 (predicted_probability 컬럼 사용)
        avg_cancellation_probability = float(date_bookings['predicted_probability'].mean())
        
        # 예상 취소 수 (확률 기반)
        predicted_cancellations = int(total_reservations * avg_cancellation_probability)
        
        # 예상 체크인 수
        expected_checkins = total_reservations - predicted_cancellations
        
        # 취소 확률을 반영한 실제 예상 손님 수
        # 전체 고객 수에 취소확률 적용: (해당일 예약 고객 수) * (1 - 취소확률)
        expected_total_guests = int((total_adults + total_children) * (1 - avg_cancellation_probability))
        
        # 성인/아동 비율 유지하여 계산
        total_guest_ratio = total_adults + total_children
        if total_guest_ratio > 0:
            adult_ratio = total_adults / total_guest_ratio
            child_ratio = total_children / total_guest_ratio
            expected_adults = int(expected_total_guests * adult_ratio)
            expected_children = int(expected_total_guests * child_ratio)
        else:
            expected_adults = 0
            expected_children = 0
        
        # 조식 준비 인원 계산 (취소 확률 반영)
        # 조식 신청 고객 수에 취소확률 적용
        expected_breakfast_guests = int(breakfast_guests * (1 - avg_cancellation_probability))
        
        # 조식 성인/아동 비율 유지하여 계산
        if breakfast_guests > 0:
            breakfast_adult_ratio = breakfast_adults / breakfast_guests
            breakfast_child_ratio = breakfast_children / breakfast_guests
            expected_breakfast_adults = int(expected_breakfast_guests * breakfast_adult_ratio)
            expected_breakfast_children = int(expected_breakfast_guests * breakfast_child_ratio)
        else:
            expected_breakfast_adults = 0
            expected_breakfast_children = 0
        
        return PredictionResponse(
            date=request.date,
            total_reservations=total_guests,  # 총 고객 수로 변경
            predicted_cancellations=int(total_guests * avg_cancellation_probability),  # 고객 수 기준으로 계산
            expected_checkins=expected_total_guests,  # 예상 체크인 고객 수
            breakfast_recommendation=expected_breakfast_guests,
            confidence_level=float(1 - avg_cancellation_probability),
            details={
                "total_bookings": total_reservations,  # 예약 건수
                "method": "ml_prediction",
                "message": "머신러닝 모델을 사용한 예측 결과입니다.",
                "adults": total_adults,
                "children": total_children,
                "babies": total_babies,
                "total_guests": total_guests,
                "breakfast_bookings": breakfast_reservations,
                "breakfast_guests": breakfast_guests,
                "breakfast_adults": breakfast_adults,
                "breakfast_children": breakfast_children,
                "avg_cancellation_probability": avg_cancellation_probability,
                "expected_adults": expected_adults,
                "expected_children": expected_children,
                "expected_total_guests": expected_total_guests,
                "expected_breakfast_guests": expected_breakfast_guests,
                "expected_breakfast_adults": expected_breakfast_adults,
                "expected_breakfast_children": expected_breakfast_children
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
                        "cancellations": int(day_data['predicted_is_canceled'].sum()),
                        "cancellation_rate": float(day_data['predicted_is_canceled'].mean()),
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
                "total_cancellations": int(month_data['predicted_is_canceled'].sum()),
                "average_cancellation_rate": float(month_data['predicted_is_canceled'].mean()) if len(month_data) > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/bookings/by-date")
async def get_bookings_by_date_api(year: int, month: int, day: int, offset: int = 0, limit: int = 10):
    """특정 날짜의 예약 목록 조회"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    try:
        # 월 이름 변환
        month_name = datetime(year, month, 1).strftime("%B")
        
        # 해당 날짜의 데이터 필터링
        date_bookings = hotel_data[
            (hotel_data['arrival_date_year'] == year) &
            (hotel_data['arrival_date_month'] == month_name) &
            (hotel_data['arrival_date_day_of_month'] == day)
        ].copy()
        
        total_count = len(date_bookings)
        
        if total_count == 0:
            return {
                "success": True,
                "data": [],
                "total_count": 0,
                "statistics": {
                    "model_confidence": 0,
                    "total_expected_guests": 0,
                    "breakfast_preparation_count": 0
                }
            }
        
        # 페이지네이션 적용
        paginated_bookings = date_bookings.iloc[offset:offset + limit]
        
        # 예약 데이터 변환
        booking_list = []
        for idx, booking in paginated_bookings.iterrows():
            # 더미 개인정보 생성 - 영국 기준 (실제 서비스에서는 실제 데이터 사용)
            dummy_names = [
                "James Smith", "Emily Johnson", "Michael Brown", "Sarah Wilson", 
                "David Jones", "Emma Davis", "Robert Miller", "Olivia Garcia",
                "William Rodriguez", "Sophia Martinez", "Thomas Anderson", "Isabella Taylor",
                "Charles Thomas", "Mia Jackson", "Christopher White", "Charlotte Harris"
            ]
            dummy_phones = [
                "+44 20 7946 0958", "+44 161 496 0345", "+44 113 496 0123", "+44 117 496 0789",
                "+44 121 496 0234", "+44 131 496 0567", "+44 151 496 0890", "+44 191 496 0345",
                "+44 29 2018 0123", "+44 28 9018 0456", "+44 1234 567890", "+44 1632 960123",
                "+44 114 496 0234", "+44 115 496 0567", "+44 116 496 0890", "+44 118 496 0123"
            ]
            
            booking_data = {
                "reservation_id": f"RES{idx:06d}",
                "name": dummy_names[idx % len(dummy_names)],
                "phone": dummy_phones[idx % len(dummy_phones)],
                "total_guests": int(booking['adults'] + booking['children'] + booking['babies']),
                "arrival_date": f"{year}-{month:02d}-{day:02d}",
                "total_nights": int(booking['stays_in_weekend_nights'] + booking['stays_in_week_nights']),
                "room_type": booking['reserved_room_type'],
                "meal": "포함" if booking['meal'] in ['BB', 'HB', 'FB'] else "불포함",
                "special_requests": f"특별 요청 {booking['total_of_special_requests']}건" if booking['total_of_special_requests'] > 0 else "없음",
                "predicted_probability": float(booking['predicted_probability']) if 'predicted_probability' in booking else float(booking.get('predicted_is_canceled', 0))
            }
            booking_list.append(booking_data)
        
        # 통계 계산
        avg_cancellation_prob = float(date_bookings['predicted_probability'].mean()) if 'predicted_probability' in date_bookings.columns else float(date_bookings['predicted_is_canceled'].mean())
        total_guests = int(date_bookings['adults'].sum() + date_bookings['children'].sum())
        expected_guests = int(total_guests * (1 - avg_cancellation_prob))
        
        # 조식 준비 인원
        breakfast_bookings = date_bookings[date_bookings['meal'].isin(['BB', 'HB', 'FB'])]
        breakfast_guests = int(breakfast_bookings['adults'].sum() + breakfast_bookings['children'].sum())
        expected_breakfast_guests = int(breakfast_guests * (1 - avg_cancellation_prob))
        
        statistics = {
            "model_confidence": round((1 - avg_cancellation_prob) * 100, 1),
            "total_expected_guests": expected_guests,
            "breakfast_preparation_count": expected_breakfast_guests
        }
        
        return {
            "success": True,
            "data": booking_list,
            "total_count": total_count,
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/trends/weekly")
async def get_weekly_trends():
    """주간 트렌드 분석"""
    if hotel_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # 요일별 취소율 분석
    hotel_data_copy = hotel_data.copy()
    hotel_data_copy['arrival_date'] = pd.to_datetime(
        hotel_data_copy['arrival_date_year'].astype(str) + '-' +
        hotel_data_copy['arrival_date_month'] + '-' +
        hotel_data_copy['arrival_date_day_of_month'].astype(str),
        errors='coerce'
    )
    
    hotel_data_copy['weekday'] = hotel_data_copy['arrival_date'].dt.day_name()
    
    weekday_stats = []
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        weekday_data = hotel_data_copy[hotel_data_copy['weekday'] == weekday]
        if len(weekday_data) > 0:
            weekday_stats.append({
                "day": weekday,
                "bookings": len(weekday_data),
                "cancellation_rate": float(weekday_data['predicted_is_canceled'].mean()),
                "avg_guests": float(weekday_data['adults'].mean() + weekday_data['children'].mean())
            })
    
    return {"weekly_trends": weekday_stats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
