# 📁 Frontend 프로젝트 구조

## 폴더 구조
```
frontend/
├── 📄 package.json              # 프로젝트 정보 및 의존성
├── 📄 package-lock.json         # 정확한 패키지 버전 기록(절대 수정 X)
├── 📄 vite.config.js           # Vite 빌드 도구 설정 (*Vite: 개발 시 코드 변경사항 즉비 반영하는 도구) -> React flugin 사용
├── 📄 eslint.config.js         # 코드 품질(스타일, 오류 등) 검사 설정 
├── 📄 index.html               # 웹페이지 진입점 (HTML)
├── 📄 README.md                # 프로젝트 설명서
│
├── 📁 public/                  # 정적 파일들
│   └── vite.svg               # 파비콘 (탭 아이콘)
│
└── 📁 src/                     # 실제 소스 코드
    ├── 📄 main.jsx            # React 앱 시작점
    ├── 📄 App.jsx             # 메인 앱 컴포넌트
    ├── 📄 App.css             # 앱 전체 스타일
    ├── 📄 index.css           # 기본 글로벌 스타일
    │
    ├── 📁 assets/             # 이미지, 아이콘 등
    │   └── react.svg         # React 로고
    │
    ├── 📁 components/         # 재사용 가능한 UI 컴포넌트
    │   ├── Navbar.jsx        # 네비게이션 바
    │   └── Navbar.css        # 네비게이션 바 스타일
    │
    └── 📁 pages/              # 각 페이지 컴포넌트
        ├── HomePage.jsx      # 홈페이지
        ├── HomePage.css      # 홈페이지 스타일
        ├── CancellationPrediction.jsx  # 취소 예측 페이지
        ├── CancellationPrediction.css  # 취소 예측 페이지 스타일
        ├── BreakfastPrediction.jsx     # 조식 예측 페이지
        └── BreakfastPrediction.css     # 조식 예측 페이지 스타일
```

## 주요 파일 설명

### 설정 파일
| 파일 | 역할 |
|------|------|
| `package.json` | 프로젝트 정보, 의존성 라이브러리, 실행 스크립트 |
| `vite.config.js` | 개발 서버 및 빌드 설정 |
| `eslint.config.js` | 코드 품질 검사 규칙 |

### 진입점
| 파일 | 역할 |
|------|------|
| `index.html` | 브라우저가 처음 로드하는 HTML 파일 |
| `src/main.jsx` | React 앱을 HTML에 연결하는 시작점 |
| `src/App.jsx` | 전체 앱의 구조와 라우팅 정의 |

### 스타일링
| 파일 | 역할 |
|------|------|
| `src/index.css` | 전체 웹사이트 기본 스타일 |
| `src/App.css` | 앱 메인 컴포넌트 스타일 |
| `src/**/*.css` | 각 컴포넌트별 개별 스타일 |

## 앱 동작 흐름

1. **브라우저** → `index.html` 로드
2. **HTML** → `src/main.jsx` 실행
3. **main.jsx** → `App.jsx` 렌더링
4. **App.jsx** → URL에 따라 페이지 컴포넌트 표시
5. **각 컴포넌트** → 해당 CSS로 스타일 적용

## 개발 시작하기

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build
```

## 주요 라이브러리

- **React**: UI 라이브러리
- **React Router**: 페이지 라우팅
- **Vite**: 빠른 개발 서버
- **Axios**: HTTP 요청
- **Chart.js**: 차트 생성
- **Framer Motion**: 애니메이션