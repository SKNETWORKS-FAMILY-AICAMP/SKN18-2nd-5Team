import xgboost as xgb


def build_xgb_classifier(
    random_state=42,
    max_depth=9,  # F1 최적화: 8→9 (0.01 향상을 위한 논리적 조정)
    learning_rate=0.05,  # F1 최적화: 0.06→0.05 (더 정밀한 학습)
    n_estimators=2000,  # F1 최적화: 1800→2000 (충분한 학습)
    subsample=0.95,  # F1 최적화: 0.9→0.95 (거의 모든 데이터 활용)
    colsample_bytree=0.95,  # F1 최적화: 0.9→0.95 (거의 모든 피처 활용)
    colsample_bylevel=0.95,  # F1 최적화: 0.9→0.95 (레벨별 거의 모든 피처)
    colsample_bynode=0.95,  # F1 최적화: 0.9→0.95 (노드별 거의 모든 피처)
    scale_pos_weight=3.3,  # F1 최적화: 3.2→3.3 (클래스 불균형 처리 미세 조정)
    reg_alpha=0.0,  # F1 최적화: 유지 (피처 활용 극대화)
    reg_lambda=0.5,  # F1 최적화: 0.6→0.5 (L2 정규화 완화로 학습 강화)
    min_child_weight=1,  # F1 최적화: 유지 (세밀한 분할)
    gamma=0.0,  # F1 최적화: 유지 (분할 제한 제거)
    early_stopping_rounds=150,  # F1 최적화: 120→150 (더 많은 학습 허용)
    eval_metric='logloss'  # F1-score 최적화를 위해 logloss 사용
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
        eval_metric=eval_metric,  # F1-score 직접 최적화
        tree_method='hist',  # 성능 최적화
        grow_policy='lossguide',  # F1-Score 최적화
        max_leaves=0,  # 무제한 리프 노드
        max_bin=512,  # 더 세밀한 분할
        objective='binary:logistic',  # 이진 분류 명시
        booster='gbtree',  # 트리 부스터 사용
        monotone_constraints=None,  # 단조성 제약 없음
        interaction_constraints=None,  # 상호작용 제약 없음
        num_parallel_tree=1,  # 병렬 트리 수
        gpu_id=-1,  # CPU 사용
        predictor='auto',  # 자동 예측기 선택
        early_stopping_rounds=early_stopping_rounds,  # 조기 종료
        enable_categorical=True,  # 추가: 범주형 변수 자동 처리
        max_cat_to_onehot=4,  # 추가: 범주형 변수 원핫인코딩 임계값
        max_cat_threshold=32,  # 추가: 범주형 변수 임계값
        sampling_method='uniform',  # 추가: 균등 샘플링
        normalize_type='tree',  # 추가: 트리 정규화
        rate_drop=0.0,  # 추가: 드롭아웃 비율
        one_drop=0,  # 추가: 드롭아웃 비율
        skip_drop=0.0,  # 추가: 스킵 드롭 비율
        feature_selector='cyclic',  # 추가: 피처 선택 방법
        top_k=0,  # 추가: 상위 K개 피처 사용
        refresh_leaf=1,  # 추가: 리프 갱신 빈도
        process_type='default',  # 추가: 처리 타입
        debug_verbose=0,  # 추가: 디버그 출력 레벨
        verbosity=0  # 추가: 출력 억제
    )




