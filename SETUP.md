# 🛠 팀원을 위한 설치 가이드

## 🚀 빠른 시작 (Windows)

### 1단계: 저장소 클론
```bash
git clone https://github.com/SKN18-2nd-5Team/hotel-prediction.git
cd SKN18-2nd-5Team
```

### 2단계: 백엔드 설치
```bash
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install --only-binary=all fastapi uvicorn[standard] pandas numpy scikit-learn joblib pydantic python-multipart python-dotenv
```

### 3단계: 프론트엔드 설치
```bash
cd ../frontend
npm install --legacy-peer-deps
```

### 4단계: 실행
**터미널 1 (백엔드)**:
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2 (프론트엔드)**:
```bash
cd frontend
npm run dev
```

### 5단계: 접속
- 웹사이트: http://localhost:5173
- API 문서: http://localhost:8000/docs

## 🔧 문제 해결

### 백엔드 패키지 설치 오류
```bash
# 방법 1: 개별 설치
pip install fastapi uvicorn pandas numpy scikit-learn joblib pydantic python-multipart python-dotenv

# 방법 2: 캐시 클리어 후 재시도
pip cache purge
pip install -r requirements.txt
```

### 프론트엔드 패키지 호환성 오류
```bash
# 기존 node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps --force
```
## 🔧 npm 의존성 충돌 해결방안

### 문제 상황
React 19를 사용할 때 다음과 같은 peer dependency 충돌이 발생할 수 있습니다:
- `lucide-react` vs React 19 타입 충돌
- `react-calendar` vs @types/react 버전 충돌
- `react-chartjs-2` vs React 19 호환성 문제

### 해결방법

#### 방법 1: .npmrc 설정 (권장)
프로젝트에 이미 `.npmrc` 파일이 설정되어 있습니다:
```bash
# frontend/.npmrc
legacy-peer-deps=true
auto-install-peers=true
```

#### 방법 2: 수동 설치 시 옵션 사용
만약 .npmrc가 없다면 다음 명령어를 사용하세요:
```bash
npm install --legacy-peer-deps
```

#### 방법 3: 완전 초기화 (문제가 지속될 경우)
```bash
cd frontend
# 기존 설치 파일 삭제
Remove-Item -Recurse -Force node_modules  # Windows PowerShell
Remove-Item -Force package-lock.json

# 재설치
npm install
```

### 업데이트된 패키지 버전
프로젝트에서 사용하는 React 19 호환 패키지들:
- `react-calendar`: ^5.0.0 (React 19 지원)
- `react-chartjs-2`: ^5.3.0 (최신 버전)
- `react-router-dom`: ^7.1.1 (React 19 호환)
- `lucide-react`: ^0.460.0 (최신 버전)


### 데이터 파일 경로 오류
- `ML/data/hotel_bookings.csv` 파일이 프로젝트 루트에 있는지 확인
- 상대경로로 자동 탐지되므로 별도 설정 불필요

## 📝 개발 시 주의사항

1. **가상환경 사용**: Python 가상환경을 반드시 사용하세요
2. **포트 충돌**: 8000, 5173 포트가 사용 중이면 변경하세요
3. **Node 버전**: Node.js 16 이상 사용 권장
4. **Python 버전**: Python 3.8 이상 사용 권장

## 🤝 팀 협업

### Git 워크플로우
```bash
# 최신 코드 받기
git pull origin main

# 새 기능 브랜치 생성
git checkout -b feature/your-feature

# 🏨 HotelPredict AI - 호텔 예약 관리 시스템

## 📋 프로젝트 소개

HotelPredict AI는 머신러닝을 활용한 지능형 호텔 예약 관리 시스템입니다. 예약 취소율을 예측하고 조식 준비 인원을 최적화하여 호텔 운영의 효율성을 극대화합니다.

### ✨ 주요 기능

- **📊 예약 취소 예측**: 머신러닝 모델을 통한 정확한 취소율 예측
- **☕ 조식 인원 예측**: 일별 조식 준비 인원 최적화
- **📅 달력 기반 인터페이스**: 직관적인 날짜 선택 및 예측
- **📈 실시간 통계**: 예약 데이터의 실시간 분석 및 시각화

## 🚀 빠른 시작 (5분 설치)

### 🎯 요약
1. **Python 3.8+, Node.js 16+, Git 설치**
2. **저장소 클론**: `git clone [URL]`
3. **백엔드**: `cd backend` → `python -m venv venv` → `venv\Scripts\activate` → `pip install --only-binary=all fastapi uvicorn[standard] pandas numpy scikit-learn joblib pydantic python-multipart python-dotenv` → `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. **프론트엔드**: 새 터미널에서 `cd frontend` → `npm install --legacy-peer-deps` → `npm run dev`
5. **접속**: http://localhost:5173

