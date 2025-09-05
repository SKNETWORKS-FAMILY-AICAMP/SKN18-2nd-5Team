from typing import Tuple

import numpy as np
import pandas as pd


def add_total_guests_and_is_alone(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    for X in (X_tr, X_te):
        X['total_guests'] = X['adults'] + X['children'] + X['babies']
        X['is_alone'] = (X['total_guests'] == 1).astype(int)
        X.drop(columns=['total_guests'], inplace=True)
    return X_tr, X_te


def add_has_company(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    for X in (X_tr, X_te):
        X['has_company'] = (X['company'] > 0).astype(int)
    return X_tr, X_te


def add_is_FB_meal(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    for X in (X_tr, X_te):
        X['is_FB_meal'] = np.where(X['meal'] == 'FB', 1, 0)
    return X_tr, X_te


def process_adr_iqr(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    Q1 = X_tr['adr'].quantile(0.25)
    Q3 = X_tr['adr'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    lower_bound = Q1 - 1.5 * IQR
    adr_filtered_median = X_tr.loc[(X_tr['adr'] >= lower_bound) & (X_tr['adr'] <= upper_bound), 'adr'].median()
    for X in (X_tr, X_te):
        X['adr_processed'] = np.where(
            (X['adr'] < lower_bound) | (X['adr'] > upper_bound),
            adr_filtered_median,
            X['adr']
        )
    return X_tr, X_te


def add_total_stay(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    for X in (X_tr, X_te):
        X['total_stay'] = X['stays_in_weekend_nights'] + X['stays_in_week_nights']
    return X_tr, X_te


def process_lead_time(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    lead_time_median = X_tr['lead_time'].median()
    for X in (X_tr, X_te):
        X['lead_time_processed'] = np.where(
            (X['lead_time'] < 0) | (X['lead_time'] > 373),
            lead_time_median,
            X['lead_time']
        )
    return X_tr, X_te


def map_hotel_type(X_tr: pd.DataFrame, X_te: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_tr = X_tr.copy()
    X_te = X_te.copy()
    for X in (X_tr, X_te):
        X['is_resort'] = X['hotel'].map({'City Hotel': 0, 'Resort Hotel': 1})
    return X_tr, X_te


