import pandas as pd
from sklearn.model_selection import train_test_split
# CatBoostClassifier를 import 합니다.
from catboost import CatBoostClassifier
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
    # --- 1. 결측치 처리 (수정) ---
    # ... (이전 코드 생략)
    # company와 agent 피처를 결측치 여부에 따라 1과 0으로 변환
    df['company'] = df['company'].notnull().astype(int)
    df['agent'] = df['agent'].notnull().astype(int)
    df['children'] = df['children'].fillna(df['children'].median())
    if df['country'].isnull().sum() > 0:
        df['country'] = df['country'].fillna(df['country'].mode()[0])

    # --- 2. 가설 기반 신규 피처 생성 (모두 유지) ---
    print("모든 가설을 종합하여 새로운 피처를 생성합니다...")
    df['is_meal_fb'] = (df['meal'] == 'FB').astype(int)
    df['is_market_segment_risky'] = df['market_segment'].isin(['Groups', 'Online TA']).astype(int)
    df['is_room_mismatch'] = (df['reserved_room_type'] != df['assigned_room_type']).astype(int)
    df['total_stay'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['is_company_booking'] = (df['company'] != 0).astype(int)
    df['is_agent_booking'] = (df['agent'] != 0).astype(int)
    df['is_family'] = ((df['adults'] > 0) & ((df['children'] > 0) | (df['babies'] > 0))).astype(int)

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

    # ⭐⭐⭐ --- 3. CatBoost를 위한 데이터 준비 (핵심 변경점) --- ⭐⭐⭐
    # CatBoost가 직접 처리할 범주형 피처 리스트를 정의합니다.
    # Label Encoding을 적용하지 않고, 원래의 object 타입을 그대로 사용합니다.
    categorical_features = [col for col in df.columns if df[col].dtype == 'object']
    print("\nCatBoost가 처리할 범주형 피처:")
    print(categorical_features)

    # --- 4. 데이터 분리 ---
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # --- 5. CatBoost 모델 학습 ---
    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    print(f"\n클래스 가중치 (scale_pos_weight): {scale_pos_weight:.2f}")

    print("CatBoost 모델 학습을 시작합니다...")
    cat_clf = CatBoostClassifier(
        cat_features=categorical_features,  # 범주형 피처 리스트 전달
        scale_pos_weight=scale_pos_weight,    # 클래스 가중치 적용
        random_state=42,
        verbose=0  # 학습 과정 출력 생략
    )
    cat_clf.fit(X_train, y_train)
    preds = cat_clf.predict(X_test)
    print("모델 학습이 완료되었습니다.")

    # --- 6. 모델 평가 (기존과 동일) ---
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

    # --- 7. 시각화 (CatBoost 방식) ---
    feature_importances = cat_clf.get_feature_importance()
    feature_names = X_train.columns
    importance_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importances})
    importance_df = importance_df.sort_values(by='importance', ascending=False).head(25)

    plt.figure(figsize=(10, 8))
    sns.barplot(x='importance', y='feature', data=importance_df)
    plt.title('CatBoost Feature Importances (Final Version)')
    plt.tight_layout()
    plt.savefig("feature_importances_catboost_4.png")
    print("\n피처 중요도 그래프를 'feature_importances_catboost_4.png' 로 저장했습니다.")

    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Canceled', 'Canceled'], yticklabels=['Not Canceled', 'Canceled'])
    plt.title('Confusion Matrix (CatBoost Final Version)')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig("confusion_matrix_catboost_4.png")
    print("혼동 행렬 그래프를 'confusion_matrix_catboost_4.png' 로 저장했습니다.")

# notion에 있는 가설 추가 버전
# company와 agent 피처를 결측치 유무에 따라 1과 0으로 치환
# f1-score -> 0.8355