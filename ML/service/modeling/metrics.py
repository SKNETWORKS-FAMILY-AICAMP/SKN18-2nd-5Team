from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


@dataclass
class Metrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc: float


def evaluate_binary(y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> Metrics:
    return Metrics(
        accuracy=accuracy_score(y_true, y_pred),
        precision=precision_score(y_true, y_pred),
        recall=recall_score(y_true, y_pred),
        f1=f1_score(y_true, y_pred),
        auc=roc_auc_score(y_true, y_proba),
    )


def format_metrics(title: str, m: Metrics) -> str:
    return (
        f"{title}\n"
        f"  정확도 (Accuracy): {m.accuracy:.4f}\n"
        f"  정밀도 (Precision): {m.precision:.4f}\n"
        f"  재현율 (Recall): {m.recall:.4f}\n"
        f"  F1-점수 (F1-Score): {m.f1:.4f}\n"
        f"  AUC: {m.auc:.4f}"
    )
