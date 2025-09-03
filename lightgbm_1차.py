import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import lightgbm as lgb
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

def ML_modeling():

    # 데이터 불러오기
    df = pd.read_csv("data/hotel_bookings.csv")
    
    # 데이터 전처리
    print(df.shape)
    print(df.info())
    print(df.describe())

    df.drop(['reservation_status', 'reservation_status_date'], axis=1,inplace=True)
    df[['company', 'agent']] = df[['company', 'agent']].fillna(0)
    df['children'] = df['children'].fillna(df['children'].median())
    df['country'] = df['country'].fillna(df['country'].mode()[0])

    # 범주형 데이터 인코딩
    categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])
        df[col] = df[col].astype('category')

    # 데이터 분리
    X = df.drop("is_canceled", axis=1)
    y = df["is_canceled"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

    # 모델 학습
    model = lgb.LGBMClassifier(random_state=42)
    model.fit(X_train, y_train)

    # 예측
    y_pred = model.predict(X_test)

    # 평가
    print("F1 Score:", f1_score(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

if __name__ == "__main__":
    
    ML_modeling()

# f1-score 0.8366