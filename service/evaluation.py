from service.data_setup import load_dataset

def create_submission_file(is_model, df_test):
    if not is_model :
        return       # 모델이 없으면 제출 안함

    predictions = is_model.predict_proba(df_test)[:,1]    # df_test 제출용으로 예측값 뽑기
    df_submission = load_dataset(path="./data/submission.csv")
    df_submission['survived'] = predictions
    df_submission.to_csv("./data/best_submission.csv",header=True, index=False)
