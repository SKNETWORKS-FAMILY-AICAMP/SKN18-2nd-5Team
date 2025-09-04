import pandas as pd
import numpy as np


# 결측치 치환
def __fillna(df_train:pd.DataFrame, df_test:pd.DataFrame):
    # train 데이터를 기준으로 채울 값을 정하기
    # df_train.isnull() -> True/False,2차원
    # df_train.isnull().sum() -> 컬럼별 결측치의 갯수, 1차원  ## 통계함수가 들어가면 차원이 줄어듦.
    # -> index는 컬럼임 / value는 결측치의 갯수
    # df_train.isnull().sum()[df_train.isnull().sum() > 0] -> 결측치가 있는 데이터만 조회 -> 1차원 데이터(index=컬럼, value=결측치의 갯수)
    # .index -> index(=컬럼)만 조회
    train_none_cols = df_train.isnull().sum()[df_train.isnull().sum() > 0].index
    test_none_cols = df_test.isnull().sum()[df_test.isnull().sum() > 0].index
    none_cols = list(set(train_none_cols) | set(test_none_cols))  # 짝대기 | : or 의미함 -> 합집합
    # 위의 정한 값을 기준으로 train, test 데이터의 결측치 치환

    for col in none_cols:
        try: 
            _value = df_train[col].mean() # 숫자형 데이터의 경우 평균값 넣기
        except:
            _value = df_test[col].mode()[0] # 범주형 데이터의 경우 최빈값 넣기
        finally:
            # 결측치에 통계값 넣기
            df_train[col] = df_train[col].fillna(_value)
            df_test[col] = df_test[col].fillna(_value)

    return df_train, df_test

# 필요 없는 컬럼 제거 > 주피터파일에서 eda 확인후 결정
def __dropcols(df_train:pd.DataFrame, df_test:pd.DataFrame, drop_cols:list):
    return df_train.drop(drop_cols, axis=1), df_test.drop(drop_cols, axis=1)


# # 왜도 / 첨도 처리 : log 변환 > 주피터파일에서 eda 확인후 결정
# def __transform_cols(df_train:pd.DataFrame, df_test:pd.DataFrame, transform_cols:list):
    
#     for col in transform_cols: # age, fare
#         df_train[col] = df_train[col].map(lambda x : np.log1p(x)) 
#         df_test[col] = df_test[col].map(lambda x : np.log1p(x))
#         ## map은 1차원 데이터(col)만 받아줌. apply는 2차원 데이터(df)도 받아줌.
#         ## lambda x : np.log1p(x) -> x(파라미터)를 np.log1p(x)로 변환하고 x로 반환. 그래서 반환값이 변환된 x(리턴)가 됨.

#     return df_train, df_test



# df_test -> 제출용 데이터. 데이터가 줄어들면 
def do_cleansing(df_train:pd.DataFrame, df_test:pd.DataFrame, drop_cols:list):   
    # 1. row 중복 제거
    #df_train = df_train.drop_duplicates()
    # drop_duplicates() -> 중복된거 알아서 없애줌. 받을 인자 없음


    # 2. 결측치 치환(train데이터만 가지고 train, test 데이터의 결측치 치환)
    df_train, df_test = __fillna(df_train, df_test)

    # 3. 필요 없는 컬럼 제거                                      drop_cols를 외부에서 받아옴
    df_train, df_test = __dropcols(df_train, df_test, drop_cols=drop_cols)


    # 4. 왜도 / 첨도 처리
    # df_train, df_test = __transform_cols(df_train, df_test, transform_cols=transform_cols)

    # 5. 검증
    ## train, test 데이터의 컬럼 갯수가 같은지 확인
    assert df_train.shape[1] == df_test.shape[1], "학습용과 테스트용 데이터의 컬럼 갯수가 같지 않습니다."


    return df_train, df_test


