import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

def ML_modeling():

    # 1. 데이터 불러오기
    df = pd.read_csv("data/hotel_bookings.csv")

    # ===================================================================
    # 2. 데이터 전처리 및 피처 엔지니어링 (데이터 분리 전 수행)
    # ===================================================================

    # 불필요한 컬럼 및 결측치 처리
    # reservation_status는 is_canceled와 직접적인 관련이 있어 타겟 유출(data leakage)을 일으킬 수 있으므로 제거합니다.
    df = df.drop(['reservation_status', 'reservation_status_date'], axis=1)
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 총 숙박일수 (total_stays)
    df['total_stays'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']

    # 총 방문객 수 (total_guests)
    df['total_guests'] = df['adults'] + df['children'] + df['babies']

    # 가족 단위 여부 (is_family)
    df['is_family'] = (df['total_guests'] > 1).astype(int)

    # 어린이 동반 여부 (has_children)
    df['has_children'] = ((df['children'] > 0) | (df['babies'] > 0)).astype(int)
    
    # arrival_date 관련 피처 생성 후 원본 컬럼 삭제
    # 월 이름을 숫자로 매핑
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['arrival_date_month'] = df['arrival_date_month'].map(month_map)

    # 범주형 데이터 인코딩 (Label Encoding)
    # LightGBM은 category 타입의 피처를 효율적으로 처리할 수 있습니다.
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])
        # category 타입으로 변환
        df[col] = df[col].astype('category')

    # ===================================================================
    # 3. 데이터 분리 (전처리 완료 후 수행)
    # ===================================================================
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y) # stratify 추가

    # ===================================================================
    # 4. 모델 학습 및 평가
    # ===================================================================
    
    # 모델 학습
    # categorical_feature='auto' (기본값)를 통해 category 타입 피처를 자동으로 인식합니다.
    model = lgb.LGBMClassifier(random_state=42)
    model.fit(X_train, y_train)

    # 예측
    y_pred = model.predict(X_test)

    # 평가
    print("F1 Score:", f1_score(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

if __name__ == "__main__":
    ML_modeling()

# f1-score 0.8291