---

## 🚀 상세 설치 가이드

### 필수 요구사항

- **Python 3.8 이상** (권장: 3.10 또는 3.11)
  - [Python 공식 다운로드](https://www.python.org/downloads/)
  - 설치 시 "Add Python to PATH" 체크 필수
- **Node.js 16 이상** (권장: 18 LTS)
  - [Node.js 공식 다운로드](https://nodejs.org/)
- **Git**
  - [Git 공식 다운로드](https://git-scm.com/)

### 설치 방법

### 🔍 설치 전 확인사항

다음 명령어로 필수 프로그램이 설치되어 있는지 확인하세요:

```bash
# Python 버전 확인 (3.8 이상이어야 함)
python --version

# Node.js 버전 확인 (16 이상이어야 함)
node --version

# npm 버전 확인
npm --version

# Git 버전 확인
git --version
```

#### 1. 저장소 클론
```bash
git clone https://github.com/SKN18-2nd-5Team/hotel-prediction.git
cd SKN18-2nd-5Team
```

> **📁 프로젝트 구조 확인**: 클론 후 다음 폴더들이 있는지 확인하세요
> - `backend/` (백엔드 코드)
> - `frontend/` (프론트엔드 코드)  
> - `ML/data/hotel_bookings.csv` (데이터 파일)

#### 2. 백엔드 설치 및 실행

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화 (강력 권장)
python -m venv venv

# Windows 사용자
venv\Scripts\activate

# 가상환경 활성화 확인 (프롬프트 앞에 (venv)가 표시되어야 함)

# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 설치 (Windows 권장 방법)
pip install --only-binary=all fastapi uvicorn[standard] pandas numpy scikit-learn joblib pydantic python-multipart python-dotenv
```

> **⚠️ 설치 중 오류 발생 시**:
> ```bash
> # 방법 1: requirements.txt 사용
> pip install -r requirements.txt
> 
> # 방법 2: 개별 설치
> pip install fastapi uvicorn pandas numpy scikit-learn joblib pydantic python-multipart python-dotenv
> ```

```bash
# FastAPI 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ **성공 확인**: 브라우저에서 http://localhost:8000/docs 접속 시 API 문서가 보이면 성공

#### 3. 프론트엔드 설치 및 실행

# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 패키지 설치 (React 19 호환성 해결)
npm install --legacy-peer-deps
```

> **⚠️ npm 설치 중 오류 발생 시**:
> ```bash
> # 캐시 정리 후 재시도
> npm cache clean --force
> rm -rf node_modules package-lock.json
> npm install --legacy-peer-deps --force
> ```

```bash
# React 개발 서버 실행
npm run dev
```

## ✅ 설치 완료 체크리스트

다음 항목들을 모두 확인하세요:

- [ ] **백엔드 서버 실행 중**: http://localhost:8000/docs 에서 API 문서 확인
- [ ] **프론트엔드 서버 실행 중**: http://localhost:5173 에서 웹사이트 접속
- [ ] **메인 페이지 로딩**: 통계 데이터와 차트가 표시됨
- [ ] **취소 예측 페이지**: 달력이 표시되고 날짜 클릭 가능
- [ ] **조식 예측 페이지**: 조식 관련 인터페이스 표시
- [ ] **데이터 로딩**: 콘솔에 "Loaded xxxxx booking records" 메시지 확인

> **🎉 모든 항목이 체크되면 설치 완료!** 이제 HotelPredict AI를 사용할 수 있습니다.

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

## 👥 팀 정보

**SKN18-2nd-5Team**
- 호텔 예약 데이터 분석 및 예측 서비스 개발팀

Made with ❤️ by SKN18-2nd-5Team

