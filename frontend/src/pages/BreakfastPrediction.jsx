import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import axios from 'axios';
import toast from 'react-hot-toast';
import Header from '../components/Header';
import 'react-calendar/dist/Calendar.css';
import './BreakfastPrediction.css';

function BreakfastPrediction() {
  const [selectedDate, setSelectedDate] = useState(new Date('2017-04-01'));
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hotelType, setHotelType] = useState('Resort Hotel');
  const [availableDates, setAvailableDates] = useState([]);
  const [dateRange, setDateRange] = useState({ min: null, max: null });

  useEffect(() => {
    document.body.className = 'breakfast-page-body';
    fetchAvailableDates();
    
    return () => {
      document.body.className = '';
    };
  }, []);

  const fetchAvailableDates = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/dates/available');
      setAvailableDates(response.data.available_dates);
      setDateRange({
        min: new Date(response.data.min_date),
        max: new Date(response.data.max_date)
      });
    } catch (error) {
      console.error('Error fetching available dates:', error);
      toast.error('사용 가능한 날짜를 불러오는데 실패했습니다.');
    }
  };

  const handleDateClick = async (date) => {
    const formattedDate = format(date, 'yyyy-MM-dd');
    
    if (!availableDates.includes(formattedDate)) {
      toast.error('해당 날짜의 데이터가 없습니다.');
      return;
    }

    setSelectedDate(date);
    setLoading(true);
    setPrediction(null);

    try {
      const response = await axios.post('http://localhost:8000/api/predict/date', {
        date: formattedDate,
        hotel_type: hotelType,
      });
      
      setPrediction(response.data);
      toast.success('조식 예측 완료!');
    } catch (error) {
      toast.error('예측 중 오류가 발생했습니다.');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const tileDisabled = ({ date, view }) => {
    if (view === 'month') {
      const formattedDate = format(date, 'yyyy-MM-dd');
      return !availableDates.includes(formattedDate);
    }
    return false;
  };

  return (
    <div className="breakfast-page">
      <Header 
        title="BREAKFAST PREDICTION"
        subtitle="날짜를 선택하여 조식 준비량을 예측하세요"
      />

      <div className="main-container">
        {/* 상단 그리드: 호텔선택(좌상단) + 날짜선택(우상단) */}
        <div className="top-grid">
          {/* 호텔 선택 - 좌상단 */}
          <div className="hotel-config-section">
            <div className="section-title">🏨 호텔 선택</div>
            <div className="hotel-selector">
              <label>호텔 타입</label>
              <select 
                value={hotelType} 
                onChange={(e) => setHotelType(e.target.value)}
                className="hotel-select"
              >
                <option value="Resort Hotel">리조트 호텔</option>
                <option value="City Hotel">시티 호텔</option>
              </select>
            </div>
            <div className="selected-date">
              <span className="date-label">선택된 날짜</span>
              <span className="date-value">{format(selectedDate, 'yyyy년 MM월 dd일')}</span>
            </div>
          </div>

          {/* 날짜 선택 - 우상단 */}
          <div className="calendar-section">
            <div className="section-title" style={{ alignSelf: 'flex-start' }}>🗓️ 날짜 선택</div>
            <div className="calendar-container">
              <Calendar
                onChange={handleDateClick}
                value={selectedDate}
                locale="ko-KR"
                tileDisabled={tileDisabled}
                minDate={dateRange.min}
                maxDate={dateRange.max}
                className="prediction-calendar"
              />
            </div>
          </div>
        </div>

        {/* 조식 예측 결과 - 위 두 개 아래에 넓게 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="prediction-section"
          style={{ width: '100%', margin: '0 auto', maxWidth: '900px' }}
        >
          <div className="section-title">🍳 조식 예측 결과</div>
          
          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>예측 중...</p>
            </div>
          ) : prediction ? (
            <div className="prediction-results">
              {/* 메인 예측 카드 */}
              <div className="main-result-card">
                <div className="result-header">조식 준비 권장량</div>
                <div className="result-value">{prediction.breakfast_recommendation}인분</div>
                <div className="result-subtitle">
                  취소율 {(prediction.details.avg_cancellation_probability * 100).toFixed(1)}% 반영
                </div>
              </div>

              {/* 상세 정보 */}
              <div className="details-grid">
                <div className="detail-card">
                  <div className="detail-label">총 예약 고객</div>
                  <div className="detail-value">{prediction.total_reservations}명</div>
                </div>
                
                <div className="detail-card">
                  <div className="detail-label">예상 체크인</div>
                  <div className="detail-value">{prediction.expected_checkins}명</div>
                </div>
                
                <div className="detail-card">
                  <div className="detail-label">조식 신청자</div>
                  <div className="detail-value">{prediction.details.breakfast_guests}명</div>
                </div>
                
                <div className="detail-card">
                  <div className="detail-label">예측 신뢰도</div>
                  <div className="detail-value">{(prediction.confidence_level * 100).toFixed(0)}%</div>
                </div>
              </div>

              {/* 고객 구성 */}
              <div className="guest-composition">
                <div className="composition-title">고객 구성</div>
                <div className="composition-grid">
                  <div className="composition-item">
                    <span className="comp-label">성인</span>
                    <span className="comp-value">{prediction.details.adults}명</span>
                  </div>
                  <div className="composition-item">
                    <span className="comp-label">아동</span>
                    <span className="comp-value">{prediction.details.children}명</span>
                  </div>
                  <div className="composition-item">
                    <span className="comp-label">유아</span>
                    <span className="comp-value">{prediction.details.babies}명</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🍳</div>
              <h3>날짜를 선택해주세요</h3>
              <p>캘린더에서 날짜를 클릭하면 조식 예측 결과를 확인할 수 있습니다</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

export default BreakfastPrediction;
