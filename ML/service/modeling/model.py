import xgboost as xgb


def build_xgb_classifier(random_state: int = 42) -> xgb.XGBClassifier:
    return xgb.XGBClassifier(random_state=random_state, use_label_encoder=False, eval_metric='logloss')


