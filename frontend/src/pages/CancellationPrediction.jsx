import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { Search } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import Header from '../components/Header';
import './CancellationPrediction.css';

function CancellationPrediction() {
  const [searchDate, setSearchDate] = useState('2017-04-01'); // 데이터가 있는 날짜로 초기화
  const [bookingList, setBookingList] = useState([]);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [dailyStatistics, setDailyStatistics] = useState(null);
  const [currentOffset, setCurrentOffset] = useState(0);

  useEffect(() => {
    // 초기 로드 시 데이터가 있는 날짜로 예약 조회
    const initialDate = new Date('2017-04-01');
    fetchBookingsByDate(initialDate);
  }, []);

  const fetchBookingsByDate = async (date) => {
    setLoading(true);
    try {
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const day = date.getDate();
      const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

      // 예약 목록과 예측 통계 병렬 호출
      const [bookingsResponse, predictionResponse] = await Promise.all([
        axios.get('http://localhost:8000/api/bookings/by-date', {
          params: {
            year,
            month,
            day,
            offset: currentOffset,
            limit: 100
          }
        }),
        axios.post('http://localhost:8000/api/predict/date', {
          date: formattedDate,
          hotel_type: 'Resort Hotel',
        })
      ]);

      if (bookingsResponse.data.success) {
        setBookingList(bookingsResponse.data.data || []);
        setTotalCount(bookingsResponse.data.total_count || 0);
        setSelectedBooking(bookingsResponse.data.data && bookingsResponse.data.data.length > 0 ? bookingsResponse.data.data[0] : null);
        // 예측 통계 저장
        setDailyStatistics(predictionResponse.data);
        if (bookingsResponse.data.total_count > 0) {
          toast.success(`${bookingsResponse.data.total_count}건의 예약을 찾았습니다.`);
        } else {
          toast.info('해당 날짜에 예약 데이터가 없습니다.');
        }
      }
    } catch (error) {
      setBookingList([]);
      setSelectedBooking(null);
      setTotalCount(0);
      setDailyStatistics(null);
      toast.error('예약 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDateSearch = () => {
    const date = new Date(searchDate);
    setCurrentOffset(0);
    fetchBookingsByDate(date);
  };

  const handleBookingClick = (booking) => {
    setSelectedBooking(booking);
  };

  const getRiskLevel = (probability) => {
    if (!probability) return 'unknown';
    if (probability > 0.7) return 'high';
    if (probability > 0.4) return 'medium';
    return 'low';
  };

  return (
    <div className="cancellation-page">
      <Header 
        title="CUSTOMER MANAGEMENT"
        subtitle="날짜를 선택하여 고객을 확인하고 운영 전략을 수립하세요"
      />

      <div className="main-content">
        {/* 중앙 테이블 */}
        <div className="table-section">
          <div className="table-container glass-card">
            <div className="table-header">
              <span className="page-title">고객 관리 페이지</span>
              <h2>
                <div className="search-input-wrapper">
                  <Search size={20} />
                  <input
                    type="date"
                    value={searchDate}
                    onChange={(e) => setSearchDate(e.target.value)}
                    className="date-input"
                  />
                <button onClick={handleDateSearch} className="search-button">
                검색
              </button>
              </div>
              </h2>
              <span className="total-count">총 {totalCount}건</span>
            </div>

            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>데이터를 불러오는 중...</p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table className="booking-table">
                  <thead>
                    <tr>
                      <th>이름</th>
                      <th>전화번호</th>
                      <th>인원</th>
                      <th>예약일자</th>
                      <th>숙박일수</th>
                      <th>방 종류</th>
                      <th>조식 여부</th>
                      <th>특별요청사항</th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* 실제 데이터가 있을 때 */}
                    {bookingList.map((booking, index) => (
                      <tr 
                        key={booking.reservation_id || index}
                        className={`booking-row ${selectedBooking?.reservation_id === booking.reservation_id ? 'selected' : ''}`}
                        onClick={() => handleBookingClick(booking)}
                      >
                        <td>{booking.name || '-'}</td>
                        <td>{booking.phone || '-'}</td>
                        <td>{booking.total_guests || '-'}</td>
                        <td>{booking.arrival_date || '-'}</td>
                        <td>{booking.total_nights ? `${booking.total_nights}박` : '-'}</td>
                        <td>{booking.room_type || '-'}</td>
                        <td>
                          <span className={`meal-badge ${booking.meal === '포함' ? 'included' : 'not-included'}`}>
                            {booking.meal || '-'}
                          </span>
                        </td>
                        <td>{booking.special_requests || '-'}</td>
                      </tr>
                    ))}
                    
                    {/* 데이터가 부족하거나 없을 때 빈 행으로 채우기 (최소 10개 행 유지) */}
                    {Array.from({ length: Math.max(0, 10 - bookingList.length) }).map((_, i) => (
                      <tr className="placeholder-row" key={`empty-${i}`}>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* 더 많은 데이터가 있을 경우 스크롤 안내 */}
            {totalCount > 10 && (
              <div className="scroll-indicator">
                <p>↓ 스크롤하여 더 많은 예약을 확인하세요 ({bookingList.length}/{totalCount})</p>
              </div>
            )}
          </div>

          {/* 하단 통계 영역 */}
          <div className="statistics-section glass-card">
            <div className="statistics-grid">
              {/* 좌측 카드: 총 인원 */}
              <div className="stat-card left-card">
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">총 인원</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.details?.total_guests ? `${dailyStatistics.details.total_guests}명` : '-'}
                    </span>
                  </div>
                </div>
              </div>
              {/* 중앙 카드: 투숙중 총 인원, 예상 투숙 인원 */}
              <div className="stat-card center-card">
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">투숙중 총 인원</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.details?.total_guests ? `${dailyStatistics.details.total_guests}명` : '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">예상 투숙 인원</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.expected_checkins ? `${dailyStatistics.expected_checkins}명` : '-'}
                    </span>
                  </div>
                </div>
              </div>
              {/* 우측 카드: 예상 조식 인원수 */}
              <div className="stat-card right-card">
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">예상 조식 인원수</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.breakfast_recommendation ? `${dailyStatistics.breakfast_recommendation}명` : '-'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CancellationPrediction;