import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 데이터 불러오기
try:
    df = pd.read_csv("data/hotel_bookings.csv")
except FileNotFoundError:
    print("Error: 'hotel_bookings.csv' 파일을 찾을 수 없습니다.")
    df = pd.DataFrame()

if not df.empty:
    # --- 1. 결측치 처리 (기존과 동일) ---
    df.drop(['reservation_status', 'reservation_status_date'], axis=1, inplace=True, errors='ignore')
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    if df['country'].isnull().sum() > 0:
        df['country'] = df['country'].fillna(df['country'].mode()[0])
    df['meal'] = df['meal'].replace('Undefined', 'SC')

    # --- 2. 가설 기반 신규 피처 생성 (종합) ---
    print("모든 가설을 종합하여 새로운 피처를 생성합니다...")

    # (기존 피처)
    df['is_meal_fb'] = (df['meal'] == 'FB').astype(int)
    df['is_market_segment_risky'] = df['market_segment'].isin(['Groups', 'Online TA']).astype(int)
    df['is_room_mismatch'] = (df['reserved_room_type'] != df['assigned_room_type']).astype(int)
    df['total_stay'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['total_guests'] = df['adults'] + df['children'] + df['babies']

    # ⭐⭐⭐ (추가된 피처) ⭐⭐⭐
    # 가설 4: 회사 통해 예약 여부
    df['is_company_booking'] = (df['company'] != 0).astype(int)
    # 가설 5: 에이전트 통해 예약 여부
    df['is_agent_booking'] = (df['agent'] != 0).astype(int)
    # 가설 6: 가족 단위 여부 (성인 1명 이상 + 아이/아기 1명 이상)
    df['is_family'] = ((df['adults'] > 0) & ((df['children'] > 0) | (df['babies'] > 0))).astype(int)

    # 가설 7: 고객 유형 분류 (1인 vs 가족 등)
    def get_customer_category(row):
        if row['total_guests'] == 1:
            return 'Solo'
        elif row['is_family'] == 1:
            return 'Family'
        elif row['total_guests'] == 2:
            return 'Couple'
        else:
            return 'Group'
    df['customer_category'] = df.apply(get_customer_category, axis=1)

    # --- 3. 범주형 데이터 인코딩 ---
    # LabelEncoder를 적용할 모든 object 타입 컬럼을 처리
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])

    # --- 4. 데이터 분리 ---
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # --- 5. LightGBM 모델 학습 ---
    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    print(f"\n클래스 가중치 (scale_pos_weight): {scale_pos_weight:.2f}")

    print("LightGBM 모델 학습을 시작합니다...")
    lgb_clf = lgb.LGBMClassifier(random_state=42, scale_pos_weight=scale_pos_weight)
    lgb_clf.fit(X_train, y_train)
    preds = lgb_clf.predict(X_test)
    print("모델 학습이 완료되었습니다.")

    # --- 6. 모델 평가 ---
    accuracy = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    conf_matrix = confusion_matrix(y_test, preds)
    class_report = classification_report(y_test, preds, target_names=['Not Canceled', 'Canceled'])

    print("\n--- 모델 평가 결과 ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score (for Canceled): {f1:.4f}")
    print("\nConfusion Matrix:")
    print(conf_matrix)
    print("\nClassification Report:")
    print(class_report)

    # --- 7. 시각화 ---
    plt.figure(figsize=(10, 8))
    lgb.plot_importance(lgb_clf, max_num_features=25) # 피처가 많아졌으므로 25개로 늘려서 확인
    plt.title("Feature Importances (Final Version)")
    plt.tight_layout()
    plt.savefig("flightgbm_5_feature_importances.png")
    print("\n피처 중요도 그래프를 'flightgbm_5_feature_importances.png' 로 저장했습니다.")

    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Canceled', 'Canceled'], yticklabels=['Not Canceled', 'Canceled'])
    plt.title('Confusion Matrix (Final Version)')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig("confusion_matrix_5.png")
    print("혼동 행렬 그래프를 'confusion_matrix_5.png' 로 저장했습니다.")

# f1-score 0.8350