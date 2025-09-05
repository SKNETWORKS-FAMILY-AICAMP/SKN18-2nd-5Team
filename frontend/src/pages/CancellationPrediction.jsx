import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import { motion } from 'framer-motion';
import { format, addMonths, subMonths } from 'date-fns';
import { ko } from 'date-fns/locale';
import { AlertCircle, TrendingDown, Users, Coffee, Calendar as CalendarIcon } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import 'react-calendar/dist/Calendar.css';
import './CancellationPrediction.css';

function CancellationPrediction() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [prediction, setPrediction] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hotelType, setHotelType] = useState('Resort Hotel');

  useEffect(() => {
    fetchMonthlyData(selectedDate);
  }, [selectedDate]);

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
      toast.success('예측 완료!');
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
      
      if (dayData && dayData.bookings > 0) {
        return (
          <div className="calendar-tile-content">
            <div className="booking-count">{dayData.bookings}</div>
            <div className="cancel-rate">
              {(dayData.cancellation_rate * 100).toFixed(0)}%
            </div>
          </div>
        );
      }
    }
    return null;
  };

  const getRiskLevel = (cancellationRate) => {
    if (cancellationRate > 0.5) return { level: '높음', color: '#ef4444' };
    if (cancellationRate > 0.3) return { level: '중간', color: '#f59e0b' };
    return { level: '낮음', color: '#22c55e' };
  };

  return (
    <div className="cancellation-page">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="page-header glass-card"
      >
        <h1>📊 호텔 예약 취소 예측</h1>
        <p>날짜를 선택하여 예약 취소율을 예측하고 운영 전략을 수립하세요</p>
      </motion.div>

      <div className="content-grid">
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

          <div className="calendar-legend">
            <div className="legend-item">
              <div className="legend-color booking"></div>
              <span>예약 건수</span>
            </div>
            <div className="legend-item">
              <div className="legend-color cancel"></div>
              <span>취소율 %</span>
            </div>
          </div>
        </motion.div>

        {/* Prediction Results */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="results-section"
        >
          {loading && (
            <div className="loading-state glass-card">
              <div className="spinner"></div>
              <p>예측 중...</p>
            </div>
          )}

          {prediction && !loading && (
            <>
              {/* Main Prediction Card */}
              <div className="prediction-card glass-card">
                <div className="prediction-header">
                  <h2>{format(selectedDate, 'yyyy년 MM월 dd일', { locale: ko })}</h2>
                  <div className="hotel-type-badge">{hotelType}</div>
                </div>

                <div className="prediction-metrics">
                  <div className="metric-card">
                    <div className="metric-icon">
                      <CalendarIcon size={20} />
                    </div>
                    <div className="metric-info">
                      <span className="metric-label">총 예약</span>
                      <span className="metric-value">{prediction.total_reservations}</span>
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-icon cancel">
                      <TrendingDown size={20} />
                    </div>
                    <div className="metric-info">
                      <span className="metric-label">예상 취소</span>
                      <span className="metric-value">{prediction.predicted_cancellations}</span>
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-icon success">
                      <Users size={20} />
                    </div>
                    <div className="metric-info">
                      <span className="metric-label">예상 체크인</span>
                      <span className="metric-value">{prediction.expected_checkins}</span>
                    </div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-icon breakfast">
                      <Coffee size={20} />
                    </div>
                    <div className="metric-info">
                      <span className="metric-label">조식 준비</span>
                      <span className="metric-value">{prediction.breakfast_recommendation}인분</span>
                    </div>
                  </div>
                </div>

                {/* Confidence Meter */}
                <div className="confidence-section">
                  <h3>예측 신뢰도</h3>
                  <div className="confidence-meter">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${prediction.confidence_level * 100}%` }}
                    ></div>
                  </div>
                  <span className="confidence-text">
                    {(prediction.confidence_level * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Risk Assessment */}
              <div className="risk-card glass-card">
                <h3>
                  <AlertCircle size={20} />
                  리스크 평가
                </h3>
                {prediction.details && (
                  <div className="risk-details">
                    <div className="risk-item">
                      <span>취소 확률:</span>
                      <span className="risk-value">
                        {(prediction.details.avg_cancellation_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="risk-item">
                      <span>리스크 레벨:</span>
                      <span 
                        className="risk-level"
                        style={{ 
                          color: getRiskLevel(prediction.details.avg_cancellation_probability).color 
                        }}
                      >
                        {getRiskLevel(prediction.details.avg_cancellation_probability).level}
                      </span>
                    </div>
                    <div className="risk-item">
                      <span>총 투숙객:</span>
                      <span>{prediction.details.total_guests}명</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              <div className="recommendations-card glass-card">
                <h3>💡 운영 제안</h3>
                <ul className="recommendations-list">
                  {prediction.predicted_cancellations > prediction.total_reservations * 0.4 && (
                    <li>높은 취소율이 예상됩니다. 오버부킹을 고려해보세요.</li>
                  )}
                  {prediction.breakfast_recommendation > 0 && (
                    <li>조식을 {prediction.breakfast_recommendation}인분 준비하세요.</li>
                  )}
                  {prediction.expected_checkins < prediction.total_reservations * 0.5 && (
                    <li>체크인율이 낮을 것으로 예상됩니다. 확인 전화를 권장합니다.</li>
                  )}
                  {prediction.confidence_level > 0.8 && (
                    <li>높은 신뢰도의 예측입니다. 이 데이터를 기반으로 계획을 수립하세요.</li>
                  )}
                </ul>
              </div>
            </>
          )}

          {!prediction && !loading && (
            <div className="empty-state glass-card">
              <CalendarIcon size={48} color="#999" />
              <h3>날짜를 선택해주세요</h3>
              <p>캘린더에서 날짜를 클릭하면 예약 취소 예측을 확인할 수 있습니다</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

export default CancellationPrediction;
