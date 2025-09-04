'''
피처 생성
x_tr, x_te
'''

import pandas as pd
import numpy as np

def do_feature_extraction(df_train:pd.DataFrame, df_test:pd.DataFrame):
    # has_conpany
    df_train['has_company'] = (df_train['company'] > 0).astype(int)
    df_test['has_company'] = (df_test['company'] > 0).astype(int) 

    # has_agent
    df_train['has_agent'] = (df_train['agent'] > 0).astype(int)
    df_test['has_agent'] = (df_test['agent'] > 0).astype(int)

    # is_FB_meal
    df_train['is_FB_meal'] = np.where(df_train['meal'] == 'FB', 1, 0)
    df_test['is_FB_meal'] = np.where(df_test['meal'] == 'FB', 1, 0)

    # market_rist_level -> 인코딩 필요(라이트gbm, 캣부스트 제외)
        # 리스크 레벨 매핑 딕셔너리
    risk_mapping = {
    'Groups': 'High risk',
    'Online TA': 'High risk', 
    'Offline TA/TO': 'Medium risk',
    'Direct': 'Low risk',
    'Corporate': 'Low risk',
    'Complementary': 'Low risk'}
    df_train['market_risk_level'] = df_train['market_segment'].map(risk_mapping)
    df_test['market_risk_level'] = df_test['market_segment'].map(risk_mapping)

    # is_HighRisk_markket_risk
    df_train['is_High_risk_market_risk'] = (df_train['market_risk_level'] == 'High risk').astype(int)
    df_test['is_High_risk_market_risk'] = (df_test['market_risk_level'] == 'High risk').astype(int)
    
    # adr_processed
    # 1. IQR을 사용하여 훈련 데이터(X_tr)의 이상치 범위 계산
    Q1 = df_train['adr'].quantile(0.25)
    Q3 = df_train['adr'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    lower_bound = Q1 - 1.5 * IQR
    # 2. 이상치(outliers)를 제외한 훈련 데이터의 adr 중앙값 재계산
    # adr은 보통 0보다 크므로 하한선을 0으로 설정하거나 IQR로 계산된 값을 사용
    # 여기서는 IQR로 계산된 값을 사용하여 더 일반적인 방법으로 처리
    adr_filtered_median = df_train.loc[(df_train['adr'] >= lower_bound) & (df_train['adr'] <= upper_bound), 'adr'].median()
    # 3. 훈련 세트(X_tr)에 새로운 'adr_processed' 피처 생성
    # 이상치 범위(lower_bound ~ upper_bound)를 벗어나는 값들을 필터링된 중앙값으로 대체
    df_train['adr_processed'] = np.where(
        (df_train['adr'] < lower_bound) | (df_train['adr'] > upper_bound),
        adr_filtered_median,
        df_train['adr'])
    # 4. 테스트 세트(X_te)에 새로운 'adr_processed' 피처 생성
    # 훈련 데이터에서 계산한 동일한 이상치 범위와 중앙값을 사용
    df_test['adr_processed'] = np.where(
        (df_test['adr'] < lower_bound) | (df_test['adr'] > upper_bound),
        adr_filtered_median,
        df_test['adr'])

    # lead_time_processed
    # 2. # 1단계: 훈련 데이터(X_tr)에서 IQR을 사용하여 이상치 범위 계산
    Q1 = df_train['lead_time'].quantile(0.25)
    Q3 = df_train['lead_time'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    # 2단계: 이상치를 제외한 데이터로 중앙값 재계산
    # lead_time은 음수일 수 없으므로 하한선은 0으로 설정합니다.
    lead_time_filtered_median = df_train.loc[(df_train['lead_time'] >= 0) & (df_train['lead_time'] <= upper_bound), 'lead_time'].median()
    # 3단계: X_tr에 'lead_time_processed' 피처 생성
    # 0 미만이거나 상한선(upper_bound)을 초과하는 값을 필터링된 중앙값으로 대체
    df_train['lead_time_processed'] = np.where(
        (df_train['lead_time'] < 0) | (df_train['lead_time'] > upper_bound),
        lead_time_filtered_median,
        df_train['lead_time'])
    # 4단계: X_te에 'lead_time_processed' 피처 생성
    # 훈련 데이터에서 계산한 동일한 상한선과 중앙값을 사용
    df_test['lead_time_processed'] = np.where(
        (df_test['lead_time'] < 0) | (df_test['lead_time'] > upper_bound),
        lead_time_filtered_median,
        df_test['lead_time'])

    # is_alone
    ## 준호님꺼
    df_train['total_guests'] = df_train['adults'] + df_train['children'] + df_train['babies']
    df_test['total_guests'] = df_test['adults'] + df_test['children'] + df_test['babies']
    # Create 'is_alone' feature for both sets
    # 1 if total_guests is 1, otherwise 0
    df_train['is_alone'] = df_train['total_guests'].apply(lambda x: 1 if x == 1 else 0)
    df_test['is_alone'] = df_test['total_guests'].apply(lambda x: 1 if x == 1 else 0)
    # Optionally, you can drop the intermediate 'total_guests' feature
    df_train = df_train.drop('total_guests', axis=1)
    df_test = df_test.drop('total_guests', axis=1)
    
    # is_resort
    # City Hotel은 0, Resort Hotel은 1로 변환
    df_train['is_resort'] = df_train['hotel'].map({'City Hotel': 0, 'Resort Hotel': 1})
    df_test['is_resort'] = df_test['hotel'].map({'City Hotel': 0, 'Resort Hotel': 1})

    # is_transient
    df_train['is_transient'] = (df_train['customer_type'] == 'Transient').astype(int)
    df_test['is_transient'] = (df_test['customer_type'] == 'Transient').astype(int)

    # total_stays
    df_train['total_stays'] = df_train['stays_in_weekend_nights'] + df_train['stays_in_week_nights']
    df_test['total_stays'] = df_test['stays_in_weekend_nights'] + df_test['stays_in_week_nights']



    return df_train, df_test


