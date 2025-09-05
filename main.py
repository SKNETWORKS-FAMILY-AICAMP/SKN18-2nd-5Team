import os
import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import f1_score
from imblearn.over_sampling import SMOTE
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, StackingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

# Suppress ALL warnings and verbose output
warnings.filterwarnings('ignore')
import logging
logging.getLogger().setLevel(logging.ERROR)

# Suppress pandas output
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)

# Avoid console crashes on unsupported characters (e.g., emojis) in Windows terminals
try:
    sys.stdout.reconfigure(errors='replace')
    sys.stderr.reconfigure(errors='replace')
except Exception:
    pass

# Redirect stdout temporarily to suppress debug output
import contextlib
from io import StringIO

# Ensure current directory is importable
sys.path.insert(0, os.getcwd())

from service.data_setup import load_train_csv, load_test_csv, split_train_validation
from service.preprocessing.cleansing import fill_missing_values
from service.preprocessing.featureExtraction import (
    add_total_guests_and_is_alone,
    add_has_company,
    add_is_FB_meal,
    process_adr_iqr,
    add_total_stay,
    process_lead_time,
    map_hotel_type,
)
from service.preprocessing.encoding import one_hot_encode_and_align, drop_original_columns
from service.modeling.metrics import evaluate_binary, format_metrics


