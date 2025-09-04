'''
cross validation : 데이터를 나누어 여러번 학습하는 방법
- StratifiedKFold : 분류문제에서 사용
- KFold : 회귀문제에서 사용
-> 1) 과적합 탐지
-> 2) 하이퍼 파라미터 튜닝
-> 3) 모델 성능 확인
'''

import logging
from sklearn.model_selection import StratifiedKFold, KFold
from .metrics import Metrics_Type


def create_cv(n_splits:int=5, shuffle:bool=True):
    return StratifiedKFold(n_splits=n_splits, shuffle=shuffle)


def do_training_with_cv(model, cv, df_train, df_trian_target
                        , metrics_type:Metrics_Type) -> float:
    scores = 0.0 # 평가지표 점수 초기값 설정
    for _ , (train_index, valid_index) in enumerate(cv.split(df_train, df_trian_target)):  #enumerate()로 현재 몇 번째 폴드인지 추적
        # 학습용 데이터 -> features, targets
        tr_features, tr_targets = df_train.iloc[train_index], df_trian_target.iloc[train_index]
        # 평가용 데이터 -> features, targets
        te_features, te_targets = df_train.iloc[valid_index], df_trian_target.iloc[valid_index]
        # 모델 학습
        model.fit(tr_features, tr_targets)
        # 평가
        predictions = model.predict_proba(te_features)[:,1] ## predict_proba: 확률로 리턴 / predict: 정수로 리턴
        scores += metrics_type.value[1](te_targets, predictions)

    return scores / cv.n_splits # 평가지표 점수 평균


