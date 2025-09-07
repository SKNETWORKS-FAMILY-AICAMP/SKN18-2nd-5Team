import xgboost as xgb


def build_xgb_classifier(
    random_state=42,
    max_depth=5,
    learning_rate=0.05,
    n_estimators=400,
    subsample=0.9,
    colsample_bytree=0.9,
    scale_pos_weight=1.5,
    reg_alpha=0.1,
    reg_lambda=1.0
):
    from xgboost import XGBClassifier
    return XGBClassifier(
        random_state=random_state,
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        scale_pos_weight=scale_pos_weight,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        use_label_encoder=False,
        eval_metric='logloss'
    )


