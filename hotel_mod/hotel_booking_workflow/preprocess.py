from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass
class DataSplit:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['company'] = df['company'].fillna(0)
    df['agent'] = df['agent'].fillna(0)
    df['children'] = df['children'].fillna(0)
    df['country'] = df['country'].fillna(df['country'].mode()[0])
    return df


def basic_train_test_split(df: pd.DataFrame, random_state: int = 42) -> DataSplit:
    X = df.drop([
        'is_canceled', 'reservation_status', 'reservation_status_date',
        'deposit_type', 'agent', 'assigned_room_type'
    ], axis=1)
    y = df['is_canceled']
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    return DataSplit(X_tr, X_te, y_tr, y_te)


def add_total_guests_and_is_alone(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    for X in (X_tr, X_te):
        X['total_guests'] = X['adults'] + X['children'] + X['babies']
        X['is_alone'] = (X['total_guests'] == 1).astype(int)
        X.drop(columns=['total_guests'], inplace=True)
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def add_has_company(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    for X in (X_tr, X_te):
        X['has_company'] = (X['company'] > 0).astype(int)
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def add_is_FB_meal(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    for X in (X_tr, X_te):
        X['is_FB_meal'] = np.where(X['meal'] == 'FB', 1, 0)
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def process_adr_iqr(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    Q1 = X_tr['adr'].quantile(0.25)
    Q3 = X_tr['adr'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    lower_bound = Q1 - 1.5 * IQR
    adr_filtered_median = X_tr.loc[
        (X_tr['adr'] >= lower_bound) & (X_tr['adr'] <= upper_bound), 'adr'
    ].median()
    for X in (X_tr, X_te):
        X['adr_processed'] = np.where(
            (X['adr'] < lower_bound) | (X['adr'] > upper_bound),
            adr_filtered_median,
            X['adr']
        )
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def add_total_stay(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    for X in (X_tr, X_te):
        X['total_stay'] = X['stays_in_weekend_nights'] + X['stays_in_week_nights']
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def process_lead_time(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    lead_time_median = X_tr['lead_time'].median()
    for X in (X_tr, X_te):
        X['lead_time_processed'] = np.where(
            (X['lead_time'] < 0) | (X['lead_time'] > 373),
            lead_time_median,
            X['lead_time']
        )
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def map_hotel_type(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    for X in (X_tr, X_te):
        X['is_resort'] = X['hotel'].map({'City Hotel': 0, 'Resort Hotel': 1})
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def one_hot_encode_and_align(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    cat_cols = X_tr.select_dtypes(include='object').columns.tolist()
    if len(cat_cols) > 0:
        X_tr = pd.get_dummies(X_tr, columns=cat_cols, drop_first=True)
        X_te = pd.get_dummies(X_te, columns=cat_cols, drop_first=True)
        X_te = X_te.reindex(columns=X_tr.columns, fill_value=0)
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def drop_original_columns(split: DataSplit) -> DataSplit:
    X_tr = split.X_train.copy()
    X_te = split.X_test.copy()
    columns_to_drop = [
        'hotel', 'lead_time', 'adr', 'stays_in_weekend_nights',
        'stays_in_week_nights', 'total_guests', 'reserved_room_type',
        'assigned_room_type', 'customer_type'
    ]
    X_tr.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    X_te.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    return DataSplit(X_tr, X_te, split.y_train, split.y_test)


def pipeline(df: pd.DataFrame, random_state: int = 42) -> DataSplit:
    df2 = fill_missing_values(df)
    split = basic_train_test_split(df2, random_state=random_state)
    split = add_total_guests_and_is_alone(split)
    split = add_has_company(split)
    split = add_is_FB_meal(split)
    split = process_adr_iqr(split)
    split = add_total_stay(split)
    split = process_lead_time(split)
    split = map_hotel_type(split)
    split = one_hot_encode_and_align(split)
    split = drop_original_columns(split)
    return split


