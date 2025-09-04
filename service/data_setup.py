import pandas as pd

def load_dataset(path:str) -> pd.DataFrame:
    return pd.read_csv(path)


def split_features_targets(df_dataset:pd.DataFrame, target_name:str) -> tuple:
    y_df = df_dataset[target_name]
    x_df = df_dataset.drop(target_name, axis=1)
    return x_df, y_df


def do_load_dataset(train_path:str, test_path:str, target_name:str):
    df_train_full = load_dataset(path=train_path)
    df_test = load_dataset(path=test_path)

    x_tr, y_tr = split_features_targets(
        df_dataset=df_train_full, target_name=target_name)
    
    x_te, y_te = split_features_targets(
        df_dataset=df_test, target_name=target_name)
    
    return x_tr, x_te, y_tr, y_te