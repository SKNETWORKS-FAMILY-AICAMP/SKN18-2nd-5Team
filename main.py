import warnings
warnings.filterwarnings('ignore')  # 경고 메시지 무시
import logging
logging.basicConfig(level=logging.INFO)  # 메인파일에서 2개줄 다 쓰면 다른 파일에서는 첫번째 
## 로깅 레벨 설정. 로깅이란 코드 실행 중 발생하는 이벤트를 기록하는 것. print()보다 깔끔하고 메모리낭비가 없음. 현업에서 많이 사용함.
## INFO : logging.info() 출력, ERROR : logging.info()가 출력되지 않게 함

import argparse # 터미널에서 인자를 입력하는대로 출력하게 하는 라이브러리
import time
from datetime import datetime

##########
# 코드 정의 영역
##########
# import 뒤에는 함수 또는 클래스만 작성
# from 뒤에는 폴더.파일명 작성

from service.data_setup import do_load_dataset
from service.preprocessing.adata_preprocessing import do_preprocessing
from service.modeling.training import do_training
from service.modeling.model import Model_Type
import json
import os
# from service.submission import create_submission_file

def create_final_comparison_report(successful_models):
    """모든 모델의 성능을 비교하는 최종 보고서 생성"""
    
    model_performances = []
    
    # 각 모델의 보고서에서 성능 데이터 수집
    for model_name in successful_models:
        report_file = f"reports/{model_name}_report.json"
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
                
            model_performances.append({
                'model_name': model_name,
                'test_f1_score': report['test_performance']['test_f1_score'],
                'test_accuracy': report['test_performance']['test_accuracy'],
                'test_roc_auc': report['test_performance']['test_roc_auc'],
                'cv_f1_score': report['cross_validation']['cv_f1_score'],
                'cv_accuracy': report['cross_validation']['cv_accuracy'],
                'cv_roc_auc': report['cross_validation']['cv_roc_auc'],
                'training_time': report['model_details']['training_time']
            })
    
    # F1 스코어 기준으로 내림차순 정렬
    model_performances.sort(key=lambda x: x['test_f1_score'], reverse=True)
    
    # 최종 비교 보고서 생성
    final_report = {
        "report_type": "final_model_comparison",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_models": len(model_performances),
        "ranking_criteria": "test_f1_score",
        "model_rankings": []
    }
    
    # 순위별 모델 정보 추가
    for rank, model_perf in enumerate(model_performances, 1):
        final_report["model_rankings"].append({
            "rank": rank,
            "model_name": model_perf['model_name'],
            "test_f1_score": model_perf['test_f1_score'],
            "test_accuracy": model_perf['test_accuracy'], 
            "test_roc_auc": model_perf['test_roc_auc'],
            "cv_f1_score": model_perf['cv_f1_score'],
            "training_time": model_perf['training_time']
        })
    
    # 최고 성능 모델 정보
    if model_performances:
        best_model = model_performances[0]
        final_report["best_model"] = {
            "name": best_model['model_name'],
            "test_f1_score": best_model['test_f1_score'],
            "improvement_over_worst": round(best_model['test_f1_score'] - model_performances[-1]['test_f1_score'], 4) if len(model_performances) > 1 else 0
        }
    
    # JSON 파일로 저장
    final_report_file = "reports/final_model_comparison.json"
    with open(final_report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    # 표 형태로 콘솔 출력
    logging.info("="*60)
    logging.info("🏆 최종 모델 성능 비교 (F1-Score 기준)")
    logging.info("="*60)
    logging.info("Model                     F1-Score   Accuracy   ROC-AUC    Time      Type")
    logging.info("="*84)
    
    # 각 모델별로 CV, Test, Diff 3줄씩 출력
    for rank, model_perf in enumerate(model_performances, 1):
        model_name = model_perf['model_name'].capitalize()
        
        # CV 성능
        logging.info(f"{model_name:<25} {model_perf['cv_f1_score']:<10.4f} {model_perf['cv_accuracy']:<10.4f} {model_perf['cv_roc_auc']:<10.4f} {model_perf['training_time']:<9} CV")
        
        # Test 성능  
        logging.info(f"{'':25} {model_perf['test_f1_score']:<10.4f} {model_perf['test_accuracy']:<10.4f} {model_perf['test_roc_auc']:<10.4f} {'-':<9} Test")
        
        # 차이값 (Test - CV)
        f1_diff = model_perf['test_f1_score'] - model_perf['cv_f1_score']
        acc_diff = model_perf['test_accuracy'] - model_perf['cv_accuracy']
        auc_diff = model_perf['test_roc_auc'] - model_perf['cv_roc_auc']
        
        logging.info(f"{'':25} {f1_diff:<10.4f} {acc_diff:<10.4f} {auc_diff:<10.4f} {'-':<9} Diff")
        logging.info("-"*84)
    
    # CV-Test 차이 분석 (일반화 성능)
    logging.info("")
    logging.info("="*60)
    logging.info("📊 CV-Test 성능 차이 분석 (일반화 성능)")
    logging.info("="*60)
    logging.info("Rank  Model               F1_Diff    Acc_Diff   AUC_Diff   Overall_Diff")
    logging.info("="*84)
    
    # 일반화 성능 순으로 정렬 (차이가 작을수록 좋음)
    generalization_ranking = []
    for model_perf in model_performances:
        f1_diff = model_perf['test_f1_score'] - model_perf['cv_f1_score']
        acc_diff = model_perf['test_accuracy'] - model_perf['cv_accuracy']
        auc_diff = model_perf['test_roc_auc'] - model_perf['cv_roc_auc']
        overall_diff = (abs(f1_diff) + abs(acc_diff) + abs(auc_diff)) / 3
        
        generalization_ranking.append({
            'model_name': model_perf['model_name'],
            'f1_diff': f1_diff,
            'acc_diff': acc_diff,
            'auc_diff': auc_diff, 
            'overall_diff': overall_diff
        })
    
    # 일반화 성능 순으로 정렬 (차이가 작을수록 상위)
    generalization_ranking.sort(key=lambda x: abs(x['overall_diff']))
    
    for rank, gen_perf in enumerate(generalization_ranking, 1):
        medal = "🏆" if rank == 1 else ""
        logging.info(f"{rank}위   {gen_perf['model_name'].capitalize():<15} {gen_perf['f1_diff']:<10.4f} {gen_perf['acc_diff']:<10.4f} {gen_perf['auc_diff']:<10.4f} {gen_perf['overall_diff']:<10.4f} {medal}")
    
    logging.info("="*84)
    
    # 종합 분석
    logging.info("")
    logging.info("="*60)
    logging.info("🎯 종합 분석 결과")
    logging.info("="*60)
    
    if model_performances:
        best_performance = model_performances[0]
        fastest_model = min(model_performances, key=lambda x: float(x['training_time'].replace(' seconds', '')))
        most_stable = generalization_ranking[0]
        avg_diff = sum([g['overall_diff'] for g in generalization_ranking]) / len(generalization_ranking)
        
        logging.info(f"🥇 최고 테스트 성능:     {best_performance['model_name'].upper():<12} (F1: {best_performance['test_f1_score']:.4f})")
        logging.info(f"⚡ 가장 빠른 학습:       {fastest_model['model_name'].upper():<12} (Time: {fastest_model['training_time']})")
        logging.info(f"🎨 가장 안정적 모델:     {most_stable['model_name'].upper():<12} (Overall Diff: {most_stable['overall_diff']:.4f})")
        logging.info(f"📈 평균 일반화 차이:     {avg_diff:.4f}      (CV-Test 성능 차이)")
        
        logging.info("")
        logging.info("="*60)
        logging.info(f"🏆 최종 추천 모델: {best_performance['model_name'].upper()}")
        logging.info(f"   ✅ 이유: 최고 테스트 성능 + 상대적 안정성")
        logging.info(f"   📊 Test F1-Score: {best_performance['test_f1_score']:.4f}")
        logging.info(f"   🎯 CV-Test 차이: {most_stable['overall_diff']:.4f}")
        logging.info("="*60)
        
    logging.info(f"📊 최종 비교 보고서 저장: {final_report_file}")
    logging.info("="*60)
    
    return final_report

def main(args):
    # 전체 실행 시작 시간
    total_start_time = time.time()
    
    logging.info("="*50)
    logging.info("🏨 호텔 예약 취소 예측 모델 - 전체 모델 실행 시작")
    logging.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*50)
    
    # 1. 데이터 로드 (한 번만 수행)
    logging.info("📊 데이터 로드 시작...")
    data_start_time = time.time()
    x_tr, x_te, y_tr, y_te = do_load_dataset(
        train_path=args.path_train, test_path=args.path_test
        , target_name=args.target_name)
    data_time = time.time() - data_start_time
    logging.info(f"✅ 데이터 로드 완료 (소요시간: {data_time:.2f}초)")

    # 2. 데이터 전처리는 각 모델별로 수행 (모델별로 인코딩 방식이 다름)
    logging.info("🔧 모델별 데이터 전처리 및 학습 시작...")

    # 3. 빠른 모델들만 선택해서 순차 실행
    fast_model_names = ['gradient_boosting', 'extra_trees', 'xgboost', 'random_forest', 
                       'lightgbm', 'logistic_regression', 'naive_bayes']
    successful_models = []
    failed_models = []
    
    logging.info(f"🤖 총 {len(fast_model_names)}개 빠른 모델 학습 시작...")
    logging.info("⚡ 실행 모델: Gradient Boosting, Extra Trees, XGBoost, Random Forest, LightGBM, Logistic Regression, Naive Bayes")
    logging.info("-" * 50)
    
    for i, model_name in enumerate(fast_model_names, 1):
        try:
            logging.info(f"[{i}/{len(fast_model_names)}] {model_name.upper()} 모델 학습 시작...")
            model_start_time = time.time()
            
            # 모델별 데이터 전처리
            x_tr_processed, x_te_processed = do_preprocessing(
                df_train=x_tr, df_test=x_te, 
                drop_cols=args.drop_cols, encoding_cols=args.encoding_cols, 
                model_name=model_name
            )
            
            # 모델 학습
            is_model = do_training(df_train=x_tr_processed, df_train_target=y_tr, 
                                 df_test=x_te_processed, df_test_target=y_te, model_name=model_name)
            
            model_time = time.time() - model_start_time
            
            if is_model:
                predictions = is_model.predict_proba(x_te_processed)[:,1]
                successful_models.append(model_name)
                logging.info(f"✅ {model_name.upper()} 모델 훈련이 끝났습니다 (소요시간: {model_time:.2f}초)")
            else:
                failed_models.append(model_name)
                logging.info(f"❌ {model_name.upper()} 모델 훈련 실패 (소요시간: {model_time:.2f}초)")
                
        except Exception as e:
            model_time = time.time() - model_start_time
            failed_models.append(model_name)
            logging.error(f"❌ {model_name.upper()} 모델 훈련 중 오류 발생: {str(e)} (소요시간: {model_time:.2f}초)")
        
        logging.info("-" * 30)
    
    # 전체 실행 결과 요약
    total_time = time.time() - total_start_time
    logging.info("="*50)
    logging.info("🎉 전체 모델 실행 완료!")
    logging.info(f"총 소요시간: {total_time:.2f}초")
    logging.info(f"성공한 모델: {len(successful_models)}개")
    logging.info(f"실패한 모델: {len(failed_models)}개")
    
    if successful_models:
        logging.info(f"✅ 성공 모델 목록: {', '.join([m.upper() for m in successful_models])}")
    
    if failed_models:
        logging.info(f"❌ 실패 모델 목록: {', '.join([m.upper() for m in failed_models])}")
    
    logging.info("📁 성능 보고서는 reports/ 폴더에 저장되었습니다.")
    
    # 최종 모델 성능 비교 보고서 생성
    if successful_models:
        create_final_comparison_report(successful_models)
    
    logging.info("="*50)



if __name__ == "__main__":
    ###############################
    # 코드 실행 영역 
    ###############################
    args = argparse.ArgumentParser() # 
    args.add_argument("--path_train", default="./data/hotel_bookings_train.csv", type=str)
    args.add_argument("--path_test", default="./data/hotel_bookings_test.csv", type=str)
    #args.add_argument("--path_submission", default="./data/submission.csv", type=str)
    args.add_argument("--target_name", default="is_canceled", type=str) 
    # eda 분석 결과
    args.add_argument("--drop_cols", default=[
        'deposit_type', 'company' ,'agent','reservation_status', 'reservation_status_date'
        , 'assigned_room_type', 'children', 'babies', 'arrival_date_full'], type=list)
    # args.add_argument("--transform_cols", default=['adr', 'lead_time', 'total_stays'], type=list)
    args.add_argument("--encoding_cols", default=['hotel', 'arrival_date_month', 'meal', 'country', 'market_segment', 'distribution_channel', 'reserved_room_type', 'customer_type', 'market_risk_level'], type=list)


    main(args.parse_args()) 