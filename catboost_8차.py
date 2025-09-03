import pandas as pd
from sklearn.model_selection import train_test_split
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
    # reservation_status는 is_canceled와 직접적인 관련이 있으므로 제거
    if 'reservation_status' in df.columns:
        df.drop(['reservation_status', 'reservation_status_date'], axis=1, inplace=True, errors='ignore')

    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    if df['country'].isnull().sum() > 0:
        df['country'] = df['country'].fillna(df['country'].mode()[0])
    df['meal'] = df['meal'].replace('Undefined', 'SC')

    # --- 2. 가설 기반 신규 피처 생성 (모두 유지) ---
    print("가설 기반 신규 피처를 생성합니다...")
    df['is_meal_fb'] = (df['meal'] == 'FB').astype(int)
    df['is_market_offline'] = ((df['market_segment'] == 'Offline TA/TO') | (df['market_segment'] == 'Direct')).astype(int)
    df['is_repeated_and_not_canceled'] = ((df['is_repeated_guest'] == 1) & (df['previous_cancellations'] == 0)).astype(int)
    df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['total_guests'] = df['adults'] + df['children'] + df['babies']
    df['has_babies'] = (df['babies'] > 0).astype(int)
    # 0으로 나누는 경우를 방지하기 위해 1e-6 (아주 작은 값)을 더해줍니다.
    df['children_ratio'] = df['children'] / (df['total_guests'] + 1e-6)
    df['adr_per_person'] = df['adr'] / (df['total_guests'] + 1e-6)

    # 불필하다고 판단되는 피처 제거
    df.drop(['adults', 'children', 'babies', 'days_in_waiting_list'], axis=1, inplace=True)
    print("가설 기반 피처 생성 완료.")

    # --- 2-1. 날짜 피처 생성 (새로 추가된 부분) ---
    print("날짜 관련 신규 피처를 생성합니다...")
    # 월 이름을 숫자로 매핑
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['arrival_date_month_numeric'] = df['arrival_date_month'].map(month_map)

    # 날짜 형식으로 변환
    df['arrival_date'] = pd.to_datetime(
        df['arrival_date_year'].astype(str) + '-' +
        df['arrival_date_month_numeric'].astype(str) + '-' +
        df['arrival_date_day_of_month'].astype(str),
        errors='coerce'
    )
    
    # 혹시 모를 NaT 값 처리 (날짜 변환 실패 시)
    if df['arrival_date'].isnull().sum() > 0:
        df.dropna(subset=['arrival_date'], inplace=True)


    # 요일 피처 생성 (0: 월요일, 6: 일요일)
    df['day_of_week'] = df['arrival_date'].dt.dayofweek

    # 주말 여부 피처 생성 (토요일, 일요일)
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

    # 계절 피처 생성
    def get_season(month):
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Autumn'
        else:
            return 'Winter'
    df['season'] = df['arrival_date_month_numeric'].apply(get_season)

    # 불필요한 날짜 컬럼 제거
    df.drop(['arrival_date_year', 'arrival_date_month', 'arrival_date_day_of_month', 'arrival_date_month_numeric', 'arrival_date'], axis=1, inplace=True, errors='ignore')
    print("날짜 피처 생성 및 기존 날짜 컬럼 제거 완료.")

    # --- 3. 범주형 피처 처리 ---
    # CatBoost는 내부적으로 범주형 피처를 처리하므로, 원-핫 인코딩이나 레이블 인코딩을 적용하지 않고, 원래의 object 타입을 그대로 사용합니다.
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

    # --- 6. 모델 평가 ---
    print("\n--- 모델 평가 결과 ---")
    print("정확도:", accuracy_score(y_test, preds))
    print("F1 스코어:", f1_score(y_test, preds))
    print("\n혼동 행렬:")
    print(confusion_matrix(y_test, preds))
    print("\n분류 리포트:")
    print(classification_report(y_test, preds))

    # --- 7. 피처 중요도 시각화 ---
    plt.figure(figsize=(10, 12))
    feat_importances = pd.Series(cat_clf.feature_importances_, index=X_train.columns)
    feat_importances.nlargest(20).sort_values().plot(kind='barh')
    plt.title("CatBoost Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    # plt.show() 대신 파일로 저장
    plt.savefig('feature_importance.png')
    print("\n피처 중요도 그래프가 'feature_importance.png' 파일로 저장되었습니다.")

else:
    print('데이터프레임이 비어있어 스크립트를 실행할 수 없습니다.')

# f1_score 0.8382