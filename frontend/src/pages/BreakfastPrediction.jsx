import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import { motion } from 'framer-motion';
import { format, startOfWeek, endOfWeek, eachDayOfInterval } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Coffee, Users, TrendingUp, Calendar as CalendarIcon, Utensils, AlertTriangle } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement } from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import axios from 'axios';
import toast from 'react-hot-toast';
import 'react-calendar/dist/Calendar.css';
import './BreakfastPrediction.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement);

function BreakfastPrediction() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [prediction, setPrediction] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hotelType, setHotelType] = useState('Resort Hotel');
  const [viewMode, setViewMode] = useState('daily'); // daily, weekly, monthly

  useEffect(() => {
    fetchMonthlyData(selectedDate);
    if (viewMode === 'weekly') {
      fetchWeeklyData();
    }
  }, [selectedDate, viewMode]);

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
    setSelectedDate(date);
    setLoading(true);
    setPrediction(null);

    try {
      const formattedDate = format(date, 'yyyy-MM-dd');
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

  const getTileContent = ({ date, view }) => {
    if (view === 'month' && monthlyData) {
      const day = date.getDate();
      const dayData = monthlyData.daily_statistics?.find(d => d.day === day);
      
      if (dayData && dayData.breakfast_count > 0) {
        return (
          <div className="calendar-tile-breakfast">
            <Coffee size={12} />
            <span>{dayData.breakfast_count}</span>
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

  const weeklyChartData = {
    labels: weeklyBreakfastData.map(d => d.date),
    datasets: [
      {
        label: '조식 인원',
        data: weeklyBreakfastData.map(d => d.breakfast),
        backgroundColor: 'rgba(245, 158, 11, 0.5)',
        borderColor: 'rgba(245, 158, 11, 1)',
        borderWidth: 2,
        tension: 0.4,
      },
    ],
  };

  const weekdayChartData = weeklyData && {
    labels: weeklyData.map(d => d.day),
    datasets: [
      {
        label: '평균 투숙객',
        data: weeklyData.map(d => d.avg_guests),
        backgroundColor: 'rgba(102, 126, 234, 0.5)',
        borderColor: 'rgba(102, 126, 234, 1)',
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
        message: '많은 조식 인원이 예상됩니다. 충분한 준비가 필요합니다.',
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

  return (
    <div className="breakfast-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="page-header glass-card"
      >
        <h1>☕ 호텔 조식 예측 서비스</h1>
        <p>정확한 조식 인원 예측으로 식자재 낭비를 줄이고 고객 만족도를 높이세요</p>
      </motion.div>

      <div className="view-mode-selector">
        <button 
          className={`mode-btn ${viewMode === 'daily' ? 'active' : ''}`}
          onClick={() => setViewMode('daily')}
        >
          일별 예측
        </button>
        <button 
          className={`mode-btn ${viewMode === 'weekly' ? 'active' : ''}`}
          onClick={() => setViewMode('weekly')}
        >
          주간 트렌드
        </button>
        <button 
          className={`mode-btn ${viewMode === 'monthly' ? 'active' : ''}`}
          onClick={() => setViewMode('monthly')}
        >
          월간 통계
        </button>
      </div>

      <div className="breakfast-content-grid">
        {/* Calendar Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="calendar-section glass-card"
        >
          <div className="section-header">
            <CalendarIcon size={24} />
            <h2>날짜 선택</h2>
          </div>
          
          <div className="hotel-type-selector">
            <label>호텔 유형:</label>
            <select 
              value={hotelType} 
              onChange={(e) => setHotelType(e.target.value)}
              className="hotel-select"
            >
              <option value="Resort Hotel">리조트 호텔</option>
              <option value="City Hotel">시티 호텔</option>
            </select>
          </div>

          <div className="calendar-wrapper">
            <Calendar
              onChange={handleDateClick}
              value={selectedDate}
              locale="ko-KR"
              tileContent={getTileContent}
              className="custom-calendar"
            />
          </div>
        </motion.div>

        {/* Results Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="results-section"
        >
          {loading && (
            <div className="loading-state glass-card">
              <div className="spinner"></div>
              <p>조식 인원 예측 중...</p>
            </div>
          )}

          {prediction && !loading && viewMode === 'daily' && (
            <>
              {/* Main Breakfast Card */}
              <div className="breakfast-main-card glass-card">
                <div className="breakfast-header">
                  <h2>{format(selectedDate, 'yyyy년 MM월 dd일', { locale: ko })}</h2>
                  <div className="breakfast-badge">
                    <Utensils size={20} />
                    조식 예측
                  </div>
                </div>

                <div className="breakfast-highlight">
                  <Coffee size={48} />
                  <div className="highlight-content">
                    <span className="highlight-label">추천 조식 준비 인원</span>
                    <span className="highlight-value">{prediction.breakfast_recommendation}인분</span>
                  </div>
                </div>

                <div className="breakfast-details">
                  <div className="detail-item">
                    <Users size={20} />
                    <span>예상 체크인: {prediction.expected_checkins}명</span>
                  </div>
                  <div className="detail-item">
                    <TrendingUp size={20} />
                    <span>조식 이용률: {((prediction.breakfast_recommendation / prediction.expected_checkins) * 100).toFixed(1)}%</span>
                  </div>
                </div>

                {breakfastDistribution && (
                  <div className="chart-section">
                    <h3>조식 이용 분포</h3>
                    <div style={{ maxWidth: '250px', margin: '0 auto' }}>
                      <Pie data={breakfastDistribution} />
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendation Card */}
              {getBreakfastRecommendation() && (
                <div className="recommendation-card glass-card" style={{ borderLeft: `5px solid ${getBreakfastRecommendation().color}` }}>
                  <h3>
                    <AlertTriangle size={20} style={{ color: getBreakfastRecommendation().color }} />
                    조식 준비 권장사항
                  </h3>
                  <div className="recommendation-content">
                    <div className="rec-level" style={{ color: getBreakfastRecommendation().color }}>
                      준비 수준: {getBreakfastRecommendation().level}
                    </div>
                    <p>{getBreakfastRecommendation().message}</p>
                    <ul className="prep-list">
                      <li>🥐 빵류: {Math.ceil(prediction.breakfast_recommendation * 1.5)}개</li>
                      <li>🥚 계란: {Math.ceil(prediction.breakfast_recommendation * 2)}개</li>
                      <li>🥛 우유: {Math.ceil(prediction.breakfast_recommendation * 0.3)}L</li>
                      <li>☕ 커피: {Math.ceil(prediction.breakfast_recommendation * 0.2)}kg</li>
                    </ul>
                  </div>
                </div>
              )}
            </>
          )}

          {viewMode === 'weekly' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="weekly-view glass-card">
                <h2>📊 주간 조식 트렌드</h2>
                <div className="chart-container">
                  <Line data={weeklyChartData} options={{
                    responsive: true,
                    plugins: {
                      legend: { position: 'top' },
                      title: {
                        display: true,
                        text: '주간 조식 인원 추이'
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }} />
                </div>

                {weeklyData && (
                  <div className="chart-container" style={{ marginTop: '30px' }}>
                    <h3>요일별 평균 투숙객</h3>
                    <Bar data={weekdayChartData} options={{
                      responsive: true,
                      plugins: {
                        legend: { display: false }
                      },
                      scales: {
                        y: {
                          beginAtZero: true
                        }
                      }
                    }} />
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {viewMode === 'monthly' && monthlyData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="monthly-view glass-card"
            >
              <h2>📈 월간 조식 통계</h2>
              <div className="monthly-stats">
                <div className="stat-box">
                  <span className="stat-label">총 예약</span>
                  <span className="stat-value">{monthlyData.summary.total_bookings}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">평균 취소율</span>
                  <span className="stat-value">{(monthlyData.summary.average_cancellation_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">예상 조식 총 인원</span>
                  <span className="stat-value">
                    {monthlyData.daily_statistics?.reduce((sum, day) => sum + day.breakfast_count, 0) || 0}명
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {!prediction && !loading && viewMode === 'daily' && (
            <div className="empty-state glass-card">
              <Coffee size={48} color="#999" />
              <h3>날짜를 선택해주세요</h3>
              <p>캘린더에서 날짜를 클릭하면 조식 준비 인원을 예측할 수 있습니다</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

export default BreakfastPrediction;