def main() -> None:
    """
    준비된 train 데이터를 train/validation으로 분할하여 모델 성능을 검증
    """
    print("=== Hotel Booking Cancellation 모델 성능 검증 ===")
    
    # 1. 데이터 로드, 결측치 처리, 분할
    data_dir = os.path.join('data')
    train_path = os.path.join(data_dir, 'hotel_bookings_train.csv')
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Train 데이터 파일이 없습니다: {train_path}")
    
    print(f"Train 데이터 로드: {train_path}")
    X, y = load_train_csv(train_path)
    X = fill_missing_values(X)
    X_tr, X_val, y_tr, y_val = split_train_validation(X, y, random_state=42)
    
    # 2. 피처 엔지니어링
    print("피처 엔지니어링 수행 중...")
    with contextlib.redirect_stdout(StringIO()):
        X_tr, X_val = add_total_guests_and_is_alone(X_tr, X_val)
        X_tr, X_val = add_has_company(X_tr, X_val)
        X_tr, X_val = add_is_FB_meal(X_tr, X_val)
        X_tr, X_val = process_adr_iqr(X_tr, X_val)
        X_tr, X_val = add_total_stay(X_tr, X_val)
        X_tr, X_val = process_lead_time(X_tr, X_val)
        X_tr, X_val = map_hotel_type(X_tr, X_val)
        X_tr, X_val = drop_original_columns(X_tr, X_val)
        X_tr, X_val = one_hot_encode_and_align(X_tr, X_val)
    
    X_tr.columns = [c.replace(' ', '_') for c in X_tr.columns]
    X_val.columns = [c.replace(' ', '_') for c in X_val.columns]
    print(f"피처 엔지니어링 완료. 피처 수: {X_tr.shape[1]}")

    # 3. SMOTE 오버샘플링 (훈련 데이터에만 적용)
    print("SMOTE 오버샘플링 수행 중...")
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_tr_smote, y_tr_smote = smote.fit_resample(X_tr, y_tr)
    print(f"SMOTE 적용 후 훈련 데이터 크기: {X_tr_smote.shape}")

    # 4. 피처 선택 (SelectFromModel) - 기준 강화
    print("피처 선택 수행 중 (기준 강화)...")
    selector_model = LGBMClassifier(random_state=42, n_jobs=-1)
    selector = SelectFromModel(
        selector_model, 
        threshold='1.25*median',
        prefit=False
    ).fit(X_tr_smote, y_tr_smote)
    
    X_tr_selected = selector.transform(X_tr_smote)
    X_val_selected = selector.transform(X_val)
    print(f"피처 선택 후 피처 수: {X_tr_selected.shape[1]}")
    
    # 5. 스태킹 앙상블 모델 정의 (규제 대폭 강화)
    print("스태킹 앙상블 모델 구성 (규제 대폭 강화)...")
    estimators = [
        ('rf', RandomForestClassifier(
            n_estimators=200, max_depth=10, min_samples_leaf=10, max_features='sqrt', random_state=42, n_jobs=1
        )),
        ('et', ExtraTreesClassifier(
            n_estimators=200, max_depth=10, min_samples_leaf=10, max_features='sqrt', random_state=42, n_jobs=1
        )),
        ('xgb', XGBClassifier(
            n_estimators=1200, max_depth=5, learning_rate=0.03, subsample=0.7, colsample_bytree=0.7,
            use_label_encoder=False, eval_metric='logloss', random_state=42, n_jobs=1
        )),
        ('lgbm', LGBMClassifier(
            n_estimators=1200, max_depth=5, learning_rate=0.03, num_leaves=20,
            random_state=42, n_jobs=1
        ))
    ]
    
    final_estimator = LogisticRegression(C=0.1, random_state=42, n_jobs=-1)
    
    model = StackingClassifier(
        estimators=estimators,
        final_estimator=final_estimator,
        cv=5,
        stack_method='predict_proba',
        n_jobs=-1,
        passthrough=False
    )

    print("스태킹 모델 학습...")
    model.fit(X_tr_selected, y_tr_smote)

    # 6. 최적 임계값(Threshold) 찾기
    print("최적 임계값 탐색 중...")
    y_val_proba = model.predict_proba(X_val_selected)[:, 1]
    thresholds = np.arange(0.3, 0.701, 0.001)
    f1_scores = [f1_score(y_val, y_val_proba >= t) for t in thresholds]
    best_threshold = thresholds[np.argmax(f1_scores)]
    print(f"최적 임계값: {best_threshold:.3f}")

    # 7. 예측 및 평가
    y_tr_proba = model.predict_proba(X_tr_selected)[:, 1]
    y_tr_pred = (y_tr_proba >= best_threshold).astype(int)
    y_val_pred = (y_val_proba >= best_threshold).astype(int)

    print("\n" + "="*25)
    print("모델 성능 평가 결과")
    print("="*25)
    print(format_metrics('훈련 데이터 성능:', evaluate_binary(y_tr_smote, y_tr_pred, y_tr_proba)))
    print()
    print(format_metrics('검증 데이터 성능:', evaluate_binary(y_val, y_val_pred, y_val_proba)))
    print("="*25)
    
    # <<<<<<< 수정된 부분 시작 (항상 Test 예측 수행) >>>>>>>
    # 8. Test 데이터 예측 수행
    # 점수와 상관없이 항상 predict_test_data 함수를 호출하여 예측 파일을 생성합니다.
    print("Test 데이터 예측을 수행합니다.")
    predict_test_data(model, selector, X_tr, best_threshold)
    # <<<<<<< 수정된 부분 끝 >>>>>>>
    
    return model


