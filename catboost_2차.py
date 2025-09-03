import pandas as pd
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier  # CatBoost 라이브러리 임포트
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
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['arrival_date_month'] = df['arrival_date_month'].map(month_map)

    # CatBoost는 Label Encoding 없이 object 타입을 직접 처리할 수 있습니다.
    # 범주형 데이터 컬럼명을 리스트로 저장합니다.
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    # 혹시 모를 오류 방지를 위해 모든 범주형 컬럼을 string 타입으로 변환합니다.
    for col in categorical_cols:
        df[col] = df[col].astype(str)

    # ===================================================================
    # 3. 데이터 분리 (전처리 완료 후 수행)
    # ===================================================================
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # ===================================================================
    # 4. 모델 학습 및 평가
    # ===================================================================
    
    # 모델 학습
    # cat_features 파라미터에 범주형 피처 컬럼명 리스트를 전달합니다.
    # verbose=0 옵션으로 학습 과정을 출력하지 않도록 설정합니다.
    model = CatBoostClassifier(random_state=42,
                            cat_features=categorical_cols,
                            verbose=0)
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

# f1-score 0.8381