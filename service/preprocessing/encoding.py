from typing import Tuple

import pandas as pd


def one_hot_encode_and_align(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    cat_cols = X_tr.select_dtypes(include='object').columns.tolist()
    if len(cat_cols) > 0:
        X_tr = pd.get_dummies(X_tr, columns=cat_cols, drop_first=True)
        X_te = pd.get_dummies(X_te, columns=cat_cols, drop_first=True)
        X_te = X_te.reindex(columns=X_tr.columns, fill_value=0)
    return X_tr, X_te


def drop_original_columns(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    columns_to_drop = [
        'hotel', 'lead_time', 'adr', 'stays_in_weekend_nights',
        'stays_in_week_nights', 'total_guests', 'reserved_room_type',
        'assigned_room_type', 'customer_type',
        'reservation_status',       # 예약 상태 (Check-Out, Canceled, No-Show)
        'reservation_status_date',  # 수천 개의 날짜 컬럼 생성 방지
        'arrival_date_full',        # 수천 개의 날짜 컬럼 생성 방지
        'deposit_type',             # 보증금 타입
        'agent',                    # 에이전트 ID (너무 많은 카테고리)
        'company',                  # 회사 ID (너무 많은 카테고리)
        'country',                  # 국가 (너무 많은 카테고리)
    ]
    X_tr.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    X_te.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    return X_tr, X_te


