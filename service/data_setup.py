import pandas as pd

def load_dataset(path:str) -> pd.DataFrame:
    return pd.read_csv(path)


def split_features_targets(df_dataset:pd.DataFrame, target_name:str) -> tuple:
    df_target = df_dataset[target_name]
    df_features = df_dataset.drop(target_name, axis=1)
    return df_features, df_target


def do_load_dataset(train_path:str, test_path:str, target_name:str):
    df_train_full = load_dataset(path=train_path)
    df_test = load_dataset(path=test_path)

    df_train, df_trian_target = split_features_targets(
        df_dataset=df_train_full, target_name=target_name)
    
    return df_train, df_test, df_trian_target