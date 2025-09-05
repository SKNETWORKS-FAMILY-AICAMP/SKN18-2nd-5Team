import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { TrendingDown, Coffee, BarChart3, Calendar, Users, Shield } from 'lucide-react';
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

  const features = [
    {
      icon: <TrendingDown size={40} color="white" />,
      title: '취소 예측',
      description: '머신러닝을 활용한 정확한 예약 취소 확률 예측',
      link: '/cancellation',
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    },
    {
      icon: <Coffee size={40} color="white" />,
      title: '조식 준비',
      description: '일별 조식 준비 인원을 정확하게 예측',
      link: '/breakfast',
      color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    },
    {
      icon: <BarChart3 size={40} color="white" />,
      title: '실시간 분석',
      description: '예약 데이터의 실시간 통계 분석',
      link: '/cancellation',
      color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    },
  ];

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
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="hero-section glass-card"
      >
        <h1>🏨 HotelPredict AI</h1>
        <p>인공지능 기반 호텔 예약 관리 시스템</p>
        <p className="hero-subtitle">
          머신러닝을 활용하여 예약 취소를 예측하고, 조식 준비 인원을 최적화하세요
        </p>
        <div className="hero-buttons">
          <Link to="/cancellation" className="btn btn-primary">
            <Shield size={20} />
            지금 시작하기
          </Link>
          <Link to="/breakfast" className="btn btn-secondary">
            <Coffee size={20} />
            조식 예측하기
          </Link>
        </div>
      </motion.div>

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

      {/* Features Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <h2 className="section-title">✨ 주요 기능</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              whileHover={{ scale: 1.05 }}
              className="feature-card"
            >
              <Link to={feature.link} style={{ textDecoration: 'none', color: 'inherit' }}>
                <div 
                  className="feature-icon" 
                  style={{ background: feature.color }}
                >
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Loading State */}
      {loading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
}

export default HomePage;
