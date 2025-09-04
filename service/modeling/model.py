import enum
from lightgbm import LGBMClassifier


class Model_Type(enum.Enum):  # 상속받아야 이넘 클래스의 __members__ 등의 속성을 사용할 수 있음
    # name = value(enum.auto()_아이디역할. 여러모델 섞이지 않도록_ , 모델이름)
    lightgbm = (enum.auto(), LGBMClassifier)  # 튜플형태 -> 두번째 값이 모델이름 -> Model_Type[model_name].value[1]
                                              # args에 넣을 --model_name 값


def create_model(model_name:Model_Type, hp:dict): 
    # 검증코드
    # __members__ 안에는 [lghtGBM, 등등 위에서 ]
    if model_name not in Model_Type.__members__:
        raise Exception(f"지원하지 않는 모델입니다. >> {model_name}")

    # 비지니스코드
    #  model = Model_Type[model_name].value[1]
    #  -> LGBMRegressor(**hp)
    model = Model_Type[model_name].value[1](**hp, verbose=-1) # 파라미터를 받아 모델의 밸류-2번째(모델)를 실행하라


    # 리턴
    return model