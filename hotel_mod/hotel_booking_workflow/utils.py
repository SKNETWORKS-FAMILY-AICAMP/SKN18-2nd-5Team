from __future__ import annotations

from typing import Tuple

import xgboost as xgb


def train_xgb_classifier(X_tr, y_tr, random_state: int = 42) -> xgb.XGBClassifier:
    model = xgb.XGBClassifier(random_state=random_state, use_label_encoder=False, eval_metric='logloss')
    model.fit(X_tr, y_tr)
    return model


