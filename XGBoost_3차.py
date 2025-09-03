import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder # XGBoost는 LabelEncoder가 필요
import xgboost as xgb # XGBoost 라이브러리 임포트
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score

def ML_modeling_xgboost():
    # 1. 데이터 불러오기
    try:
        df = pd.read_csv("data/hotel_bookings.csv")
    except FileNotFoundError:
        print("Error: 'hotel_bookings.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return

    # 2. 데이터 전처리
    df.drop(['reservation_status', 'reservation_status_date'], axis=1, inplace=True)
    df[['company', 'agent', 'children']] = df[['company', 'agent', 'children']].fillna(0)
    df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 5. 범주형 데이터 인코딩 (LabelEncoder 사용)
    # XGBoost는 object 타입을 처리할 수 없으므로 숫자형으로 변환해야 합니다.
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])

    # 6. 데이터 분리
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 7. 모델 학습 (XGBoost로 변경)
    xgb_model = xgb.XGBClassifier(
        random_state=42,
        eval_metric='logloss' # 경고 메시지를 피하기 위해 평가 지표 설정
    )
    xgb_model.fit(X_train, y_train)

    # 8. 예측 및 평가
    y_pred = xgb_model.predict(X_test)
    
    print("XGBoost 모델 평가")
    print("--------------------")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    print(f"정확도(Accuracy): {accuracy_score(y_test, y_pred):.4f}")
    print("\n혼동 행렬(Confusion Matrix):")
    print(confusion_matrix(y_test, y_pred))
    print("\n분류 보고서(Classification Report):")
    print(classification_report(y_test, y_pred))

# 함수 실행
ML_modeling_xgboost()

# f1_score 0.8339