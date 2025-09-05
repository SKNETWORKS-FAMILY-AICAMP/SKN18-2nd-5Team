"""
데이터베이스 및 데이터 로드 관련 함수들
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

def load_hotel_data():
    """호텔 예약 데이터 로드"""
    # 현재 파일 기준으로 상대경로 설정
    current_dir = Path(__file__).parent
    
    # 여러 경로 시도
    possible_paths = [
        current_dir / "../ML/data/hotel_bookings.csv",
        current_dir / "../../ML/data/hotel_bookings.csv", 
        Path("../ML/data/hotel_bookings.csv"),
        Path("ML/data/hotel_bookings.csv"),
        Path("./ML/data/hotel_bookings.csv")
    ]
    
    data_path = None
    for path in possible_paths:
        if path.exists():
            data_path = path
            break
            
    if data_path is None:
        raise FileNotFoundError(f"Data file not found in any of these paths: {[str(p) for p in possible_paths]}")
    
    # CSV 로드
    df = pd.read_csv(data_path)
    
    # 기본 데이터 정리
    df['children'] = df['children'].fillna(0)
    df['country'] = df['country'].fillna('Unknown')
    df['agent'] = df['agent'].fillna(0)
    df['company'] = df['company'].fillna(0)
    
    print(f"Loaded {len(df)} booking records")
    
    return df

def get_bookings_by_date(df: pd.DataFrame, target_date: datetime, hotel_type: str = None):
    """특정 날짜의 예약 데이터 조회"""
    # 날짜 정보 추출
    year = target_date.year
    month = target_date.strftime("%B")  # 월 이름 (예: "July")
    day = target_date.day
    
    # 필터링
    filtered_df = df[
        (df['arrival_date_year'] == year) &
        (df['arrival_date_month'] == month) &
        (df['arrival_date_day_of_month'] == day)
    ]
    
    # 호텔 타입 필터링
    if hotel_type:
        filtered_df = filtered_df[filtered_df['hotel'] == hotel_type]
    
    return filtered_df

def get_monthly_statistics(df: pd.DataFrame, year: int, month: int):
    """월별 통계 계산"""
    month_name = datetime(year, month, 1).strftime("%B")
    
    month_data = df[
        (df['arrival_date_year'] == year) &
        (df['arrival_date_month'] == month_name)
    ]
    
    if len(month_data) == 0:
        return None
    
    stats = {
        'total_bookings': len(month_data),
        'cancellations': int(month_data['is_canceled'].sum()),
        'cancellation_rate': float(month_data['is_canceled'].mean()),
        'avg_lead_time': float(month_data['lead_time'].mean()),
        'avg_stay_length': float(
            month_data['stays_in_weekend_nights'].mean() + 
            month_data['stays_in_week_nights'].mean()
        ),
        'total_guests': int(
            month_data['adults'].sum() + 
            month_data['children'].sum() + 
            month_data['babies'].sum()
        ),
        'breakfast_bookings': len(month_data[month_data['meal'].isin(['BB', 'FB', 'HB'])]),
        'room_types': month_data['reserved_room_type'].value_counts().to_dict()
    }
    
    return stats

def calculate_breakfast_estimate(df: pd.DataFrame, include_probability: bool = True):
    """조식 인원 예측"""
    # 조식이 포함된 예약만 필터링
    breakfast_df = df[df['meal'].isin(['BB', 'FB', 'HB'])]
    
    if len(breakfast_df) == 0:
        return 0
    
    # 총 인원 계산 (성인 + 어린이)
    total_breakfast_guests = (
        breakfast_df['adults'].sum() + 
        breakfast_df['children'].sum()
    )
    
    if include_probability:
        # 취소되지 않을 예약만 고려 (과거 데이터 기준)
        active_breakfast_df = breakfast_df[breakfast_df['is_canceled'] == 0]
        active_guests = (
            active_breakfast_df['adults'].sum() + 
            active_breakfast_df['children'].sum()
        )
        return int(active_guests)
    
    return int(total_breakfast_guests)
