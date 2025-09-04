import os
import sys
import pandas as pd
from pathlib import Path

# 현재 스크립트의 경로를 기준으로 최상위 프로젝트 경로를 설정
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from hotel_booking_workflow import settings, preprocess, utils, modeling
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

# 1. 시드 초기화로 재현성 확보
settings.reset_seeds()

# 2. 데이터 로드 및 전처리 파이프라인 실행
df = preprocess.load_data(settings.DEFAULT_PATH)
split = preprocess.pipeline(df)
X_tr, y_tr = split.X_train, split.y_train
X_te, y_te = split.X_test, split.y_test

# 3. XGBoost 모델 학습
xgb_classifier = utils.train_xgb_classifier(X_tr, y_tr)

# 4. 성능 평가 및 결과 출력
y_tr_pred = xgb_classifier.predict(X_tr)
y_te_pred = xgb_classifier.predict(X_te)
y_tr_proba = xgb_classifier.predict_proba(X_tr)[:, 1]
y_te_proba = xgb_classifier.predict_proba(X_te)[:, 1]

# 훈련 데이터 성능
train_metrics = modeling.evaluate_binary(y_tr, y_tr_pred, y_tr_proba)
print(modeling.format_metrics("XGBoost 훈련 성능", train_metrics))

# 테스트 데이터 성능
test_metrics = modeling.evaluate_binary(y_te, y_te_pred, y_te_proba)
print(modeling.format_metrics("\nXGBoost 테스트 성능", test_metrics))