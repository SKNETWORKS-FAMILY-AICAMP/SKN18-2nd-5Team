# 🏨 호텔 예약 취소 예측 모델

## 📋 프로젝트 개요
호텔 및 리조트 예약자 데이터를 분석하여 **예약 취소율을 예측**하는 머신러닝 모델 개발 프로젝트입니다.  
학습용 데이터로 다양한 모델을 훈련시키고, 테스트 데이터에서 예측 성능을 비교 분석하여 최적의 모델을 선정합니다.

## 🏗️ 프로젝트 구조

```
SKN18-2nd-5Team/
├── main.py                    # 메인 실행 파일 (모든 모델 자동 실행)
├── requirements.txt           # 패키지 의존성
├── README.md                  # 프로젝트 설명서
├── data/                      # 데이터 폴더
│   ├── hotel_bookings_train.csv
│   └── hotel_bookings_test.csv
├── service/                   # 서비스 모듈
│   ├── data_setup.py         # 데이터 로드 모듈
│   ├── evaluation.py         # 모델 평가 모듈
│   ├── preprocessing/        # 데이터 전처리 모듈
│   │   ├── adata_preprocessing.py
│   │   ├── cleansing.py
│   │   ├── encoding.py
│   │   └── featureExtraction.py
│   └── modeling/            # 모델링 모듈
│       ├── model.py             # 모델 생성 및 하이퍼파라미터
│       ├── training.py          # 모델 학습 및 평가
│       ├── cross_validation.py  # 교차 검증
│       └── metrics.py           # 평가 지표 정의
└── reports/                # 성능 보고서 저장 폴더
    ├── gradient_boosting_report.json
    ├── extra_trees_report.json
    ├── lightgbm_report.json
    ├── logistic_regression_report.json
    └── naive_bayes_report.json
```

## 🚀 실행 방법

### 1. 환경 설정
```bash
# 가상환경 활성화
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 패키지 설치
pip install -r requirements.txt
```

### 2. 실행 방법
```bash
# 모든 모델 자동 실행 (7개 모델)
python main.py
```

**실행되는 모델:**
- Gradient Boosting
- Extra Trees  
- XGBoost
- Random Forest
- LightGBM
- Logistic Regression
- Naive Bayes

**제외된 모델 (시간 소요):**
- SVM, Neural Network, KNN, AdaBoost, catboost

## 🔧 주요 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `--path_train` | `./data/hotel_bookings_train.csv` | 학습 데이터 경로 |
| `--path_test` | `./data/hotel_bookings_test.csv` | 테스트 데이터 경로 |
| `--target_name` | `is_canceled` | 타겟 컬럼명 |
| `--drop_cols` | 자동 설정 | 제거할 컬럼 목록 |
| `--encoding_cols` | 자동 설정 | 인코딩할 범주형 컬럼 |

## 📊 데이터 처리 파이프라인

### 1. 데이터 로드 (`data_setup.py`)
- **변수 규칙**: 
  - 학습용 피처: `x_tr`
  - 학습용 타겟: `y_tr` 
  - 테스트용 피처: `x_te`
  - 테스트용 타겟: `y_te`

### 2. 데이터 전처리 (`preprocessing/`)
- **데이터 정제**: 결측값 처리, 이상치 제거
- **피처 엔지니어링**: 새로운 특성 생성
- **모델별 인코딩**: 범주형 데이터 변환
  - LightGBM: `category` 타입 변환
  - 기타 모델: 원-핫 인코딩 적용

### 3. 모델 학습 및 평가 (`modeling/`)
- **지원 모델**: 7개 모델 (빠른 실행 위해 선별)
- **교차 검증**: 5-fold StratifiedKFold 사용
- **실제 테스트**: 별도 테스트 데이터로 실제 성능 측정
- **평가 지표**: F1-Score, Accuracy, ROC-AUC
- **보고서 생성**: 각 모델별 성능 보고서 자동 저장 (`reports/` 폴더)

## 📈 모델 성능 평가

### 평가 방식
1. **교차 검증**: 학습 데이터에서 5-fold StratifiedKFold로 모델 안정성 확인
2. **테스트 평가**: 별도의 테스트 데이터로 실제 성능 측정
3. **모델 비교**: 여러 알고리즘의 성능을 정량적으로 비교
4. **성능 보고서**: 각 모델 실행 시마다 콘솔 출력 + JSON 파일 저장

