from typing import Dict, Any

import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate

from .model import build_xgb_classifier


def stratified_cv_scores(
    X, y, random_state: int = 42, n_splits: int = 5,
    max_depth: int = 5, learning_rate: float = 0.1, n_estimators: int = 200,
    subsample: float = 0.8, colsample_bytree: float = 0.8, scale_pos_weight: float = 1.0
) -> Dict[str, Any]:
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    model = build_xgb_classifier(
        random_state=random_state,
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        scale_pos_weight=scale_pos_weight
    )
    scoring = {
        'accuracy': 'accuracy',
        'precision': 'precision',
        'recall': 'recall',
        'f1': 'f1',
        'roc_auc': 'roc_auc',
    }
    results = cross_validate(model, X, y, cv=cv, scoring=scoring, return_train_score=False)
    summary = {metric: float(np.mean(vals)) for metric, vals in results.items() if metric.startswith('test_')}
    return summary

