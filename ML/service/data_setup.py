import os
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split


def load_raw_csv(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def train_test_from_raw(df: pd.DataFrame, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    X = df.drop([
        'is_canceled', 'reservation_status', 'reservation_status_date',
        'deposit_type', 'agent', 'assigned_room_type'
    ], axis=1)
    y = df['is_canceled']
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    return X_tr, X_te, y_tr, y_te


