import os
import sys
import warnings
import warnings

import numpy as np
import pandas as pd

# Suppress ALL warnings and verbose output
warnings.filterwarnings('ignore')
import logging
logging.getLogger().setLevel(logging.ERROR)

# Suppress pandas output
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)

# Redirect stdout temporarily to suppress debug output
import contextlib
from io import StringIO

# Ensure current directory is importable
sys.path.insert(0, os.getcwd())

from service.data_setup import load_train_csv, load_test_csv, split_train_validation
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
from service.modeling.training import train_xgb_classifier


def main() -> None:
    """
    준비된 train 데이터를 train/validation으로 분할하여 모델 성능을 검증
    """
    print("=== Hotel Booking Cancellation 모델 성능 검증 ===")
    
    # 1. 준비된 train 데이터 로드
    data_dir = os.path.join('data')
    train_path = os.path.join(data_dir, 'hotel_bookings_train.csv')
    
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Train 데이터 파일이 없습니다: {train_path}")
    
    print(f"Train 데이터 로드: {train_path}")
    X, y = load_train_csv(train_path)
    print(f"전체 데이터 형태: {X.shape}, 타겟 분포: {y.value_counts().to_dict()}")
    
    # 2. 결측치 처리
    print("결측치 처리 중...")
    X = fill_missing_values(X)
    
    # 3. Train/Validation 분할
    print("Train/Validation 분할 (80:20)...")
    X_tr, X_val, y_tr, y_val = split_train_validation(X, y, random_state=42)
    print(f"Train: {X_tr.shape}, Validation: {X_val.shape}")
    
    # 4. 피처 엔지니어링 파이프라인 (조용히 실행)
    print("피처 엔지니어링 수행 중... 🔧")
    
    # Suppress all output during feature engineering
    with contextlib.redirect_stdout(StringIO()):
        X_tr, X_val = add_total_guests_and_is_alone(X_tr, X_val)
        X_tr, X_val = add_has_company(X_tr, X_val)
        X_tr, X_val = add_is_FB_meal(X_tr, X_val)
        X_tr, X_val = process_adr_iqr(X_tr, X_val)
        X_tr, X_val = add_total_stay(X_tr, X_val)
        X_tr, X_val = process_lead_time(X_tr, X_val)
        X_tr, X_val = map_hotel_type(X_tr, X_val)

        # 5. 불필요한 컬럼 먼저 드롭 (인코딩 전에!)
        X_tr, X_val = drop_original_columns(X_tr, X_val)
        # 6. 원-핫 인코딩 (드롭 후에!)
        X_tr, X_val = one_hot_encode_and_align(X_tr, X_val)
    
    print(f"✅ 피처 엔지니어링 완료! 최종 피처 수: {X_tr.shape[1]}")

    # 6. 모델 학습 및 평가
    print("XGBoost 모델 학습...")
    model = train_xgb_classifier(X_tr, y_tr, random_state=42)
    
    # 예측 수행
    y_tr_pred = model.predict(X_tr)
    y_val_pred = model.predict(X_val)
    y_tr_proba = model.predict_proba(X_tr)[:, 1]
    y_val_proba = model.predict_proba(X_val)[:, 1]

    # 결과 출력
    print("\n" + "🎯"*25)
    print("🏆 모델 성능 평가 결과 🏆")
    print("🎯"*25)
    print(format_metrics('📊 훈련 데이터 성능:', evaluate_binary(y_tr, y_tr_pred, y_tr_proba)))
    print()
    print(format_metrics('🔍 검증 데이터 성능:', evaluate_binary(y_val, y_val_pred, y_val_proba)))
    print("🎯"*25)
    
    # 성능이 만족스러운지 체크하고 test 데이터 예측 수행
    val_metrics = evaluate_binary(y_val, y_val_pred, y_val_proba)
    if val_metrics.f1 > 0.8 and val_metrics.auc > 0.85:
        print("✅ 모델 성능이 우수합니다! Test 데이터 예측을 수행합니다.")
        predict_test_data(model, X_tr, X_val)
    else:
        print("⚠️  모델 성능을 더 개선할 필요가 있을 수 있습니다.")
        print(f"   현재 F1-Score: {val_metrics.f1:.3f}, AUC-ROC: {val_metrics.auc:.3f}")
        
        user_input = input("그래도 Test 데이터 예측을 수행하시겠습니까? (y/n): ")
        if user_input.lower() == 'y':
            predict_test_data(model, X_tr, X_val)
        else:
            print("예측을 건너뜁니다. 모델을 개선한 후 다시 실행해주세요.")
    
    return model


