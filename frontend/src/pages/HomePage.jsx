import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingDown, Calendar, Users, Building2 } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import axios from 'axios';
import './HomePage.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

function HomePage() {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/statistics/overview');
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setLoading(false);
    }
  };


  const statsCards = [
    {
      title: '총 예약 건수',
      value: statistics?.total_bookings?.toLocaleString() || '0',
      icon: <Calendar size={24} />,
      color: '#667eea',
    },
    {
      title: '평균 취소율',
      value: statistics ? `${(statistics.overall_cancellation_rate * 100).toFixed(1)}%` : '0%',
      icon: <TrendingDown size={24} />,
      color: '#f5576c',
    },
    {
      title: '평균 리드타임',
      value: statistics ? `${Math.round(statistics.average_lead_time)}일` : '0일',
      icon: <Users size={24} />,
      color: '#4facfe',
    },
  ];

  const chartData = statistics && {
    labels: ['예약 완료', '예약 취소'],
    datasets: [
      {
        data: [
          statistics.total_bookings * (1 - statistics.overall_cancellation_rate),
          statistics.total_bookings * statistics.overall_cancellation_rate,
        ],
        backgroundColor: ['#22c55e', '#ef4444'],
        borderColor: ['#16a34a', '#dc2626'],
        borderWidth: 2,
      },
    ],
  };

  const monthlyChartData = statistics && {
    labels: statistics.monthly_statistics?.map(stat => stat.month) || [],
    datasets: [
      {
        label: '월별 예약 건수',
        data: statistics.monthly_statistics?.map(stat => stat.bookings) || [],
        backgroundColor: 'rgba(102, 126, 234, 0.5)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 2,
      },
    ],
  };

  return (
    <div className="home-page">
      {/* Header Section */}
      <header className="header-section">
        <div className="header-content">
          <div className="hotel-image-container">
            <img 
              src="/images/hotel_main.jpg"
              alt="HotelPredict AI" 
              className="hotel-image"
            />
            <div className="hotel-overlay">
              <h1 className="hotel-title">
                <span className="hotel-icon">
                  <Building2 size={48} />
                </span>
                HotelPredict AI
              </h1>
              <p className="hotel-subtitle">AI 기반 스마트 호텔 관리 시스템</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-section">
        <div className="main-content-wrapper">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="main-content-card"
          >
            <div className="welcome-section">
              <h2 className="main-title">HotelPredict AI에 오신 것을 환영합니다</h2>
              <p className="main-description">
                HotelPredict AI의 혁신적인 AI 기반 예약 관리 시스템으로 호텔 운영의 효율성을 극대화하세요. <br/>
                머신러닝 기술을 통해 예측 정확도를 높이고, 운영 비용을 절감하며, <br/>
                고객 만족도를 향상시키는 스마트한 솔루션을 제공합니다.
              </p>
            </div>
            
            <div className="services-grid">
              <div className="service-card">
                <div className="service-icon">📈</div>
                <h3>고객 데이터 분석</h3>
                <p>호텔 운영 데이터를 분석하여<br/>즉각적인 의사결정을 지원하는 대시보드를 제공합니다.</p>
              </div>
              
              <div className="service-card">
                <div className="service-icon">🍽️</div>
                <h3>조식 준비 최적화</h3>
                <p>실제 투숙객 수를 기반으로 조식 준비 인원을 자동 계산하여 <br/>식비를 절약하고 낭비를 방지합니다.</p>
              </div>
              
              <div className="service-card">
                <div className="service-icon">📊</div>
                <h3>예약 취소 예측</h3>
                <p>고급 머신러닝 알고리즘을 통해 예약 취소 확률을 예측하여 <br/>수익 손실을 최소화합니다.</p>
              </div>
            </div>
            
            <div className="cta-section">
              <h3>지금 시작하세요</h3>
              <p>HotelPredict AI와 함께 호텔 운영의 새로운 차원을 경험해보세요. <br/>
                 직관적인 인터페이스와 강력한 AI 기술로 더 스마트한 호텔 관리가 가능합니다.</p>
            </div>
          </motion.div>
        </div>
      </main>

      {/* Statistics Overview */}
      {!loading && statistics && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <h2 className="section-title">📊 실시간 통계</h2>
          <div className="stats-grid">
            {statsCards.map((stat, index) => (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.5 }}
                className="stat-card"
                style={{ borderTop: `3px solid ${stat.color}` }}
              >
                <div className="stat-icon" style={{ color: stat.color }}>
                  {stat.icon}
                </div>
                <h3>{stat.title}</h3>
                <div className="value">{stat.value}</div>
              </motion.div>
            ))}
          </div>

          {/* Charts */}
          <div className="charts-row">
            <div className="chart-container">
              <h3>예약 현황</h3>
              <div style={{ maxWidth: '300px', margin: '0 auto' }}>
                <Doughnut data={chartData} />
              </div>
            </div>
            <div className="chart-container">
              <h3>월별 예약 추이</h3>
              <Bar data={monthlyChartData} />
            </div>
          </div>
        </motion.div>
      )}


      {/* Loading State */}
      {loading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      )}

      {/* Footer Section */}
      <footer className="footer-section">
        <div className="footer-content">
          <div className="footer-info">
            <div className="footer-brand">
              <h3>HotelPredict AI</h3>
              <p>AI 기반 스마트 호텔 관리 솔루션</p>
            </div>
            
            <div className="footer-contact">
              <h4>연락처 정보</h4>
              <div className="contact-item">
                <span className="contact-label">전화번호:</span>
                <span className="contact-value">02-1234-5678</span>
              </div>
              <div className="contact-item">
                <span className="contact-label">이메일:</span>
                <span className="contact-value">info@hotelpredict_ai.com</span>
              </div>
              <div className="contact-item">
                <span className="contact-label">주소:</span>
                <span className="contact-value">서울특별시 금천구 가산동 123</span>
              </div>
            </div>
            
            <div className="footer-services">
              <h4>서비스</h4>
              <ul>
                <li>예약 취소 예측</li>
                <li>조식 준비 최적화</li>
                <li>실시간 통계 분석</li>
                <li>고객 관리 시스템</li>
              </ul>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; 2025 HotelPredict AI. All rights reserved.</p>
            <p>Powered by HotelPredict AI Technology</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default HomePage;