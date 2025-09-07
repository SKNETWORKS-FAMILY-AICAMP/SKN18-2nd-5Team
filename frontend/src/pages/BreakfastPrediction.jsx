import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import axios from 'axios';
import toast from 'react-hot-toast';
import 'react-calendar/dist/Calendar.css';
import './BreakfastPrediction.css';

function BreakfastPrediction() {
  const [selectedDate, setSelectedDate] = useState(new Date('2017-04-01'));
  const [prediction, setPrediction] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hotelType, setHotelType] = useState('Resort Hotel');
  const [viewMode, setViewMode] = useState('daily');
  const [availableDates, setAvailableDates] = useState([]);
  const [dateRange, setDateRange] = useState({ min: null, max: null });

  useEffect(() => {
    fetchAvailableDates();
  }, []);

  useEffect(() => {
    fetchMonthlyData(selectedDate);
  }, [selectedDate, viewMode]);

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

  const fetchMonthlyData = async (date) => {
    try {
      const response = await axios.get('http://localhost:8000/api/calendar/monthly', {
        params: {
          year: date.getFullYear(),
          month: date.getMonth() + 1,
        },
      });
      setMonthlyData(response.data);
    } catch (error) {
      console.error('Error fetching monthly data:', error);
    }
  };

  const handleDateClick = async (date) => {
    const formattedDate = format(date, 'yyyy-MM-dd');
    
    // 사용 가능한 날짜인지 확인
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

  // 캘린더 타일 비활성화 함수
  const tileDisabled = ({ date, view }) => {
    if (view === 'month') {
      const formattedDate = format(date, 'yyyy-MM-dd');
      return !availableDates.includes(formattedDate);
    }
    return false;
  };

  const getTileContent = ({ date, view }) => {
    if (view === 'month' && monthlyData) {
      const day = date.getDate();
      const dayData = monthlyData.daily_statistics?.find(d => d.day === day);
      
      if (dayData && dayData.breakfast_count > 0) {
        return (
          <div className="calendar-tile-breakfast">
            <span className="tile-count">{dayData.breakfast_count}</span>
          </div>
        );
      }
    }
    return null;
  };

  return (
    <div className="breakfast-modern-container">
      <div className="background-elements">
        <div className="floating-element element-1">☕</div>
        <div className="floating-element element-2">🥐</div>
        <div className="floating-element element-3">🍳</div>
        <div className="floating-element element-4">🥛</div>
        <div className="floating-element element-5">🧈</div>
        <div className="floating-element element-6">🍓</div>
      </div>

      <div className="main-content-wrapper">
        <div className="content-section">
          {/* 헤더 */}
          <motion.div 
            className="monopoly-header"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1>조회를 원하시는 날짜를 선택해 주세요</h1>
          </motion.div>

          {/* 날짜 조회 버튼 */}
          <motion.button 
            className="date-query-button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleDateClick(selectedDate)}
          >
            날짜 조회
          </motion.button>

          {/* 메인 정보 그리드 */}
          <div className="modern-info-grid">
            {/* 캘린더 카드 */}
            <motion.div 
              className="calendar-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="calendar-header">
                {prediction ? format(selectedDate, 'yyyy.MM.dd') : '0000.00.00'}
              </div>
              <div className="mini-calendar">
                <div className="calendar-days">
                  <div className="day-header">S</div>
                  <div className="day-header">M</div>
                  <div className="day-header">T</div>
                  <div className="day-header">W</div>
                  <div className="day-header">T</div>
                  <div className="day-header">F</div>
                  <div className="day-header">S</div>
                </div>
                <Calendar
                  onChange={handleDateClick}
                  value={selectedDate}
                  locale="ko-KR"
                  tileContent={getTileContent}
                  tileDisabled={tileDisabled}
                  minDate={dateRange.min}
                  maxDate={dateRange.max}
                  className="monopoly-calendar"
                />
              </div>
            </motion.div>

            {/* 예측 결과 카드 */}
            <motion.div 
              className="prediction-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="prediction-header">해당일 예약 고객수</div>
              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                </div>
              ) : (
                <div className="prediction-details">
                  <div className="prediction-main">
                    <div className="prediction-value">
                      {prediction ? `${prediction.total_reservations}명` : '00명'}
                    </div>
                    <div className="prediction-sublabel">총 예약</div>
                  </div>
                  
                  {prediction && (
                    <div className="guest-breakdown">
                      <div className="guest-item">
                        <span className="guest-label">성인:</span>
                        <span className="guest-count">{prediction.details.adults}명</span>
                      </div>
                      <div className="guest-item">
                        <span className="guest-label">아동:</span>
                        <span className="guest-count">{prediction.details.children}명</span>
                      </div>
                      <div className="guest-item">
                        <span className="guest-label">유아:</span>
                        <span className="guest-count">{prediction.details.babies}명</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </motion.div>

            {/* 상세 정보 카드들 */}
            <motion.div 
              className="info-cards-container"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              {/* 예약 고객 수 */}
              <div className="info-card">
                <div className="info-label">예약 고객 수</div>
                <div className="info-main">
                  {prediction ? `${prediction.total_reservations}명` : '00명'}
                </div>
                <div className="info-detail">
                  {prediction ? `(성인 ${prediction.details.adults}명 + 아이 ${prediction.details.children}명)` : '(성인 00명 + 아이 00명)'}
                </div>
              </div>

              {/* 조식 예약 고객 수 */}
              <div className="info-card">
                <div className="info-label">조식 예약 고객 수</div>
                <div className="info-main">
                  {prediction ? `${prediction.details.breakfast_guests || 0}명` : '00명'}
                </div>
                <div className="info-detail">
                  {prediction ? `(성인 ${prediction.details.breakfast_adults || 0}명 + 아이 ${prediction.details.breakfast_children || 0}명)` : '(성인 00명 + 아이 00명)'}
                </div>
              </div>

              {/* AI 취소확률 예측 */}
              <div className="info-card highlight-card">
                <div className="info-label">AI 취소확률 예측</div>
                <div className="info-main percentage-value">
                  {prediction ? `${(prediction.details.avg_cancellation_probability * 100).toFixed(0)}%` : '00%'}
                </div>
                <div className="info-detail">
                  머신러닝 기반 예측
                </div>
              </div>

              {/* 예상 실 체크인 고객 수 */}
              <div className="info-card">
                <div className="info-label">예상 실 체크인 고객 수</div>
                <div className="info-main">
                  {prediction ? `${prediction.details.expected_total_guests}명` : '00명'}
                </div>
                <div className="info-detail">
                  {prediction ? `(성인 ${prediction.details.expected_adults}명 + 아이 ${prediction.details.expected_children}명)` : '(성인 00명 + 아이 00명)'}
                </div>
              </div>

              {/* 예상 조식 준비량 */}
              <div className="info-card final-card">
                <div className="info-label">예상 조식 준비량</div>
                <div className="info-main final-value">
                  {prediction ? `${prediction.breakfast_recommendation}인분` : '00인분'}
                </div>
                <div className="info-detail">
                  {prediction ? `(성인 ${prediction.details.expected_breakfast_adults || 0}인분 + 아이 ${prediction.details.expected_breakfast_children || 0}인분)` : '(성인 00인분 + 아이 00인분)'}
                </div>
              </div>

              {/* 추가 통계 정보 */}
              <div className="info-card stats-card">
                <div className="info-label">📊 추가 통계 정보</div>
                <div className="stats-grid-mini">
                  <div className="stat-mini">
                    <span className="stat-mini-label">예약 건수</span>
                    <span className="stat-mini-value">{prediction ? `${prediction.details.total_bookings}건` : '00건'}</span>
                  </div>
                  <div className="stat-mini">
                    <span className="stat-mini-label">유아 수</span>
                    <span className="stat-mini-value">{prediction ? `${prediction.details.babies}명` : '00명'}</span>
                  </div>
                  <div className="stat-mini">
                    <span className="stat-mini-label">신뢰도</span>
                    <span className="stat-mini-value">{prediction ? `${(prediction.confidence_level * 100).toFixed(0)}%` : '00%'}</span>
                  </div>
                  <div className="stat-mini">
                    <span className="stat-mini-label">조식 이용률</span>
                    <span className="stat-mini-value">{prediction && prediction.details.total_guests > 0 ? `${((prediction.details.breakfast_guests / prediction.details.total_guests) * 100).toFixed(0)}%` : '00%'}</span>
                  </div>
                </div>
              </div>
            </motion.div>

          </div>

          {/* 추가 정보 및 컨트롤 */}
          <div className="controls-section">
            {/* 뷰 모드 선택 버튼들 */}
            <div className="view-mode-buttons">
              <button 
                className={`mode-button ${viewMode === 'daily' ? 'active' : ''}`}
                onClick={() => setViewMode('daily')}
              >
                일별
              </button>
              <button 
                className={`mode-button ${viewMode === 'weekly' ? 'active' : ''}`}
                onClick={() => setViewMode('weekly')}
              >
                주간
              </button>
              <button 
                className={`mode-button ${viewMode === 'monthly' ? 'active' : ''}`}
                onClick={() => setViewMode('monthly')}
              >
                월간
              </button>
            </div>

            {/* 호텔 타입 선택 */}
            <div className="hotel-selector">
              <select 
                value={hotelType} 
                onChange={(e) => setHotelType(e.target.value)}
                className="hotel-select-modern"
              >
                <option value="Resort Hotel">리조트 호텔</option>
                <option value="City Hotel">시티 호텔</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BreakfastPrediction;