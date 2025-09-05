"""
MySQL 데이터베이스에서 CSV 파일로 데이터 추출
1단계: DB → data 폴더의 CSV 파일
"""
import os
import pandas as pd
from service.database.connection import get_db_connection

def export_train_data() -> bool:
    """MySQL에서 train 데이터를 CSV로 저장"""
    db = get_db_connection()
    
    if not db.is_connected():
        if not db.connect():
            print("❌ 데이터베이스 연결에 실패했습니다.")
            return False
    
    try:
        print("📥 Train 데이터 로드 중...")
        query = "SELECT * FROM hotel_bookings_train"
        df = pd.read_sql(query, db.get_connection())
        
        # data 폴더 확인 및 생성
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # CSV 저장
        output_path = os.path.join(data_dir, "hotel_bookings_train.csv")
        df.to_csv(output_path, index=False)
        
        print(f"✅ Train 데이터 저장 완료: {output_path}")
        print(f"   - 행 수: {df.shape[0]}")
        print(f"   - 열 수: {df.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Train 데이터 추출 실패: {e}")
        return False

def export_test_data() -> bool:
    """MySQL에서 test 데이터를 CSV로 저장"""
    db = get_db_connection()
    
    if not db.is_connected():
        if not db.connect():
            print("❌ 데이터베이스 연결에 실패했습니다.")
            return False
    
    try:
        print("📥 Test 데이터 로드 중...")
        query = "SELECT * FROM hotel_bookings_test"
        df = pd.read_sql(query, db.get_connection())
        
        # data 폴더 확인 및 생성
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # CSV 저장
        output_path = os.path.join(data_dir, "hotel_bookings_test.csv")
        df.to_csv(output_path, index=False)
        
        print(f"✅ Test 데이터 저장 완료: {output_path}")
        print(f"   - 행 수: {df.shape[0]}")
        print(f"   - 열 수: {df.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test 데이터 추출 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=== MySQL → CSV 데이터 추출 ===")
    
    # Train 데이터 추출
    train_success = export_train_data()
    
    # Test 데이터 추출
    test_success = export_test_data()
    
    # 결과 요약
    print("\n=== 추출 결과 요약 ===")
    if train_success and test_success:
        print("🎉 모든 데이터 추출이 완료되었습니다!")
        print("💡 다음 단계: python main.py 실행")
    else:
        print("❌ 일부 데이터 추출에 실패했습니다.")
        if not train_success:
            print("   - Train 데이터 추출 실패")
        if not test_success:
            print("   - Test 데이터 추출 실패")

if __name__ == "__main__":
    main()
