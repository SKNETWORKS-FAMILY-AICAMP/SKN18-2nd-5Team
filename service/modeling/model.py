import enum
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier


class Model_Type(enum.Enum):  # 상속받아야 이넘 클래스의 __members__ 등의 속성을 사용할 수 있음
    # Tree-based Models
    lightgbm = (enum.auto(), LGBMClassifier)
    xgboost = (enum.auto(), XGBClassifier)
    random_forest = (enum.auto(), RandomForestClassifier)
    gradient_boosting = (enum.auto(), GradientBoostingClassifier)
    ada_boost = (enum.auto(), AdaBoostClassifier)
    extra_trees = (enum.auto(), ExtraTreesClassifier)
    
    # Linear Models
    logistic_regression = (enum.auto(), LogisticRegression)
    
    # Other Models
    svm = (enum.auto(), SVC)
    naive_bayes = (enum.auto(), GaussianNB)
    knn = (enum.auto(), KNeighborsClassifier)
    neural_network = (enum.auto(), MLPClassifier)

def create_model(model_name:Model_Type, hp:dict): 
    # 검증코드
    if model_name not in Model_Type.__members__:
        raise Exception(f"지원하지 않는 모델입니다. >> {model_name}")

    # 기본 하이퍼파라미터 설정
    default_params = get_default_params(model_name)
    final_params = {**default_params, **hp}  # hp로 덮어쓰기
    
    # 모델별 특별 처리
    try:
        if model_name in ["lightgbm"]:
            model = Model_Type[model_name].value[1](**final_params, verbose=-1)
        elif model_name in ["neural_network"]:
            model = Model_Type[model_name].value[1](**final_params, max_iter=500)
        elif model_name in ["svm"]:
            # SVM은 확률 예측을 위해 probability=True 필요
            model = Model_Type[model_name].value[1](**final_params, probability=True)
        else:
            model = Model_Type[model_name].value[1](**final_params)
    except Exception as e:
        # 파라미터 오류 시 기본 파라미터만으로 생성
        model = Model_Type[model_name].value[1]()
        
    return model


def get_default_params(model_name):
    """각 모델별 최적화된 기본 파라미터"""
    defaults = {
        'lightgbm': {
            'n_estimators': 200,
            'max_depth': 8,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'class_weight': 'balanced',
            'random_state': 42
        },
        'xgboost': {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'scale_pos_weight': 1.5,
            'random_state': 42,
            'eval_metric': 'logloss'
        },
        'random_forest': {
            'n_estimators': 200,
            'max_depth': 15,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'class_weight': {0: 1, 1: 1.5},
            'random_state': 42
        },
        'gradient_boosting': {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'random_state': 42
        },
        'ada_boost': {
            'n_estimators': 100,
            'learning_rate': 1.0,
            'random_state': 42
        },
        'extra_trees': {
            'n_estimators': 200,
            'max_depth': 15,
            'min_samples_split': 5,
            'class_weight': 'balanced',
            'random_state': 42
        },
        'logistic_regression': {
            'class_weight': 'balanced',
            'random_state': 42,
            'max_iter': 1000
        },
        'svm': {
            'class_weight': 'balanced',
            'random_state': 42
        },
        'naive_bayes': {},
        'knn': {
            'n_neighbors': 5,
            'weights': 'distance'
        },
        'neural_network': {
            'hidden_layer_sizes': (100, 50),
            'alpha': 0.01,
            'learning_rate_init': 0.01,
            'random_state': 42
        }
    }
    
    return defaults.get(model_name, {})