### 평가 지표
모든 모델에 대해 다음 3가지 지표로 성능을 평가합니다:
- **F1-Score**: 정밀도와 재현율의 조화평균 (불균형 데이터 고려)
- **Accuracy**: 전체 정확도 (기본 성능 지표)
- **ROC-AUC**: ROC 곡선 아래 면적 (임계값 독립적 성능)

### 성능 보고서 형식
```json
{
  "model_name": "lightgbm",
  "timestamp": "2025-09-04 19:28:58",
  "cross_validation": {
    "cv_f1_score": 0.8104,
    "cv_accuracy": 0.8942,
    "cv_roc_auc": 0.961
  },
  "test_performance": {
    "test_f1_score": 0.674,
    "test_accuracy": 0.7858,
    "test_roc_auc": 0.8707
  },
  "model_details": {
    "training_time": "10.38 seconds"
  }
}
```

### 현재 사용 가능한 보고서
현재 `reports/` 폴더에는 다음 모델들의 성능 보고서가 저장되어 있습니다:
- `gradient_boosting_report.json`
- `extra_trees_report.json`
- `lightgbm_report.json`
- `logistic_regression_report.json`
- `naive_bayes_report.json`

## 📝 개발 규칙

### ⚠️ 필수 준수 사항
1. **main.py 실행으로만 결과 도출** - 다른 파일 직접 실행 금지
2. **모듈화 구조 유지** - 기존 폴더/파일 형식 변경 금지
3. **주석 및 로깅 필수**:
   ```python
   # -- 수정 이유: 성능 향상을 위한 하이퍼파라미터 조정
   logging.info("데이터 전처리 완료")
   ```

### 📁 파일 관리
- 추가 파일은 `.gitignore`에 등록
- 기존 모듈 구조 변경 시 사전 협의 필수

## 🎯 향후 계획
- [ ] Stacking 모델 구현
- [ ] 모델 성능 시각화 대시보드
- [ ] 피처 중요도 분석 및 해석
- [ ] 모델 앙상블 기법 적용

## 👥 팀 정보
- **팀명**: SKN18-2nd-5Team
- **브랜치**: INHA-2
- **프로젝트 기간**: 2024년 9월

## 📊 예상 결과
프로젝트 완료 후 다음과 같은 결과를 얻을 수 있습니다:

### 콘솔 출력 예시
```
==================================================
🏨 호텔 예약 취소 예측 모델 - 전체 모델 실행 시작
실행 시간: 2025-09-04 19:28:45
==================================================
📊 데이터 로드 시작...
✅ 데이터 로드 완료 (소요시간: 0.12초)
🔧 모델별 데이터 전처리 및 학습 시작...
🤖 총 7개 빠른 모델 학습 시작...
⚡ 실행 모델: Gradient Boosting, Extra Trees, XGBoost, Random Forest, LightGBM, Logistic Regression, Naive Bayes
--------------------------------------------------
[1/7] GRADIENT_BOOSTING 모델 학습 시작...
=== GRADIENT_BOOSTING 모델 성능 보고서 ===
교차 검증 결과:
- F1-Score: 0.8104
- Accuracy: 0.8942
- ROC-AUC: 0.9610

테스트 데이터 성능:
- F1-Score: 0.6740
- Accuracy: 0.7858
- ROC-AUC: 0.8707
학습 시간: 10.38초
✅ GRADIENT_BOOSTING 모델 훈련이 끝났습니다 (소요시간: 12.45초)
------------------------------
...
🎉 전체 모델 실행 완료!
총 소요시간: 125.67초
성공한 모델: 7개
📁 성능 보고서는 reports/ 폴더에 저장되었습니다.
==================================================
```

### 파일 결과물
- **성능 보고서**: `reports/` 폴더에 JSON 형식으로 저장
- **모델 비교 분석**: 각 모델의 강점과 약점 분석
- **피처 중요도**: 예측에 중요한 변수 순위
- **호텔 도메인 인사이트**: 취소 패턴 및 비즈니스 시사점

---
*📧 문의사항이 있으시면 팀 리더에게 연락해주세요.*
010...