import warnings
warnings.filterwarnings('ignore')  # 경고 메시지 무시
import logging
logging.basicConfig(level=logging.INFO)  # 메인파일에서 2개줄 다 쓰면 다른 파일에서는 첫번째 
## 로깅 레벨 설정. 로깅이란 코드 실행 중 발생하는 이벤트를 기록하는 것. print()보다 깔끔하고 메모리낭비가 없음. 현업에서 많이 사용함.
## INFO : logging.info() 출력, ERROR : logging.info()가 출력되지 않게 함

import argparse # 터미널에서 인자를 입력하는대로 출력하게 하는 라이브러리

##########
# 코드 정의 영역
##########
# import 뒤에는 함수 또는 클래스만 작성
# from 뒤에는 폴더.파일명 작성

from service.data_setup import do_load_dataset
from service.preprocessing.adata_preprocessing import do_preprocessing
from service.modeling.training import do_training
from service.submission import create_submission_file

def main(args):
    # 1. 데이터 로드
    df_train, df_test, df_trian_target = do_load_dataset(
        train_path=args.path_train, test_path=args.path_test
        , target_name=args.target_name)

    # 2. 데이터 전처리
    df_train, df_test = do_preprocessing(df_train=df_train, df_test=df_test
    , drop_cols=args.drop_cols, transform_cols=args.transform_cols, encoding_cols=args.encoding_cols)

    # 3. 모델 학습
    is_model = do_training(df_train, df_trian_target, args)
    if is_model : # is_model 값이 모델이 있으묜(스코어가 70 이상인 경우에만 모델 적용을 하도록 해뒀으니까..!)
        predictions = is_model.predict_proba(df_test)[:,1]

    # 제출
    create_submission_file(is_model, df_test)



if __name__ == "__main__":
    ###############################
    # 코드 실행 영역 
    ###############################
    args = argparse.ArgumentParser() # 
    args.add_argument("--path_train", default="./data/hotel_bookings_train", type=str)
    args.add_argument("--path_test", default="./data/hotel_bookings_test", type=str)
    #args.add_argument("--path_submission", default="./data/submission.csv", type=str)
    args.add_argument("--target_name", default="is_canceled", type=str) 
    # eda 분석 결과
    args.add_argument("--drop_cols", default=['passengerid', 'name', 'ticket'], type=list)
    args.add_argument("--transform_cols", default=['age', 'fare'], type=list)
    args.add_argument("--encoding_cols", default=['pclass', 'gender','cabin', 'embarked'], type=list)
    args.add_argument("--model_name", default="lightgbm", type=str)
    args.add_argument("--hp", default={}, type=dict)




    main(args.parse_args()) 