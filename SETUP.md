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

# 작업 후 커밋
git add .
git commit -m "feat: 새 기능 추가"

# 푸시
git push origin feature/your-feature
```

### 코드 스타일
- Python: PEP8 준수
- JavaScript: ESLint 설정 따르기
- 커밋 메시지: Conventional Commits 형식

## 📞 도움이 필요하면
- GitHub Issues에 문제 등록
- 팀 채널에서 질문
- README.md 참조
