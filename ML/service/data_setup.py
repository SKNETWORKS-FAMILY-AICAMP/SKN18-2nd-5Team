import os
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split


def load_raw_csv(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def load_train_csv(csv_path: str) -> Tuple[pd.DataFrame, pd.Series]:
    """준비된 train CSV 파일을 로드하고 X, y로 분리"""
    df = pd.read_csv(csv_path)
    X = df.drop('is_canceled', axis=1)
    y = df['is_canceled']
    return X, y


def load_test_csv(csv_path: str) -> pd.DataFrame:
    """타겟이 없는 test CSV 파일 로드"""
    return pd.read_csv(csv_path)


def split_train_validation(X: pd.DataFrame, y: pd.Series, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Train 데이터를 train/validation으로 분할"""
    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    return X_tr, X_val, y_tr, y_val


def train_test_from_raw(df: pd.DataFrame, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """원본 데이터에서 train/test 분할 (기존 함수 유지)"""
    X = df.drop([
        'is_canceled', 'reservation_status', 'reservation_status_date',
        'deposit_type', 'agent', 'assigned_room_type'
    ], axis=1)
    y = df['is_canceled']
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    return X_tr, X_te, y_tr, y_te


