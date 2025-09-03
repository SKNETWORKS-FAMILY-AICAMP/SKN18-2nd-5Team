import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np # numpy 추가

# 데이터 불러오기
try:
    df = pd.read_csv("data/hotel_bookings.csv")
except FileNotFoundError:
    print("Error: 'hotel_bookings.csv' 파일을 찾을 수 없습니다.")
    df = pd.DataFrame()

if not df.empty:
    # --- 새로운 피처 생성 (이전과 동일) ---
    df['total_stay'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['is_with_children'] = (df['children'] > 0) | (df['babies'] > 0)

    # --- 데이터 전처리 (이전과 동일) ---
    if 'reservation_status' in df.columns and 'reservation_status_date' in df.columns:
        df = df.drop(['reservation_status', 'reservation_status_date'], axis=1)
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    if df['country'].isnull().sum() > 0:
        df['country'] = df['country'].fillna(df['country'].mode()[0])
    df['meal'] = df['meal'].replace('Undefined', 'SC')
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])
    df['is_with_children'] = df['is_with_children'].astype('category')

    # --- 데이터 분리 (이전과 동일) ---
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # ⭐⭐⭐ --- 모델 학습 (개선된 부분) --- ⭐⭐⭐
    # 1. 클래스 가중치 계산
    scale_pos_weight = np.sqrt(y_train.value_counts()[0] / y_train.value_counts()[1])
    print(f"클래스 가중치 (scale_pos_weight): {scale_pos_weight:.2f}")

    # 2. LightGBM 모델에 가중치 적용하여 학습
    print("개선된 LightGBM 모델 학습을 시작합니다...")
    lgb_clf = lgb.LGBMClassifier(random_state=42, scale_pos_weight=scale_pos_weight) # 파라미터 추가
    lgb_clf.fit(X_train, y_train)
    preds = lgb_clf.predict(X_test)
    print("모델 학습이 완료되었습니다.")
    # ⭐⭐⭐ --- 개선된 부분 끝 --- ⭐⭐⭐

    # --- 평가 (이전과 동일) ---
    accuracy = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    conf_matrix = confusion_matrix(y_test, preds)
    class_report = classification_report(y_test, preds, target_names=['Not Canceled', 'Canceled']) # 타겟 이름 추가

    print("\n--- 모델 평가 결과 ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score (for Canceled): {f1:.4f}")
    print("\nConfusion Matrix:")
    print(conf_matrix)
    print("\nClassification Report:")
    print(class_report)

    # --- 시각화 (이전과 동일) ---
    plt.figure(figsize=(10, 8))
    lgb.plot_importance(lgb_clf, max_num_features=20)
    plt.title("Feature Importances")
    plt.tight_layout()
    plt.savefig("feature_importances_v2.png")
    print("\n피처 중요도 그래프를 'feature_importances_v2.png' 로 저장했습니다.")

    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Canceled', 'Canceled'], yticklabels=['Not Canceled', 'Canceled'])
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig("confusion_matrix_v2.png")
    print("혼동 행렬 그래프를 'confusion_matrix_v2.png' 로 저장했습니다.")

# f1-score 0.8312
