import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
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
    # --- 새로운 피처 생성 (동일) ---
    df['total_stay'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['is_with_children'] = (df['children'] > 0) | (df['babies'] > 0)

    # --- 데이터 전처리 (CatBoost에 맞게 수정) ---
    if 'reservation_status' in df.columns and 'reservation_status_date' in df.columns:
        df = df.drop(['reservation_status', 'reservation_status_date'], axis=1)

    # 결측치 처리 (company, agent는 숫자형이므로 그대로 둠)
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    # CatBoost는 object 타입의 결측치를 내부적으로 처리할 수 있으나, 일관성을 위해 최빈값으로 채웁니다.
    if df['country'].isnull().sum() > 0:
        df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 'meal' 컬럼의 'Undefined'를 'SC'로 대체
    df['meal'] = df['meal'].replace('Undefined', 'SC')

    # bool 타입을 0과 1로 변환
    df['is_with_children'] = df['is_with_children'].astype(int)

    # ⭐⭐⭐ --- CatBoost 모델을 위한 준비 (핵심 변경점) --- ⭐⭐⭐
    # 1. 범주형 피처의 리스트를 정의 (Label Encoding을 하지 않습니다!)
    categorical_features = [col for col in df.columns if df[col].dtype == 'object']
    print("CatBoost가 처리할 범주형 피처:")
    print(categorical_features)

    # 2. 데이터 분리
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 3. 클래스 가중치 계산 (LightGBM과 동일)
    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    print(f"\n클래스 가중치 (scale_pos_weight): {scale_pos_weight:.2f}")

    # 4. CatBoost 모델 정의
    cat_clf = CatBoostClassifier(
        cat_features=categorical_features, # 범주형 피처 리스트 전달
        scale_pos_weight=scale_pos_weight,  # 클래스 가중치 적용
        random_state=42,
        verbose=0  # 학습 과정 출력 생략
    )
    # ⭐⭐⭐ --- 변경점 끝 --- ⭐⭐⭐

    # 모델 학습
    print("CatBoost 모델 학습을 시작합니다...")
    cat_clf.fit(X_train, y_train)
    preds = cat_clf.predict(X_test)
    print("모델 학습이 완료되었습니다.")

    # 평가
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

    # 피처 중요도 시각화
    feature_importances = cat_clf.get_feature_importance()
    feature_names = X_train.columns
    importance_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importances})
    importance_df = importance_df.sort_values(by='importance', ascending=False).head(20)

    plt.figure(figsize=(10, 8))
    sns.barplot(x='importance', y='feature', data=importance_df)
    plt.title('CatBoost Feature Importances')
    plt.tight_layout()
    plt.savefig("feature_importances_catboost.png")
    print("\n피처 중요도 그래프를 'feature_importances_catboost.png' 로 저장했습니다.")

    # 혼동 행렬 시각화
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Canceled', 'Canceled'], yticklabels=['Not Canceled', 'Canceled'])
    plt.title('Confusion Matrix (CatBoost)')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig("confusion_matrix_catboost.png")
    print("혼동 행렬 그래프를 'confusion_matrix_catboost.png' 로 저장했습니다.")

    # f1-score 0.8446