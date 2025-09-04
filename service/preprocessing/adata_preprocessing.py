import pandas as pd
import logging

from .cleansing import do_cleansing
from .encoding import do_encoding
from .cleansing import do_cleansing
from .featureExtraction import do_feature_extraction



def do_preprocessing(df_train:pd.DataFrame, df_test:pd.DataFrame, drop_cols:list, encoding_cols:list, args):
    '''
    모델 학습 전 데이터 전처리 함수
    '''
    
    # 1. feature extraction 
    df_train, df_test = do_feature_extraction(df_train, df_test)

    # 2. cleansing
    df_train, df_test = do_cleansing(df_train, df_test, drop_cols)

    # 3. encoding
    df_train, df_test = do_encoding(df_train, df_test, encoding_cols, args)


    return df_train, df_test