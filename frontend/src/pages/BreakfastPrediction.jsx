import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import { motion } from 'framer-motion';
import { format, startOfWeek, endOfWeek, eachDayOfInterval } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Coffee, Users, TrendingUp, Calendar as CalendarIcon, Utensils, AlertTriangle, Droplet, Zap, Wine, Package, Palette } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement } from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import axios from 'axios';
import toast from 'react-hot-toast';
import 'react-calendar/dist/Calendar.css';
import './BreakfastPrediction.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement);

function BreakfastPrediction() {
  const [selectedDate, setSelectedDate] = useState(new Date('2017-04-01'));
  const [prediction, setPrediction] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
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
    if (viewMode === 'weekly') {
      fetchWeeklyData();
    }
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

  const fetchWeeklyData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/trends/weekly');
      setWeeklyData(response.data.weekly_trends);
    } catch (error) {
      console.error('Error fetching weekly data:', error);
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

  const calculateWeeklyBreakfast = () => {
    if (!monthlyData) return [];
    
    const weekStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
    const weekEnd = endOfWeek(selectedDate, { weekStartsOn: 1 });
    const weekDays = eachDayOfInterval({ start: weekStart, end: weekEnd });
    
    return weekDays.map(day => {
      const dayData = monthlyData.daily_statistics?.find(
        d => d.day === day.getDate() && 
        day.getMonth() === selectedDate.getMonth()
      );
      return {
        date: format(day, 'MM/dd'),
        breakfast: dayData?.breakfast_count || 0,
        guests: dayData?.total_guests || 0,
      };
    });
  };

  const weeklyBreakfastData = calculateWeeklyBreakfast();

  const breakfastDistribution = prediction && {
    labels: ['조식 이용', '조식 미이용'],
    datasets: [
      {
        data: [
          prediction.breakfast_recommendation,
          prediction.expected_checkins - prediction.breakfast_recommendation,
        ],
        backgroundColor: ['#f59e0b', '#e5e7eb'],
        borderColor: ['#d97706', '#d1d5db'],
        borderWidth: 2,
      },
    ],
  };

  const getBreakfastRecommendation = () => {
    if (!prediction) return null;
    
    const ratio = prediction.breakfast_recommendation / prediction.expected_checkins;
    
    if (ratio > 0.8) {
      return {
        level: '높음',
        color: '#ef4444',
        message: '많은 조식 인원이 예상됩니다.',
      };
    } else if (ratio > 0.5) {
      return {
        level: '보통',
        color: '#f59e0b',
        message: '평균적인 조식 인원이 예상됩니다.',
      };
    } else {
      return {
        level: '낮음',
        color: '#22c55e',
        message: '조식 인원이 적을 것으로 예상됩니다.',
      };
    }
  };

  // 모노폴리 스타일 카드 데이터
  const monopolyCards = [
    { icon: <Droplet />, title: 'WATER\nWORKS', price: 'M150', color: '#87CEEB', id: 'water' },
    { icon: <Zap />, title: 'ELECTRIC\nCOMPANY', price: 'M150', color: '#FFD700', id: 'electric' },
    { icon: <Palette />, title: 'CUSTOM', price: 'M100', color: '#98FB98', id: 'custom1' },
    { icon: <Package />, title: 'IRN BRU', price: 'M150', color: '#FFA500', id: 'irnbru' },
    { icon: <Wine />, title: 'ALCOHOL', price: 'M150', color: '#DDA0DD', id: 'alcohol' },
    { icon: <Coffee />, title: 'CUSTOM', price: 'M100', color: '#F0E68C', id: 'custom2' },
  ];

  return (
    <div className="breakfast-monopoly-container">
      <div className="monopoly-board">
        {/* 왼쪽 카드 섹션 */}
        <div className="monopoly-left-section">
          <div className="property-cards">
            {monopolyCards.map((card, index) => (
              <motion.div
                key={card.id}
                className="property-card"
                style={{ backgroundColor: card.color }}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, rotate: 2 }}
              >
                <div className="card-icon">{card.icon}</div>
                <div className="card-title">{card.title}</div>
                <div className="card-price">{card.price}</div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* 오른쪽 메인 콘텐츠 */}
        <div className="monopoly-right-section">
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

          {/* 메인 정보 카드 */}
          <div className="main-info-grid">
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

          {/* 추가 정보 */}
          <motion.div 
            className="additional-info"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <p>식재료 추가 준비가 필요합니다.</p>
          </motion.div>

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
              className="hotel-select-monopoly"
            >
              <option value="Resort Hotel">리조트 호텔</option>
              <option value="City Hotel">시티 호텔</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BreakfastPrediction;