def predict_test_data(model, X_tr_processed, X_val_processed):
    """
    검증된 모델로 test 데이터 예측 수행
    """
    print("\n" + "="*50)
    print("Test 데이터 예측 수행")
    print("="*50)
    
    # Test 데이터 로드
    data_dir = os.path.join('data')
    test_path = os.path.join(data_dir, 'hotel_bookings_test.csv')
    
    if not os.path.exists(test_path):
        print(f"❌ Test 데이터 파일이 없습니다: {test_path}")
        return
    
    print(f"Test 데이터 로드: {test_path}")
    X_test = load_test_csv(test_path)
    print(f"Test 데이터 형태: {X_test.shape}")
    
    # 결측치 처리
    X_test = fill_missing_values(X_test)
    
    # Train 데이터와 동일한 피처 엔지니어링 적용 (더미 train 데이터 사용)
    print("피처 엔지니어링 적용...")
    dummy_X_tr = X_tr_processed.iloc[:100].copy()  # 작은 더미 데이터
    
    # 원래 컬럼들로 되돌리기 위해 역변환 (복잡하므로 다른 방법 사용)
    # 대신 처음부터 다시 피처 엔지니어링 적용
    
    # 다시 train 데이터 로드 (피처 엔지니어링용)
    train_path = os.path.join(data_dir, 'hotel_bookings_train.csv')
    X_train_for_fe, _ = load_train_csv(train_path)
    X_train_for_fe = fill_missing_values(X_train_for_fe)
    
    # 피처 엔지니어링 다시 적용
    X_train_fe, X_test_fe = add_total_guests_and_is_alone(X_train_for_fe, X_test)
    X_train_fe, X_test_fe = add_has_company(X_train_fe, X_test_fe)
    X_train_fe, X_test_fe = add_is_FB_meal(X_train_fe, X_test_fe)
    X_train_fe, X_test_fe = process_adr_iqr(X_train_fe, X_test_fe)
    X_train_fe, X_test_fe = add_total_stay(X_train_fe, X_test_fe)
    X_train_fe, X_test_fe = process_lead_time(X_train_fe, X_test_fe)
    X_train_fe, X_test_fe = map_hotel_type(X_train_fe, X_test_fe)
    
    # 예측 결과 CSV용 데이터 저장 (원본 test.csv의 모든 컬럼 보존)
    # 피처 엔지니어링 전의 원본 test 데이터 사용
    result_data = X_test.copy()  # 원본 test 데이터의 모든 컬럼 보존
    
    # 불필요한 컬럼 먼저 드롭 (인코딩 전에!)
    X_train_final, X_test_final = drop_original_columns(X_train_fe, X_test_fe)
    # 원-핫 인코딩 (드롭 후에!)
    X_train_final, X_test_final = one_hot_encode_and_align(X_train_final, X_test_final)
    
    # 예측 수행
    print("예측 수행 중...")
    y_pred = model.predict(X_test_final)
    y_pred_proba = model.predict_proba(X_test_final)[:, 1]
    
    print(f"🎯 예측 완료! 총 {len(y_pred)}개 샘플")
    print(f"📋 취소 예측: {sum(y_pred)}개 ({sum(y_pred)/len(y_pred)*100:.1f}%)")
    
    # 결과 저장
    results_dir = os.path.join('data', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    result_data['predicted_is_canceled'] = y_pred
    result_data['predicted_probability'] = y_pred_proba
    
    result_path = os.path.join(results_dir, 'hotel_booking_predictions.csv')
    result_data.to_csv(result_path, index=False)
    
    print(f"📁 예측 결과 저장: {result_path}")
    print(f"📊 저장된 데이터 형태: {result_data.shape}")
    
    # 결과 미리보기
    print("\n=== 예측 결과 미리보기 ===")
    print(result_data.head())
    
    print("="*50)


if __name__ == '__main__':
    main()


