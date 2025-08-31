# 🏨 호텔 예약 취소 예측 프로젝트

## 📋 프로젝트 개요
**목적**: 호텔 예약 취소 여부(`is_canceled`)를 예측하여 호텔 수요 예측 및 수익 최적화를 위한 데이터 분석 및 머신러닝/딥러닝 모델 구축

**데이터셋**: `hotel_bookings.csv`
- **타겟 변수**: `is_canceled` (0: 유지, 1: 취소)
- **예측 목표**: 예약 취소 확률 예측을 통한 호텔 수요 관리

---

## 🔄 데이터 전처리 파이프라인

### 1️⃣ 불필요한 컬럼 제거 (Drop Columns)
**제거 대상 및 근거:**
- `arrival_date_year`, `arrival_date_month`, `arrival_date_week_number`, `arrival_date_day_of_month`: 박스플롯 분석 결과 타겟과 상관성 낮음
- `country`: 과도한 범주 수 (고차원 문제)
- `reservation_status`, `reservation_status_date`: 타겟 변수와 중복/누수 위험
- `agent`: 316개 고유값으로 인한 차원의 저주
- `hotel`: 분석 목적과 무관

### 2️⃣ 결측치 처리 (Missing Value Imputation)
| 컬럼 | 처리 방법 | 근거 |
|------|-----------|------|
| `children` | 0으로 대체 | describe() 분석 결과 75%가 아이 없음 (최빈값) |
| `company` | 0으로 대체 | 회사 미이용 예약자 구분을 위함 (피처 생성 전 단계) |
| `agent` | 0으로 대체 | 에이전트 미이용 예약자 구분을 위함 (피처 생성 전 단계) |

### 3️⃣ 피처 엔지니어링 (Feature Engineering)
**새로운 피처 생성:**

| 피처명 | 생성 로직 | 비즈니스 가설 |
|--------|-----------|---------------|
| `has_company` | `company > 0` → 1, else 0 | 회사 예약 시 취소율 차이 |
| `has_agent` | `agent > 0` → 1, else 0 | 에이전트 예약 시 취소율 차이 |
| `is_FB_meal` | `meal == 'FB'` → 1, else 0 | Full Board 식사 시 취소율 높음 |
| `room_type_changed` | `reserved_room_type != assigned_room_type` → 1, else 0 | 방 변경 시 고객 불만으로 취소율 증가 |
| `market_risk_level` | 시장 세분화 기반 리스크 레벨 | 예약 채널별 취소 패턴 차이 |

**`market_risk_level` 매핑:**
- **High risk**: Groups, Online_TA
- **Medium risk**: Offline_TA/TO  
- **Low risk**: Direct, Corporate, Complementary

### 4️⃣ 데이터 분포 정규화 (Skewness & Kurtosis Treatment)
**로그 변환 기준**: `|왜도| >= 1` AND `첨도 >= 2`

**변환 대상 피처:**
```
📊 수치형 원본 피처:
- lead_time, stays_in_weekend_nights, stays_in_week_nights
- adults, children, babies
- previous_cancellations, previous_bookings_not_canceled
- booking_changes, days_in_waiting_list
- adr, required_car_parking_spaces, total_of_special_requests

🔧 생성된 피처:
- has_company, has_agent, is_FB_meal, room_type_changed
```

### 5️⃣ 범주형 인코딩 (Categorical Encoding)
**원핫 인코딩 (One-Hot Encoding)**
- 대상: `object` 및 `category` 데이터 타입
- 도구: `category_encoders.OneHotEncoder`
- 메모리 최적화: 사전에 `category` 타입으로 변환

### 6️⃣ 피처 스케일링 (Feature Scaling)
**선별적 표준화 적용:**
- **스케일링 대상**: 연속형 수치 피처만
- **제외 대상**: 원핫 인코딩된 이진 피처 (0/1)
- **방법**: `StandardScaler` 적용
- **적용 순서**: Train 데이터로 학습 → Validation/Test 데이터에 동일 파라미터 적용

---

## 🤖 모델링 전략  -- (수정 필)

### 주요 모델: **LightGBM**
**선택 근거:**
- 범주형 피처 자동 처리
- 빠른 학습 속도
- 높은 예측 성능
- 스케일링에 덜 민감

### 보조 모델: **Logistic Regression**
**비교 목적:**
- 스케일링 효과 검증
- 해석 가능성 제공
- 베이스라인 성능 측정

---

## 📈 예상 성과 및 활용 방안

### 비즈니스 임팩트:
1. **수요 예측 정확도 향상** → 객실 오버부킹 최적화
2. **취소 패턴 분석** → 마케팅 전략 수립
3. **수익 최적화** → 동적 가격 책정 지원
4. **고객 세분화** → 맞춤형 서비스 제공

### 기술적 성과:
- 예측 정확도: AUC-ROC 0.85+ 목표
- 피처 중요도 분석을 통한 비즈니스 인사이트 도출
- 실시간 예측 시스템 구축 가능한 모델 파이프라인 완성