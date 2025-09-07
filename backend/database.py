"""
데이터베이스 및 데이터 로드 관련 함수들
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
import sys
import mysql.connector
from typing import Optional, List, Dict

# ML 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ML'))
from service.database.connection import get_db_connection

def get_mysql_connection():
    """MySQL 연결 객체 반환"""
    db = get_db_connection()
    if not db.is_connected():
        if not db.connect():
            raise Exception("Failed to connect to MySQL database")
    return db.get_connection()

def load_hotel_data():
    """호텔 예약 데이터 로드 - MySQL에서 직접 조회"""
    try:
        conn = get_mysql_connection()
        
        # 먼저 사용 가능한 테이블 확인
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Available tables: {tables}")
        
        # 날짜 범위 확인
        cursor.execute("SELECT MIN(arrival_date_year), MAX(arrival_date_year), COUNT(*) FROM hotel_booking_predictions")
        date_info = cursor.fetchone()
        print(f"Date range: {date_info[0]} - {date_info[1]}, Total records: {date_info[2]}")
        
        # 2017년 7월 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM hotel_booking_predictions WHERE arrival_date_year = 2017 AND arrival_date_month = 'July'")
        july_2017_count = cursor.fetchone()
        print(f"July 2017 records: {july_2017_count[0]}")
        
        cursor.close()
        
        # hotel_booking_predictions 테이블만 먼저 조회
        query = """
        SELECT * FROM hotel_booking_predictions
        LIMIT 10000
        """
        df = pd.read_sql(query, conn)
        
        # 기본 데이터 정리
        df['children'] = df['children'].fillna(0) if 'children' in df.columns else 0
        df['country'] = df['country'].fillna('Unknown') if 'country' in df.columns else 'Unknown'
        df['agent'] = df['agent'].fillna(0) if 'agent' in df.columns else 0
        df['company'] = df['company'].fillna(0) if 'company' in df.columns else 0
        
        print(f"Loaded {len(df)} booking records from MySQL")
        print(f"Available columns: {list(df.columns)}")
        return df
        
    except Exception as e:
        print(f"Error loading data from MySQL: {e}")
        raise

def get_bookings_by_date_from_db(year: int, month: int, day: int, offset: int = 0, limit: int = 10) -> List[Dict]:
    """MySQL에서 특정 날짜의 예약 데이터 조회"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 월 이름으로 변환 (1 -> January, 2 -> February, ...)
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month] if 1 <= month <= 12 else 'January'
        
        # 실제 테이블 구조에 맞게 쿼리 수정
        query = """
        SELECT 
            reservation_id,
            hotel,
            CONCAT(arrival_date_year, '-', 
                   LPAD(MONTH(STR_TO_DATE(arrival_date_month, '%%M')), 2, '0'), '-',
                   LPAD(arrival_date_day_of_month, 2, '0')) as arrival_date,
            (adults + children + babies) as total_guests,
            (stays_in_weekend_nights + stays_in_week_nights) as total_nights,
            COALESCE(reserved_room_type, '-') as room_type,
            COALESCE(meal, '-') as meal_type,
            CASE 
                WHEN total_of_special_requests = 0 OR total_of_special_requests IS NULL THEN '-' 
                ELSE CAST(total_of_special_requests AS CHAR) 
            END as special_requests,
            predicted_is_canceled,
            predicted_probability
        FROM hotel_booking_predictions
        WHERE arrival_date_year = %s 
            AND arrival_date_month = %s 
            AND arrival_date_day_of_month = %s
        ORDER BY reservation_id DESC
        LIMIT %s OFFSET %s
        """
        
        print(f"Executing query with params: year={year}, month={month_name}, day={day}, limit={limit}, offset={offset}")
        cursor.execute(query, (year, month_name, day, limit, offset))
        results = cursor.fetchall()
        print(f"Query returned {len(results)} results")
        
        # 데이터 포맷팅
        formatted_results = []
        for row in results:
            formatted_results.append({
                'reservation_id': row['reservation_id'],
                'name': '-',  # 없는 데이터
                'phone': '-',  # 없는 데이터
                'hotel': row['hotel'],
                'arrival_date': row['arrival_date'],
                'total_guests': row['total_guests'],
                'total_nights': row['total_nights'],
                'room_type': row['room_type'],
                'meal': format_meal_type(row['meal_type']),
                'special_requests': row['special_requests'],
                'predicted_is_canceled': row['predicted_is_canceled'],
                'predicted_probability': row['predicted_probability']
            })
        
        cursor.close()
        return formatted_results
        
    except Exception as e:
        print(f"Error fetching bookings by date: {e}")
        return []

def format_meal_type(meal: str) -> str:
    """식사 타입 포맷팅"""
    if meal in ['BB', 'FB', 'HB']:
        return '포함'
    elif meal == '-' or meal is None:
        return '-'
    else:
        return '미포함'

def get_bookings_count_by_date(year: int, month: int, day: int) -> int:
    """특정 날짜의 전체 예약 수 조회"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month] if 1 <= month <= 12 else 'January'
        
        query = """
        SELECT COUNT(*) as total
        FROM hotel_booking_predictions
        WHERE arrival_date_year = %s 
            AND arrival_date_month = %s 
            AND arrival_date_day_of_month = %s
        """
        
        cursor.execute(query, (year, month_name, day))
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else 0
        
    except Exception as e:
        print(f"Error counting bookings: {e}")
        return 0
>>>>>>> origin/inha-2

def get_bookings_by_date(df: pd.DataFrame, target_date: datetime, hotel_type: str = None):
    """특정 날짜의 예약 데이터 조회 (기존 함수 - 호환성 유지)"""
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
        'cancellations': int(month_data['predicted_is_canceled'].sum()),
        'cancellation_rate': float(month_data['predicted_probability'].mean()),
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
        active_breakfast_df = breakfast_df[breakfast_df['predicted_is_canceled'] == 0]
        active_guests = (
            active_breakfast_df['adults'].sum() + 
            active_breakfast_df['children'].sum()
        )
        return int(active_guests)
    
    return int(total_breakfast_guests)