def predict_test_data(model, selector, X_tr_reference, threshold):
    """
    검증된 모델, 피처 선택기, 최적 임계값으로 test 데이터 예측 수행
    """
    print("\n" + "="*50)
    print("Test 데이터 예측 수행")
    print("="*50)
    
    # Test 데이터 로드 및 전처리
    data_dir = os.path.join('data')
    test_path = os.path.join(data_dir, 'hotel_bookings_test.csv')
    if not os.path.exists(test_path):
        print(f"Test 데이터 파일이 없습니다: {test_path}")
        return
    
    print(f"Test 데이터 로드: {test_path}")
    X_test_orig = load_test_csv(test_path)
    X_test = X_test_orig.copy()
    
    # Test 데이터에서 타겟 컬럼 제거 (있다면)
    if 'is_canceled' in X_test.columns:
        print("Test 데이터에서 'is_canceled' 컬럼을 제거합니다.")
        X_test = X_test.drop('is_canceled', axis=1)
    
    X_test = fill_missing_values(X_test)
    
    # Train 데이터와 동일한 피처 엔지니어링 적용
    print("피처 엔지니어링 적용...")
    
    dummy_train_df = pd.DataFrame(columns=X_test.columns.difference(['lead_time_group']))
    
    _, X_test = add_total_guests_and_is_alone(dummy_train_df.copy(), X_test)
    _, X_test = add_has_company(dummy_train_df.copy(), X_test)
    _, X_test = add_is_FB_meal(dummy_train_df.copy(), X_test)
    _, X_test = process_adr_iqr(dummy_train_df.copy(), X_test)
    _, X_test = add_total_stay(dummy_train_df.copy(), X_test)
    _, X_test = process_lead_time(dummy_train_df.copy(), X_test)
    _, X_test = map_hotel_type(dummy_train_df.copy(), X_test)
    _, X_test = drop_original_columns(dummy_train_df.copy(), X_test)
    
    # 실제 Train 데이터를 참조로 사용 (원-핫 인코딩 구조 동일하게 맞춤)
    print(f"X_tr_reference shape: {X_tr_reference.shape}")
    print(f"X_tr_reference columns: {list(X_tr_reference.columns)}")
    print(f"X_test shape before encoding: {X_test.shape}")
    print(f"X_test columns before encoding: {list(X_test.columns)}")
    print(f"X_test categorical columns: {X_test.select_dtypes(include='object').columns.tolist()}")
    
    # 강제로 Test 데이터 원-핫 인코딩 후 Train 컬럼에 맞춤
    print("강제 원-핫 인코딩 적용...")
    
    # Test 데이터 원-핫 인코딩
    cat_cols = X_test.select_dtypes(include='object').columns.tolist()
    if len(cat_cols) > 0:
        X_test = pd.get_dummies(X_test, columns=cat_cols, drop_first=True)
    
    # Train 컬럼에 맞춰서 정렬 (누락된 컬럼은 0으로 채움)
    X_test = X_test.reindex(columns=X_tr_reference.columns, fill_value=0)
    
    print(f"X_test shape after encoding: {X_test.shape}")
    print(f"X_test columns after encoding: {list(X_test.columns)}")
    print(f"Train과 Test 컬럼 일치: {set(X_test.columns) == set(X_tr_reference.columns)}")

    X_test.columns = [c.replace(' ', '_') for c in X_test.columns]
    
    print("피처 선택 적용...")
    X_test_selected = selector.transform(X_test)
    
    # 예측 수행
    print("예측 수행 중...")
    y_pred_proba = model.predict_proba(X_test_selected)[:, 1]
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    print(f"예측 완료. 총 {len(y_pred)}개 샘플")
    print(f"취소 예측: {sum(y_pred)}개 ({sum(y_pred)/len(y_pred)*100:.1f}%)")
    
    # 결과 저장
    results_dir = os.path.join('data', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    result_data = X_test_orig.copy()
    result_data['predicted_is_canceled'] = y_pred
    result_data['predicted_probability'] = y_pred_proba
    

    # 타임스탬프 생성 (월일시분초)
    timestamp = datetime.now().strftime("%m%d%H%M%S")
    result_filename = f'hotel_booking_predictions_{timestamp}.csv'
    result_path = os.path.join(results_dir, result_filename)
    result_data.to_csv(result_path, index=False)
    
    print(f"📁 예측 결과 저장: {result_path}")
    print(f"📊 저장된 데이터 형태: {result_data.shape}")
    print(f"🕐 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 결과 미리보기
    print("\n=== 예측 결과 미리보기 ===")
    print(result_data.head())
    
    print("="*50)


if __name__ == '__main__':
    main()


