# Hotel Booking ML with Database

## 🚀 실행 방법 (3단계)

```bash
# 1단계: DB → CSV
python db_to_csv.py

# 2단계: ML 실행
python main.py

# 3단계: 결과 → DB (최신 파일 자동 인식)
python csv_to_db.py
```

**💡 참고**: 
- 2단계에서 `hotel_booking_predictions_MMDDHHMMSS.csv` 형식으로 저장됨
- 3단계에서 가장 최신 파일을 자동으로 찾아서 DB에 저장


## 🔧 DB 연결 설정

**파일**: `service/database/connection.py`  
**수정 위치**: 13번째 줄

```python
def __init__(self, host: str = "localhost", port: int = 3306, 
             database: str = "examplesdb", user: str = "root", password: str = "root1234"):
```

**변경할 값들**:
- `host`: DB 서버 주소
- `port`: DB 포트 (보통 3306)
- `database`: 데이터베이스 이름
- `user`: DB 사용자명
- `password`: DB 비밀번호

## 📋 필요한 DB 테이블

DBeaver에서 미리 로드해야 할 테이블:
- `hotel_bookings_train` (학습 데이터)
- `hotel_bookings_test` (예측 대상 데이터)

**결과 테이블** (자동 생성):
- `hotel_booking_predictions` (예측 결과 저장)



## 📦 필요한 패키지

```bash
pip install mysql-connector-python
```
