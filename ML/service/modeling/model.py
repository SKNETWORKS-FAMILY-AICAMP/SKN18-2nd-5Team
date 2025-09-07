import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier


def build_xgb_classifier(
    random_state=42,
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
):
    from xgboost import XGBClassifier
    return XGBClassifier(
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
        gamma=gamma,
        use_label_encoder=False,
        eval_metric='logloss',
        tree_method='hist',  # 추가: 성능 최적화
        grow_policy='lossguide',  # 추가: F1-Score 최적화
        max_leaves=0,  # 추가: 무제한 리프 노드
        max_bin=512,  # 추가: 더 세밀한 분할
        objective='binary:logistic',  # 추가: 이진 분류 명시
        booster='gbtree',  # 추가: 트리 부스터 사용
        monotone_constraints=None,  # 추가: 단조성 제약 없음
        interaction_constraints=None,  # 추가: 상호작용 제약 없음
        num_parallel_tree=1,  # 추가: 병렬 트리 수
        gpu_id=-1,  # 추가: CPU 사용
        predictor='auto'  # 추가: 자동 예측기 선택
    )


def build_random_forest_classifier(
    random_state=42,
    n_estimators=500,  # 충분한 트리 수
    max_depth=12,  # 깊은 트리 허용
    min_samples_split=5,  # 과적합 방지
    min_samples_leaf=2,  # 과적합 방지
    max_features='sqrt',  # 랜덤성 증가
    class_weight='balanced'  # 클래스 불균형 처리
):
    """RandomForest 분류기 빌드"""
    return RandomForestClassifier(
        random_state=random_state,
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        class_weight=class_weight,
        n_jobs=-1  # 병렬 처리
    )


def build_lightgbm_classifier(
    random_state=42,
    max_depth=8,
    learning_rate=0.01,
    n_estimators=1000,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=2.5,
    reg_alpha=0.2,
    reg_lambda=1.0,
    min_child_weight=3,
    gamma=0.1
):
    """LightGBM 분류기 빌드"""
    return LGBMClassifier(
        random_state=random_state,
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        scale_pos_weight=scale_pos_weight,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        min_child_weight=min_child_weight,
        min_gain_to_split=gamma,
        class_weight='balanced',
        verbose=-1,  # 로그 출력 억제
        n_jobs=-1  # 병렬 처리
    )


def build_catboost_classifier(
    random_state=42,
    max_depth=8,
    learning_rate=0.01,
    iterations=1000,
    subsample=0.8,
    colsample_bylevel=0.8,
    scale_pos_weight=2.5,
    reg_lambda=1.0,
    min_child_samples=3,
    gamma=0.1
):
    """CatBoost 분류기 빌드"""
    return CatBoostClassifier(
        random_seed=random_state,
        max_depth=max_depth,
        learning_rate=learning_rate,
        iterations=iterations,
        subsample=subsample,
        colsample_bylevel=colsample_bylevel,
        class_weights=[1, scale_pos_weight],  # 클래스 가중치 사용
        reg_lambda=reg_lambda,
        min_child_samples=min_child_samples,
        verbose=False,  # 로그 출력 억제
        thread_count=-1  # 병렬 처리
    )


