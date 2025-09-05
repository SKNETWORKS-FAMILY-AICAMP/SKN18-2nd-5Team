import os
import sys

import pandas as pd

# Ensure current directory is importable
sys.path.insert(0, os.getcwd())

from service.data_setup import load_raw_csv, train_test_from_raw
from service.preprocessing.cleansing import fill_missing_values
from service.preprocessing.featureExtraction import (
    add_total_guests_and_is_alone,
    add_has_company,
    add_is_FB_meal,
    process_adr_iqr,
    add_total_stay,
    process_lead_time,
    map_hotel_type,
)
from service.preprocessing.encoding import one_hot_encode_and_align, drop_original_columns
from service.modeling.training import train_xgb_classifier
from service.modeling.metrics import evaluate_binary, format_metrics


def main() -> None:
    data_dir = os.path.join('data')
    train_path = os.path.join(data_dir, 'hotel_bookings_train.csv')
    test_path = os.path.join(data_dir, 'hotel_bookings_test.csv')

    if not (os.path.exists(train_path) and os.path.exists(test_path)):
        # Fallback: build from original CSV if split files do not exist
        raw_path = os.path.join('archive', 'hotel_bookings.csv')
        df = load_raw_csv(raw_path)
        df = fill_missing_values(df)
        X_tr, X_te, y_tr, y_te = train_test_from_raw(df, random_state=42)
    else:
        # Load pre-split CSVs
        df_tr = pd.read_csv(train_path)
        df_te = pd.read_csv(test_path)
        y_tr = df_tr['is_canceled']
        y_te = df_te['is_canceled']
        X_tr = df_tr.drop('is_canceled', axis=1)
        X_te = df_te.drop('is_canceled', axis=1)

    # Feature engineering pipeline
    X_tr, X_te = add_total_guests_and_is_alone(X_tr, X_te)
    X_tr, X_te = add_has_company(X_tr, X_te)
    X_tr, X_te = add_is_FB_meal(X_tr, X_te)
    X_tr, X_te = process_adr_iqr(X_tr, X_te)
    X_tr, X_te = add_total_stay(X_tr, X_te)
    X_tr, X_te = process_lead_time(X_tr, X_te)
    X_tr, X_te = map_hotel_type(X_tr, X_te)

    # Encoding and alignment
    X_tr, X_te = one_hot_encode_and_align(X_tr, X_te)
    X_tr, X_te = drop_original_columns(X_tr, X_te)

    # Train and evaluate
    model = train_xgb_classifier(X_tr, y_tr, random_state=42)
    y_tr_pred = model.predict(X_tr)
    y_te_pred = model.predict(X_te)
    y_tr_proba = model.predict_proba(X_tr)[:, 1]
    y_te_proba = model.predict_proba(X_te)[:, 1]

    print(format_metrics('XGBoost 훈련 성능:', evaluate_binary(y_tr, y_tr_pred, y_tr_proba)))
    print()
    print(format_metrics('XGBoost 테스트 성능:', evaluate_binary(y_te, y_te_pred, y_te_proba)))


if __name__ == '__main__':
    main()


