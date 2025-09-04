from typing import Any

from .model import build_xgb_classifier


def train_xgb_classifier(X_tr, y_tr, random_state: int = 42) -> Any:
    model = build_xgb_classifier(random_state=random_state)
    model.fit(X_tr, y_tr)
    return model


