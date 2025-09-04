## Hotel Booking Cancellation - Modular Pipeline
호텔 예약 취소 여부(`is_canceled`)를 예측하는 이진 분류 프로젝트입니다. 실험용 노트북(`ver_01.ipynb`, `ver_03.ipynb`)과 재현 가능한 스크립트(`main.py`)를 모두 지원하도록 `service/` 기반으로 모듈화했습니다.

### Project Structure
```
├── main.py
├── requirements.txt
├── archive/
│   └── hotel_bookings.csv
├── data/
│   ├── hotel_bookings_train.csv (선택)
│   └── hotel_bookings_test.csv  (선택)
├── service/
│   ├── data_setup.py
│   ├── preprocessing/
│   │   ├── adata_preprocessing.py (예약: 필요 시 추가)
│   │   ├── cleansing.py
│   │   ├── encoding.py
│   │   └── featureExtraction.py
│   └── modeling/
│       ├── model.py
│       ├── training.py
│       ├── cross_validation.py
│       └── metrics.py
├── ver_01.ipynb # EDA
└── ver_03.ipynb # 전처리한 jupyter
```

### Setup
```bash
pip install -r requirements.txt
```

### Quickstart
- Script (end-to-end pipeline):
```bash
python main.py
```
- If `data/` has pre-split CSVs, they are used. Otherwise `archive/hotel_bookings.csv`를 로드해 내부에서 분할합니다.

### Notebooks
- `ver_01.ipynb`: 초기 실험 노트북 (수동/탐색 중심)
- `ver_03.ipynb`: 파이프라인을 모듈로 호출하는 예시가 하단 셀에 포함됨
- `ver_03.ipynb` 하단 셀에서 `service` 모듈을 임포트해 동일 파이프라인 실행 가능:
```python
from service.data_setup import load_raw_csv, train_test_from_raw
from service.preprocessing.cleansing import fill_missing_values
from service.preprocessing.featureExtraction import add_total_guests_and_is_alone
```

### Modules
- `service/data_setup.py`: CSV 로드, raw 데이터에서 train/test 분할
- `service/preprocessing/cleansing.py`: 결측치 처리
- `service/preprocessing/encoding.py`: 원-핫 인코딩 및 컬럼 정렬, 원본 컬럼 제거
- `service/preprocessing/featureExtraction.py`: 특징 생성(단독여부, company, meal, adr IQR 처리, total_stay, lead_time 처리, hotel 타입 매핑)
- `service/modeling/model.py`: XGBoost 모델 빌더
- `service/modeling/training.py`: 학습 함수
- `service/modeling/cross_validation.py`: Stratified K-Fold 교차검증
- `service/modeling/metrics.py`: 지표 계산 및 포맷

### Tips
- 노트북 실행 환경에서 현재 폴더가 `C:\dev\hotel`이 아닐 경우, 아래를 먼저 실행해 모듈 경로를 보장하세요.
```python
import sys, os
sys.path.insert(0, os.getcwd())
```