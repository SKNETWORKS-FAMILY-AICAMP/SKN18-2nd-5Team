import logging
from sklearn.metrics import f1_score, roc_auc_score
from .model import create_model
from .cross_validation import do_training_with_cv, create_cv
from .metrics import Metrics_Type



def do_training(df_train, df_trian_target, args) -> bool:
    result = None
    model = create_model(model_name=args.model_name, hp=args.hp)
    score_by_cv =do_training_with_cv(
        model, create_cv(), df_train, df_trian_target,
        Metrics_Type.roc_auc_score)
    logging.info(f"score_by_cv: {score_by_cv}")

    if score_by_cv >= 0.7:
        result = model
    
    return result

