import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Search, Calendar as CalendarIcon } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './GuestManagement.css';

function GuestManagement({ sidebarOpen }) {
  const [bookingList, setBookingList] = useState([]);
  const [searchDate, setSearchDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [currentOffset, setCurrentOffset] = useState(0);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [dailyStatistics, setDailyStatistics] = useState(null);

  useEffect(() => {
    // 초기 로드 시 오늘 날짜의 예약 조회
    const today = new Date();
    fetchBookingsByDate(today);
  }, []);

  const fetchBookingsByDate = async (date) => {
    setLoading(true);
    try {
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const day = date.getDate();

      const response = await axios.get('http://localhost:8000/api/bookings/by-date', {
        params: {
          year,
          month,
          day,
          offset: currentOffset,
          limit: 10
        }
      });

      console.log('API Response:', response.data); // 디버깅 로그 추가

      if (response.data.success) {
        setBookingList(response.data.data);
        setTotalCount(response.data.total_count);
        setDailyStatistics(response.data.statistics);
        console.log('Booking list set:', response.data.data); // 디버깅 로그 추가
        console.log('Statistics set:', response.data.statistics); // 디버깅 로그 추가
        
        // 첫 번째 예약을 기본으로 선택
        if (response.data.data && response.data.data.length > 0) {
          setSelectedBooking(response.data.data[0]);
        }
      } else {
        console.log('API returned success: false'); // 디버깅 로그 추가
      }
    } catch (error) {
      console.error('Error fetching bookings:', error);
      toast.error('예약 정보를 불러오는데 실패했습니다.');
      setBookingList([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDateSearch = () => {
    const date = new Date(searchDate);
    setCurrentOffset(0);
    fetchBookingsByDate(date);
  };

  const handleFilter = (filterType) => {
    // 필터링 로직 (추후 구현)
    console.log('Filter applied:', filterType);
    toast.info(`${filterType} 필터가 적용되었습니다.`);
  };

  const getRiskLevel = (probability) => {
    if (!probability) return 'unknown';
    if (probability > 0.7) return 'high';
    if (probability > 0.4) return 'medium';
    return 'low';
  };

  const handleBookingClick = (booking) => {
    setSelectedBooking(booking);
  };

  return (
    <div className="guest-management-page">
      {/* 상단 검색바 */}
      <div className="search-header glass-card">
        <div className="search-container">
          <h1 className="page-title">고객 관리 페이지</h1>
        </div>
      </div>

      <div className="main-content">
        {/* 중앙 테이블 */}
        <div className={`table-section ${sidebarOpen ? 'sidebar-open' : ''}`}>
          <div className="table-container glass-card">
            <div className="table-header">
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
            {/* <h3>통계 정보</h3> */}
            <div className="statistics-grid">
              {/* 좌측 카드: 예약 1개 정보 - 조식관련 */}
              <div className="stat-card left-card">
                {/* <h4>고객 예약 정보 - 조식</h4> */}
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">어른/아이</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {selectedBooking ? 
                        `${selectedBooking.total_guests - (selectedBooking.babies || 0)}명` : 
                        '-'
                      }
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">조식 종류</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {selectedBooking?.meal || '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">특별요청사항</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {selectedBooking?.special_requests || '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">고객 위험도</span>
                    <span className="stat-divider"></span>
                    <span className={`stat-value risk-level ${getRiskLevel(selectedBooking?.predicted_probability)}`}>
                      {selectedBooking?.predicted_probability ? 
                        `${(selectedBooking.predicted_probability * 100).toFixed(1)}%` : 
                        '-'
                      }
                    </span>
                  </div>
                </div>
              </div>

              {/* 중앙 카드: 예약 1개 정보 - 숙박관련 */}
              <div className="stat-card center-card">
                {/* <h4>고객 예약 정보 - 숙박</h4> */}
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">체크인/체크아웃</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">-</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">투숙중인 층 인원</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {selectedBooking?.total_guests ? `${selectedBooking.total_guests}명` : '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">배정 가능 잔여 객실</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">-</span>
                  </div>
                </div>
              </div>

              {/* 우측 카드: 해당일 전체 통계 */}
              <div className="stat-card right-card">
                {/* <h4>해당일 전체 통계</h4> */}
                <div className="stat-items">
                  <div className="stat-item">
                    <span className="stat-label">날짜</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {searchDate ? format(new Date(searchDate), 'yyyy.MM.dd') : '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">모델 예측 신뢰도</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.model_confidence ? `${dailyStatistics.model_confidence}%` : '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">예상 투숙 인원</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.total_expected_guests ? `${dailyStatistics.total_expected_guests}명` : '-'}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">예상 조식 인원수</span>
                    <span className="stat-divider"></span>
                    <span className="stat-value">
                      {dailyStatistics?.breakfast_preparation_count ? `${dailyStatistics.breakfast_preparation_count}명` : '-'}
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

export default GuestManagement;
