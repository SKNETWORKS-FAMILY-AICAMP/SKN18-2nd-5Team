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
# from service.submission import create_submission_file

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