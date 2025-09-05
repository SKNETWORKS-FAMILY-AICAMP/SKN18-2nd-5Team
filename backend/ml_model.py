"""
호텔 예약 취소 예측 머신러닝 모델
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

class CancellationPredictor:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_columns = []
        self.categorical_columns = [
            'hotel', 'meal', 'country', 'market_segment', 
            'distribution_channel', 'reserved_room_type', 
            'assigned_room_type', 'deposit_type', 'customer_type'
        ]
        self.numerical_columns = [
            'lead_time', 'stays_in_weekend_nights', 'stays_in_week_nights',
            'adults', 'children', 'babies', 'is_repeated_guest',
            'previous_cancellations', 'previous_bookings_not_canceled',
            'booking_changes', 'days_in_waiting_list', 'adr',
            'required_car_parking_spaces', 'total_of_special_requests'
        ]
        
    def preprocess_data(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """데이터 전처리"""
        df = df.copy()
        
        # NULL 값 처리
        df['children'] = df['children'].fillna(0)
        df['country'] = df['country'].fillna('Unknown')
        df['agent'] = df['agent'].fillna(0)
        df['company'] = df['company'].fillna(0)
        
        # 카테고리 변수 인코딩
        for col in self.categorical_columns:
            if col in df.columns:
                if is_training:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                        # Unknown 값을 위한 처리
                        unique_values = df[col].unique().tolist()
                        unique_values.append('Unknown')
                        self.label_encoders[col].fit(unique_values)
                
                # 인코딩 적용
                df[col] = df[col].apply(lambda x: x if x in self.label_encoders[col].classes_ else 'Unknown')
                df[col + '_encoded'] = self.label_encoders[col].transform(df[col])
        
        # 추가 특징 생성
        df['total_guests'] = df['adults'] + df['children'] + df['babies']
        df['total_stay_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
        df['is_weekend_stay'] = (df['stays_in_weekend_nights'] > 0).astype(int)
        df['has_special_requests'] = (df['total_of_special_requests'] > 0).astype(int)
        df['has_parking'] = (df['required_car_parking_spaces'] > 0).astype(int)
        df['is_family'] = ((df['children'] > 0) | (df['babies'] > 0)).astype(int)
        
        # Lead time 구간화
        df['lead_time_category'] = pd.cut(df['lead_time'], 
                                          bins=[0, 7, 30, 90, 180, 365, 1000],
                                          labels=['very_short', 'short', 'medium', 'long', 'very_long', 'extreme'])
        df['lead_time_category_encoded'] = LabelEncoder().fit_transform(df['lead_time_category'])
        
        # ADR 이상치 처리
        df['adr'] = df['adr'].clip(upper=500)
        
        # 특징 선택
        feature_cols = self.numerical_columns + [col + '_encoded' for col in self.categorical_columns if col in df.columns]
        feature_cols += ['total_guests', 'total_stay_nights', 'is_weekend_stay', 
                        'has_special_requests', 'has_parking', 'is_family', 'lead_time_category_encoded']
        
        if is_training:
            self.feature_columns = [col for col in feature_cols if col in df.columns]
        
        return df[self.feature_columns] if not is_training else df
    
    def train(self, df: pd.DataFrame):
        """모델 학습"""
        print("Preprocessing data...")
        processed_df = self.preprocess_data(df, is_training=True)
        
        # 특징과 타겟 분리
        X = processed_df[self.feature_columns]
        y = df['is_canceled']
        
        # 학습/검증 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training with {len(X_train)} samples...")
        
        # 모델 학습 (Gradient Boosting 사용)
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            subsample=0.8
        )
        
        self.model.fit(X_train, y_train)
        
        # 성능 평가
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        
        # 특징 중요도
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Important Features:")
        print(feature_importance.head(10))
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def predict_single(self, booking_data: Dict) -> float:
        """단일 예약 취소 확률 예측"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # DataFrame으로 변환
        df = pd.DataFrame([booking_data])
        
        # 전처리
        processed_df = self.preprocess_data(df, is_training=False)
        
        # 예측
        cancellation_prob = self.model.predict_proba(processed_df)[0, 1]
        
        return cancellation_prob
    
    def predict_batch(self, df: pd.DataFrame) -> np.ndarray:
        """배치 예측"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # 전처리
        processed_df = self.preprocess_data(df, is_training=False)
        
        # 예측
        cancellation_probs = self.model.predict_proba(processed_df)[:, 1]
        
        return cancellation_probs
    
    def save_model(self, filepath: str):
        """모델 저장"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """모델 로드"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.categorical_columns = model_data['categorical_columns']
        self.numerical_columns = model_data['numerical_columns']
        print(f"Model loaded from {filepath}")
