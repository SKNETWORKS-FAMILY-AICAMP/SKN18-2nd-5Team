'''
metrics : 평가할 때 사용
- f1, accuracy, roc_auc
'''

import enum
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score, precision_score, recall_score


class Metrics_Type(enum.Enum):   # 내가 정의하는 메트릭스 타입 클래스
    roc_auc_score = (enum.auto(), roc_auc_score)
    f1_score = (enum.auto(), f1_score)
    accuracy_score = (enum.auto(), accuracy_score)
    precision_score = (enum.auto(), precision_score)
    recall_score = (enum.auto(), recall_score)

