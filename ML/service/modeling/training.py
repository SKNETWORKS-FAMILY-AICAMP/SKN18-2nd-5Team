from typing import Any


def train_xgb_classifier(
    X, y, random_state=42,
    max_depth=11,  # F1 최적화: 9 → 11 (더 깊은 트리)
    learning_rate=0.005,  # F1 최적화: 0.01 → 0.005 (더 세밀한 학습)
    n_estimators=3000,  # F1 최적화: 1500 → 3000 (더 많은 학습)
    subsample=0.7,  # F1 최적화: 0.8 → 0.7 (과적합 방지 강화)
    colsample_bytree=0.7,  # F1 최적화: 0.8 → 0.7 (과적합 방지 강화)
    colsample_bylevel=0.7,  # F1 최적화: 0.8 → 0.7 (과적합 방지 강화)
    colsample_bynode=0.7,  # F1 최적화: 0.8 → 0.7 (과적합 방지 강화)
    scale_pos_weight=5.0,  # F1 최적화: 3.0 → 5.0 (클래스 불균형 처리 강화)
    reg_alpha=0.2,  # F1 최적화: 0.1 → 0.2 (L1 정규화 강화)
    reg_lambda=2.0,  # F1 최적화: 1.0 → 2.0 (L2 정규화 강화)
    min_child_weight=2,  # F1 최적화: 3 → 2 (분할 허용 증가)
    gamma=0.05  # F1 최적화: 0.1 → 0.05 (분할 최소 이득 감소)
) -> Any:
    from .model import build_xgb_classifier
    model = build_xgb_classifier(
        random_state=random_state,
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        colsample_bylevel=colsample_bylevel,
        colsample_bynode=colsample_bynode,
        scale_pos_weight=scale_pos_weight,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        min_child_weight=min_child_weight,
        gamma=gamma
    )
    model.fit(X, y)
    return model


def train_random_forest_classifier(X, y, random_state=42) -> Any:
    """RandomForest 분류기 학습"""
    from .model import build_random_forest_classifier
    model = build_random_forest_classifier(random_state=random_state)
    model.fit(X, y)
    return model


def train_lightgbm_classifier(X, y, random_state=42) -> Any:
    """LightGBM 분류기 학습"""
    from .model import build_lightgbm_classifier
    model = build_lightgbm_classifier(random_state=random_state)
    model.fit(X, y)
    return model


def train_catboost_classifier(X, y, random_state=42) -> Any:
    """CatBoost 분류기 학습"""
    from .model import build_catboost_classifier
    model = build_catboost_classifier(random_state=random_state)
    model.fit(X, y)
    return model


def train_all_models(X, y, random_state=42) -> dict:
    """모든 모델을 학습하고 결과 반환"""
    models = {}
    
    print("🌳 XGBoost 학습 중...")
    models['XGBoost'] = train_xgb_classifier(X, y, random_state)
    
    print("🌲 RandomForest 학습 중...")
    models['RandomForest'] = train_random_forest_classifier(X, y, random_state)
    
    print("💡 LightGBM 학습 중...")
    models['LightGBM'] = train_lightgbm_classifier(X, y, random_state)
    
    print("🐱 CatBoost 학습 중...")
    models['CatBoost'] = train_catboost_classifier(X, y, random_state)
    
    return models


