# 🏨 호텔 예약 취소 예측 프로젝트 (Hotel Booking Cancellation Prediction)

## 📝 프로젝트 개요 (Overview)

이 프로젝트는 호텔 예약 데이터를 분석하여 고객의 예약 취소 여부를 예측하는 머신러닝 모델을 구축하는 것을 목표로 합니다.

호텔 산업에서 예약 취소는 예측 불가능한 수익 손실과 객실 관리의 비효율성을 초래하는 주요 문제입니다. 이 모델을 통해 호텔은 잠재적인 예약 취소 고객을 사전에 식별하고, 타겟 마케팅, 오버부킹 전략 수립 등 선제적인 조치를 통해 수익을 최적화할 수 있습니다.

## 📊 데이터셋 (Dataset)

본 프로젝트에서는 Kaggle에서 제공하는 **"Hotel Booking Demand"** 데이터를 사용했습니다.

  * **데이터 출처:** [Kaggle - Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand)
  * **데이터 기간:** 2015년 7월 1일 ~ 2017년 9월 14일
  * **데이터 구성:**
      * 두 종류의 호텔(리조트 호텔, 시티 호텔) 데이터 포함
      * 총 119,390개의 예약 기록
      * 32개의 변수 (ex: `lead_time`, `arrival_date_month`, `adr`, `customer_type`, `is_canceled` 등)

## 🎯 프로젝트 목표 (Goals)

1.  **탐색적 데이터 분석 (EDA):** 데이터 시각화를 통해 예약 취소에 영향을 미치는 주요 요인을 파악합니다.
2.  **데이터 전처리 및 피처 엔지니어링:** 모델 학습에 적합한 형태로 데이터를 정제하고, 새로운 파생 변수를 생성합니다.
3.  **머신러닝 모델 구축:** 다양한 분류 알고리즘을 사용하여 예약 취소 여부를 예측하는 최적의 모델을 개발합니다.
4.  **모델 평가 및 해석:** 모델의 성능을 평가하고, 어떤 변수가 예측에 가장 큰 영향을 미치는지 분석합니다.

## 🛠️ 기술 스택 (Tech Stack)

  * **Language:** `Python 3.8+`
  * **Libraries:**
      * `Pandas`: 데이터 조작 및 분석
      * `NumPy`: 수치 연산
      * `Matplotlib` & `Seaborn`: 데이터 시각화
      * `Scikit-learn`: 데이터 전처리, 모델링 및 평가
      * `Jupyter Notebook`: 프로젝트 개발 환경

## 📁 프로젝트 구조 (Project Structure)

```
.
├── data/
│   └── hotel_bookings.csv      # 원본 데이터 파일
├── notebooks/
│   ├── 01_EDA.ipynb            # 탐색적 데이터 분석 노트북
│   └── 02_Preprocessing_and_Modeling.ipynb # 데이터 전처리 및 모델링 노트북
├── README.md                   # 프로젝트 설명 파일
└── requirements.txt            # 라이브러리 및 의존성 관리 파일
```

## 🚀 실행 방법 (How to Run)

1.  **저장소 복제 (Clone the repository):**

    ```bash
    git clone https://github.com/[your-username]/hotel-cancellation-prediction.git
    cd hotel-cancellation-prediction
    ```

2.  **가상 환경 생성 및 활성화 (Create and activate a virtual environment):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows: venv\Scripts\activate
    ```

3.  **필요한 라이브러리 설치 (Install dependencies):**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Jupyter Notebook 실행 (Run Jupyter Notebook):**
    `notebooks/` 디렉토리의 노트북 파일들을 순서대로 실행합니다.

    ```bash
    jupyter notebook
    ```

## 📈 분석 과정 및 결과 요약 (Analysis & Results)

### 1\. 탐색적 데이터 분석 (EDA) 주요 결과

  * **리드 타임(Lead Time):** 예약 시점과 도착일 사이의 기간이 길수록 취소율이 높아지는 경향을 보였습니다.
  * **고객 유형(Customer Type):** 'Transient' 유형의 고객이 다른 그룹에 비해 높은 취소율을 보였습니다.
  * **보증금 유형(Deposit Type):** 'Non Refund'(환불 불가) 조건의 예약은 거의 취소되지 않았습니다.
  * **온라인 여행사(Online TA):** 온라인 여행사를 통해 예약된 경우 취소율이 상대적으로 높았습니다.

### 2\. 모델링 및 평가

  * **사용한 모델:** Logistic Regression, Random Forest, LightGBM
  * **성능 평가:** 정확도(Accuracy), 정밀도(Precision), 재현율(Recall), F1-Score, AUC-ROC를 사용하여 모델 성능을 종합적으로 평가했습니다.
  * **최종 모델:** **LightGBM** 모델이 가장 우수한 성능을 보였습니다.
      * **Accuracy:** 약 87%
      * **F1-Score:** 약 0.82
  * **주요 변수 중요도(Feature Importance):** `lead_time`, `deposit_type`, `adr`(일일 평균 요금), `country` 등이 예약 취소 예측에 중요한 영향을 미치는 것으로 나타났습니다.

## 🔮 향후 개선 방향 (Future Work)

  * **하이퍼파라미터 튜닝:** Grid Search, Bayesian Optimization 등을 통해 모델 성능을 추가적으로 최적화할 수 있습니다.
  * **다양한 모델 활용:** XGBoost, CatBoost 등 다른 앙상블 모델을 적용하여 성능을 비교 분석합니다.
  * **실시간 예측 시스템:** 모델을 API 형태로 배포하여 실시간으로 들어오는 예약에 대한 취소 확률을 예측하는 시스템을 구축합니다.