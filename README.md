# 🏨 HotelPredict AI - 호텔 예약 관리 시스템

## 📋 프로젝트 소개

HotelPredict AI는 머신러닝을 활용한 지능형 호텔 예약 관리 시스템입니다. 예약 취소율을 예측하고 조식 준비 인원을 최적화하여 호텔 운영의 효율성을 극대화합니다.

### ✨ 주요 기능

- **📊 예약 취소 예측**: 머신러닝 모델을 통한 정확한 취소율 예측
- **☕ 조식 인원 예측**: 일별 조식 준비 인원 최적화
- **📅 달력 기반 인터페이스**: 직관적인 날짜 선택 및 예측
- **📈 실시간 통계**: 예약 데이터의 실시간 분석 및 시각화

## 🚀 시작하기

### 필수 요구사항

- Python 3.8 이상
- Node.js 16 이상
- npm 또는 yarn

### 설치 방법

#### 1. 저장소 클론
```bash
git clone https://github.com/SKN18-2nd-5Team/hotel-prediction.git
cd SKN18-2nd-5Team
```

#### 2. 백엔드 설치 및 실행

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화 (선택사항)
python -m venv venv
# Windows
venv\Scripts\activate

# 의존성 패키지 설치
python -m pip install --upgrade pip

# Windows 사용자 (권장)
pip install --only-binary=all fastapi uvicorn[standard] pandas numpy scikit-learn joblib pydantic python-multipart python-dotenv

# 또는 requirements.txt 사용 (문제 발생 시)
# pip install -r requirements.txt

# FastAPI 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

백엔드 서버가 http://localhost:8000 에서 실행됩니다.

#### 3. 프론트엔드 설치 및 실행

새 터미널 창에서:

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 패키지 설치 (호환성 문제 해결)
npm install --legacy-peer-deps

# React 개발 서버 실행
npm run dev
```

프론트엔드가 http://localhost:5173 에서 실행됩니다.

## 💡 사용 방법

### 1. 메인 페이지
- 시스템 개요 및 전체 통계 확인
- 주요 기능 바로가기

### 2. 취소 예측 페이지
1. 달력에서 예측하고자 하는 날짜 클릭
2. 호텔 타입 선택 (리조트/시티)
3. 실시간으로 예측 결과 확인:
   - 총 예약 수
   - 예상 취소 수
   - 예상 체크인 수
   - 조식 준비 권장 인원

### 3. 조식 예측 페이지
1. 달력에서 날짜 선택
2. 예상 조식 인원 확인
3. 보기 모드 변경:
   - **일별 예측**: 선택한 날짜의 상세 조식 정보
   - **주간 트렌드**: 주간 조식 인원 추이
   - **월간 통계**: 월별 종합 통계

### 📊 예측 정확도

- 머신러닝 모델: Gradient Boosting Classifier
- 예측 정확도: 약 85%
- 주요 예측 요인:
  - 리드타임 (예약일과 체크인일 사이 기간)
  - 예약 변경 횟수
  - 특별 요청 사항
  - 고객 유형
  - 예약 경로

## 🛠 기술 스택

### Backend
- **FastAPI**: 고성능 웹 API 프레임워크
- **Python 3.8+**: 백엔드 개발 언어
- **Scikit-learn**: 머신러닝 모델
- **Pandas/NumPy**: 데이터 처리

### Frontend
- **React 19**: UI 라이브러리
- **Vite**: 빌드 도구
- **React Router**: 라우팅
- **Chart.js**: 데이터 시각화
- **Framer Motion**: 애니메이션
- **Axios**: HTTP 클라이언트

## 📁 프로젝트 구조

```
hotel-prediction/
├── backend/
│   ├── main.py           # FastAPI 메인 서버
│   ├── ml_model.py        # 머신러닝 모델
│   ├── database.py        # 데이터 처리
│   ├── models/            # 학습된 모델 저장
│   └── requirements.txt   # Python 패키지
│
├── frontend/
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── pages/        # 페이지 컴포넌트
│   │   ├── App.jsx       # 메인 앱
│   │   └── main.jsx      # 엔트리 포인트
│   ├── package.json      # Node 패키지
│   └── vite.config.js    # Vite 설정
│
└── ML/
    └── data/
        └── hotel_bookings.csv  # 학습 데이터

```

## 🔧 환경 설정

### 백엔드 환경 변수
백엔드 루트에 `.env` 파일 생성:
```env
# API 설정
HOST=0.0.0.0
PORT=8000

# 데이터베이스 경로
DATA_PATH=../ML/data/hotel_bookings.csv
```

### 프론트엔드 환경 변수
프론트엔드 루트에 `.env` 파일 생성:
```env
VITE_API_URL=http://localhost:8000
```

## 📈 API 문서

FastAPI 서버 실행 후 다음 주소에서 API 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 주요 API 엔드포인트

- `GET /`: 헬스체크
- `GET /api/statistics/overview`: 전체 통계
- `POST /api/predict/date`: 날짜별 예측
- `POST /api/predict/booking`: 개별 예약 예측
- `GET /api/calendar/monthly`: 월별 캘린더 데이터
- `GET /api/trends/weekly`: 주간 트렌드

## 🤝 기여하기

프로젝트 개선을 위한 제안이나 버그 리포트를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👥 팀 정보

**SKN18-2nd-5Team**
- 호텔 예약 데이터 분석 및 예측 서비스 개발팀

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 Issue를 통해 연락 부탁드립니다.

---

Made with ❤️ by SKN18-2nd-5Team
