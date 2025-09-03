import pandas as pd
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

def ML_modeling():

    # 1. 데이터 불러오기
    df = pd.read_csv("data/hotel_bookings.csv")
    
    # 2. 데이터 전처리
    # 예약 상태 관련 컬럼 제거 (타겟 변수와 강한 상관관계)
    df.drop(['reservation_status', 'reservation_status_date'], axis=1, inplace=True)
    
    # 결측치 처리
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 3. 데이터 분리
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 4. 범주형 피처 식별
    # CatBoost에 알려줄 범주형 컬럼 목록을 준비
    categorical_features_indices = [col for col in X.columns if X[col].dtype == 'object']
    print("범주형 피처:", categorical_features_indices)

    # 5. 모델 학습
    # cat_features 파라미터에 범주형 컬럼 목록을 전달
    model = CatBoostClassifier(
        random_state=42,
        cat_features=categorical_features_indices,
        verbose=100, # 100번 반복마다 학습 과정 출력
        iterations=1000 # 최대 반복 횟수
    )
    
    # early_stopping_rounds: 검증 데이터 성능이 50번 이상 개선되지 않으면 학습 조기 종료
    model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=50
    )

    # 6. 예측 및 평가
    y_pred = model.predict(X_test)

    print("\n--- 최종 평가 결과 ---")
    print("F1 Score:", f1_score(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

if __name__ == "__main__":
    ML_modeling()

# 기본 전처리(결측치 처리, 예약상태 확인 관련 컬럼 제거)
# f1-score 0.8401