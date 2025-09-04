import pandas as pd


def do_encoding(df_train:pd.DataFrame, df_test:pd.DataFrame, encoding_cols:list, args):
    """
    모델 타입에 따라 다른 인코딩 적용
    
    Args:
        model_type: 'lightgbm', 'catboost', 'xgboost' 중 선택
    """
    
    if args.model_name in ['lightgbm', 'catboost']:
        # LightGBM, CatBoost: category 타입으로만 변환
        for col in encoding_cols:
            df_train[col] = df_train[col].astype('category')
            df_test[col] = df_test[col].astype('category')
    
    elif args.model_name == 'xgboost':
        # XGBoost: 원-핫 인코딩 필요
        import category_encoders as ce
        encoder = ce.OneHotEncoder(cols=encoding_cols, use_cat_names=True)
        df_train = encoder.fit_transform(df_train)
        df_test = encoder.transform(df_test)
    
    return df_train, df_test 




    ### lightgbm, catboost 