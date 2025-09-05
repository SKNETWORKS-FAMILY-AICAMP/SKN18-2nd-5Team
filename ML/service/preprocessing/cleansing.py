import pandas as pd


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['company'] = df['company'].fillna(0)
    df['agent'] = df['agent'].fillna(0)
    df['children'] = df['children'].fillna(0)
    df['country'] = df['country'].fillna(df['country'].mode()[0])
    return df


