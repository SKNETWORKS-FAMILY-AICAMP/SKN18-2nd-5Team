import pandas as pd
from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder  <- CatBoost는 필요 없음
from catboost import CatBoostClassifier  # CatBoost 라이브러리 임포트
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score


def ML_modeling_catboost():
    # 1. 데이터 불러오기
    try:
        df = pd.read_csv("data/hotel_bookings.csv")
    except FileNotFoundError:
        print("Error: 'hotel_bookings.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return

    # 2. 데이터 전처리
    df.drop(['reservation_status', 'reservation_status_date'], axis=1, inplace=True)
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 3. 피처 엔지니어링 (이전과 동일)
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    epsilon = 1e-6
    df['cancellation_rate'] = df['previous_cancellations'] / (df['previous_cancellations'] + df['previous_bookings_not_canceled'] + epsilon)

    # 4. 날짜 피처 처리 (이전과 동일)
    month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    df['arrival_date_month_number'] = df['arrival_date_month'].map(month_map)
    df['arrival_date'] = pd.to_datetime(
        df['arrival_date_year'].astype(str) + '-' +
        df['arrival_date_month_number'].astype(str) + '-' +
        df['arrival_date_day_of_month'].astype(str),
        errors='coerce'
    )
    df['arrival_year'] = df['arrival_date'].dt.year
    df['arrival_month'] = df['arrival_date'].dt.month
    df['arrival_day'] = df['arrival_date'].dt.day
    df['arrival_day_of_week'] = df['arrival_date'].dt.dayofweek
    df.drop(['arrival_date', 'arrival_date_year', 'arrival_date_month', 'arrival_date_week_number', 'arrival_date_day_of_month', 'arrival_date_month_number'], axis=1, inplace=True)

    # 5. 데이터 분리 (인코딩 전에 수행)
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    
    # CatBoost를 위해 범주형 피처의 컬럼 이름을 찾아 리스트로 저장
    categorical_features_indices = [col for col in X.columns if X[col].dtype == 'object']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 6. 모델 학습 (CatBoost로 변경)
    # cat_features 파라미터에 범주형 피처 리스트를 전달
    cat_model = CatBoostClassifier(
        cat_features=categorical_features_indices,
        random_state=42,
        verbose=0  # 학습 과정을 출력하지 않음
    )
    cat_model.fit(X_train, y_train)

    # 7. 예측 및 평가
    y_pred = cat_model.predict(X_test)
    
    print("CatBoost 모델 평가")
    print("--------------------")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    print(f"정확도(Accuracy): {accuracy_score(y_test, y_pred):.4f}")
    print("\n혼동 행렬(Confusion Matrix):")
    print(confusion_matrix(y_test, y_pred))
    print("\n분류 보고서(Classification Report):")
    print(classification_report(y_test, y_pred))

# 함수 실행
ML_modeling_catboost()