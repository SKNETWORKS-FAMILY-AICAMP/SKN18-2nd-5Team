import pandas as pd


def do_encoding(df_train:pd.DataFrame, df_test:pd.DataFrame, encoding_cols:list):
    
    for col in encoding_cols:
        df_train[col] = df_train[col].astype('category')
        df_test[col] = df_test[col].astype('category')
    
    return df_train, df_test


    ###### 라이트GBM 기준
    # 타입을 카테고리로 바꿔만 줘도 알아서 학습함. 
    # 그래서 라이트GBM은 캣부스트 등의 인코딩객체를 선언하지 않아도 됨 