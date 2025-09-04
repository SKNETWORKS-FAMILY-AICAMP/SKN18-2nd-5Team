import logging
import json
import os
from datetime import datetime
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score
from .model import create_model
from .cross_validation import do_training_with_cv, create_cv
from .metrics import Metrics_Type


def evaluate_all_metrics(model, cv, df_train, df_train_target):
    """모든 평가 지표로 교차 검증 수행"""
    metrics_results = {}
    
    # 각 지표별로 교차 검증 수행
    for metric_name, metric_enum in [
        ('f1_score', Metrics_Type.f1_score),
        ('accuracy_score', Metrics_Type.accuracy_score), 
        ('roc_auc_score', Metrics_Type.roc_auc_score)
    ]:
        score = do_training_with_cv(model, cv, df_train, df_train_target, metric_enum)
        metrics_results[metric_name] = score
        
    return metrics_results


def create_performance_report(model_name, cv_metrics_results, test_metrics_results, training_time):
    """성능 보고서 생성 및 저장"""
    
    # 보고서 데이터 구성
    report = {
        "model_name": model_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cross_validation": {
            "cv_f1_score": round(cv_metrics_results['f1_score'], 4),
            "cv_accuracy": round(cv_metrics_results['accuracy_score'], 4),
            "cv_roc_auc": round(cv_metrics_results['roc_auc_score'], 4)
        },
        "test_performance": {
            "test_f1_score": round(test_metrics_results['f1_score'], 4),
            "test_accuracy": round(test_metrics_results['accuracy_score'], 4),
            "test_roc_auc": round(test_metrics_results['roc_auc_score'], 4)
        },
        "model_details": {
            "training_time": f"{training_time:.2f} seconds"
        }
    }
    
    # 로깅 출력
    logging.info(f"=== {model_name.upper()} 모델 성능 보고서 ===")
    logging.info("교차 검증 결과:")
    logging.info(f"- F1-Score: {report['cross_validation']['cv_f1_score']:.4f}")
    logging.info(f"- Accuracy: {report['cross_validation']['cv_accuracy']:.4f}")
    logging.info(f"- ROC-AUC: {report['cross_validation']['cv_roc_auc']:.4f}")
    logging.info("")
    logging.info("테스트 데이터 성능:")
    logging.info(f"- F1-Score: {report['test_performance']['test_f1_score']:.4f}")
    logging.info(f"- Accuracy: {report['test_performance']['test_accuracy']:.4f}")
    logging.info(f"- ROC-AUC: {report['test_performance']['test_roc_auc']:.4f}")
    logging.info(f"학습 시간: {training_time:.2f}초")
    
    # reports 폴더 생성
    os.makedirs('reports', exist_ok=True)
    
    # JSON 파일로 저장
    report_file = f"reports/{model_name}_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logging.info(f"보고서 저장됨: {report_file}")
    logging.info("=" * 40)
    
    return report


def do_training(df_train, df_train_target, df_test, df_test_target, model_name):
    """모델 학습 및 성능 평가"""
    import time
    from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
    
    start_time = time.time()
    
    # 모델 생성
    model = create_model(model_name=model_name, hp={})
    cv = create_cv()
    
    # 교차 검증 평가
    cv_metrics_results = evaluate_all_metrics(model, cv, df_train, df_train_target)
    
    # 전체 훈련 데이터로 모델 학습
    final_model = create_model(model_name=model_name, hp={})
    final_model.fit(df_train, df_train_target)
    
    # 테스트 데이터로 성능 평가
    test_predictions_proba = final_model.predict_proba(df_test)[:,1]
    test_predictions = (test_predictions_proba >= 0.5).astype(int)
    
    test_metrics_results = {
        'f1_score': f1_score(df_test_target, test_predictions),
        'accuracy_score': accuracy_score(df_test_target, test_predictions),
        'roc_auc_score': roc_auc_score(df_test_target, test_predictions_proba)
    }
    
    training_time = time.time() - start_time
    
    # 성능 보고서 생성 (교차검증 + 테스트 결과 포함)
    report = create_performance_report(model_name, cv_metrics_results, test_metrics_results, training_time)
    
    # 로깅
    logging.info(f"모델 학습 완료 - {model_name}")
    logging.info(f"CV F1: {cv_metrics_results['f1_score']:.4f}, "
                f"CV Accuracy: {cv_metrics_results['accuracy_score']:.4f}, "
                f"CV ROC-AUC: {cv_metrics_results['roc_auc_score']:.4f}")
    logging.info(f"Test F1: {test_metrics_results['f1_score']:.4f}, "
                f"Test Accuracy: {test_metrics_results['accuracy_score']:.4f}, "
                f"Test ROC-AUC: {test_metrics_results['roc_auc_score']:.4f}")
    
    # 성능 기준 체크 (Test ROC-AUC 0.7 이상)
    if test_metrics_results['roc_auc_score'] >= 0.7:
        return final_model
    else:
        logging.info(f"⚠️ 모델 성능이 기준(Test ROC-AUC 0.7) 미달: {test_metrics_results['roc_auc_score']:.4f}")
        return None

