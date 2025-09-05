"""
CSV 예측 결과를 MySQL 데이터베이스로 저장
3단계: data/results/hotel_booking_predictions.csv → DB
"""
import os
import pandas as pd
from service.database.connection import get_db_connection
import mysql.connector

def import_predictions_to_db() -> bool:
    """예측 결과 CSV를 MySQL로 저장"""
    
    # 1. CSV 파일 존재 확인
    csv_path = os.path.join("data", "results", "hotel_booking_predictions.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ 예측 결과 파일이 없습니다: {csv_path}")
        print("💡 먼저 main.py를 실행하여 예측 결과를 생성하세요.")
        return False
    
    # 2. CSV 파일 로드
    try:
        print(f"📥 예측 결과 CSV 로드 중: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"   - 행 수: {df.shape[0]}")
        print(f"   - 열 수: {df.shape[1]}")
        
    except Exception as e:
        print(f"❌ CSV 파일 로드 실패: {e}")
        return False
    
    # 3. 데이터베이스 연결
    db = get_db_connection()
    
    if not db.is_connected():
        if not db.connect():
            print("❌ 데이터베이스 연결에 실패했습니다.")
            return False
    
    # 4. 데이터베이스에 저장
    try:
        print("💾 MySQL에 예측 결과 저장 중...")
        
        connection = db.get_connection()
        cursor = connection.cursor()
        
        # 기존 테이블 삭제 (있다면)
        table_name = "hotel_booking_predictions"
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # 테이블 생성 쿼리 동적 생성
        columns_def = []
        for col in df.columns:
            if df[col].dtype == 'object':  # 문자열
                columns_def.append(f"`{col}` TEXT")
            elif df[col].dtype in ['int64', 'int32']:  # 정수
                columns_def.append(f"`{col}` INT")
            elif df[col].dtype in ['float64', 'float32']:  # 실수
                columns_def.append(f"`{col}` DOUBLE")
            else:  # 기타
                columns_def.append(f"`{col}` TEXT")
        
        create_table_query = f"""
        CREATE TABLE {table_name} (
            {', '.join(columns_def)}
        )
        """
        
        cursor.execute(create_table_query)
        print(f"✅ 테이블 '{table_name}' 생성 완료")
        
        # 데이터 삽입
        # DataFrame을 리스트로 변환
        data_tuples = [tuple(row) for row in df.values]
        
        # INSERT 쿼리 생성
        placeholders = ', '.join(['%s'] * len(df.columns))
        columns_names = ', '.join([f"`{col}`" for col in df.columns])
        insert_query = f"INSERT INTO {table_name} ({columns_names}) VALUES ({placeholders})"
        
        # 배치로 데이터 삽입
        cursor.executemany(insert_query, data_tuples)
        connection.commit()
        
        print(f"✅ {len(data_tuples)}개 예측 결과가 '{table_name}' 테이블에 저장되었습니다!")
        
        cursor.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ 데이터베이스 저장 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def verify_saved_data() -> bool:
    """저장된 데이터 검증"""
    db = get_db_connection()
    
    if not db.is_connected():
        if not db.connect():
            return False
    
    try:
        cursor = db.get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM hotel_booking_predictions")
        count = cursor.fetchone()[0]
        
        print(f"🔍 저장 검증: {count}개 레코드 확인됨")
        
        # 샘플 데이터 확인
        cursor.execute("SELECT * FROM hotel_booking_predictions LIMIT 3")
        sample_rows = cursor.fetchall()
        
        print("📋 샘플 데이터:")
        for i, row in enumerate(sample_rows, 1):
            print(f"   {i}. 예측값: {row[-2]}, 확률: {row[-1]:.3f}")  # 마지막 2개 컬럼
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터 검증 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=== CSV → MySQL 예측 결과 저장 ===")
    
    # 예측 결과 저장
    success = import_predictions_to_db()
    
    if success:
        # 저장된 데이터 검증
        verify_saved_data()
        
        print("\n🎉 예측 결과가 성공적으로 MySQL에 저장되었습니다!")
        print("💡 DBeaver에서 'hotel_booking_predictions' 테이블을 확인하세요.")
    else:
        print("\n❌ 예측 결과 저장에 실패했습니다.")

if __name__ == "__main__":
    main()
