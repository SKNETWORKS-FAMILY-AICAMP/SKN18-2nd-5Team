import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score

def ML_modeling():
    # 1. 데이터 불러오기 (경로 수정)
    try:
        df = pd.read_csv("data/hotel_bookings.csv")
    except FileNotFoundError:
        print("Error: 'hotel_bookings.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return

    # 2. 데이터 전처리
    
    # is_canceled와 높은 상관관계가 있거나, 예측 시점에서는 알 수 없는 정보(Data Leakage)이므로 삭제
    df.drop(['reservation_status', 'reservation_status_date'], axis=1, inplace=True)

    # 결측치 처리
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 3. 피처 엔지니어링 (새로운 피처 생성)
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    
    # 0으로 나누는 오류 방지
    epsilon = 1e-6
    df['cancellation_rate'] = df['previous_cancellations'] / (df['previous_cancellations'] + df['previous_bookings_not_canceled'] + epsilon)
    
    # 4. 날짜 피처 처리 (오류 수정의 핵심 부분)
    
    # 'arrival_date_month'를 숫자로 변환
    month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    df['arrival_date_month'] = df['arrival_date_month'].map(month_map)

    # datetime 객체 생성
    df['arrival_date'] = pd.to_datetime(
        df['arrival_date_year'].astype(str) + '-' +
        df['arrival_date_month'].astype(str) + '-' +
        df['arrival_date_day_of_month'].astype(str),
        errors='coerce' # 혹시 잘못된 날짜가 있으면 NaT로 처리
    )

    # datetime 객체에서 유용한 숫자 피처 추출
    df['arrival_year'] = df['arrival_date'].dt.year
    df['arrival_month'] = df['arrival_date'].dt.month
    df['arrival_day'] = df['arrival_date'].dt.day
    df['arrival_day_of_week'] = df['arrival_date'].dt.dayofweek # 월요일=0, 일요일=6
    
    # 더 이상 필요 없는 원본 날짜 컬럼들 삭제
    df.drop(['arrival_date', 'arrival_date_year', 'arrival_date_month', 'arrival_date_week_number', 'arrival_date_day_of_month'], axis=1, inplace=True)
    
    # 5. 범주형 데이터 인코딩
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])
        # LightGBM은 'category' 타입으로 변환해주면 더 잘 처리합니다.
        df[col] = df[col].astype('category')

    # 6. 데이터 분리
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y) # stratify 추가하여 클래스 비율 유지

    # 7. 모델 학습
    lgb_model = lgb.LGBMClassifier(random_state=42)
    lgb_model.fit(X_train, y_train)

    # 8. 예측 및 평가
    y_pred = lgb_model.predict(X_test)
    
    print("LightGBM 모델 평가")
    print("--------------------")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    print(f"정확도(Accuracy): {accuracy_score(y_test, y_pred):.4f}")
    print("\n혼동 행렬(Confusion Matrix):")
    print(confusion_matrix(y_test, y_pred))
    print("\n분류 보고서(Classification Report):")
    print(classification_report(y_test, y_pred))

# 함수 실행
ML_modeling()