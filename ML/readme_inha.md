# Hotel Booking ML with Database

## 📦 필요한 패키지

```bash
<<<<<<< HEAD
cd ML
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
=======
# 0단계: 가상환경 설정
uv venv .venv --python 3.13
.\venv\Scripts\activate
uv pip install --upgrade pip
uv pip install  -r .\requirements.txt

# 1단계: DB → CSV
python db_to_csv.py
>>>>>>> origin/inha-2

pip install mysql-connector-python
```
## 🔧 DB 연결 설정

**파일**: `service/database/connection.py`  
**수정 위치**: 13번째 줄

```python
def __init__(self, host: str = "localhost", port: int = 3306, 
             database: str = "hotalbookings", user: str = "root", password: str = "root1234"):
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

## 🚀 실행 방법 (3단계)

```bash
# 1단계: DB → CSV
python db_to_csv.py

<<<<<<< HEAD
# 2단계: ML 실행
python main.py

# 3단계: 결과 → DB
python csv_to_db.py
=======
>>>>>>> origin/inha-2
```

