import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const handleBreakfastClick = () => {
    navigate('/breakfast');
  };

  const handleCancellationClick = () => {
    navigate('/cancellation');
  };

  // 페이지 이동 수정!!
  const handleReservationClick = () => {
    navigate('/cancellation');
  };

  return (
    <div className="hotel-management-homepage">
      <Header 
        title="GRAND HOTEL MONOPOLY"
        subtitle="AI 기반 스마트 호텔 관리 시스템"
      />
      
      {/* Main Container */}
      <div className="main-container">
        {/* Central Board - Full Screen */}
        <div className="board-container">
          <img 
            src="/images/broad_all.png" 
            alt="Hotel Management System Board" 
            className="board-image"
          />
        </div>

        {/* HotelPredict AI Title - Center */}
        <div className="title-container">
          <h1 className="main-title">HotelPredict AI</h1>
          <p className="subtitle">AI 기반 스마트 호텔 관리 시스템</p>
        </div>

        {/* Corner Cards - Four corners with exact positioning */}
        <div className="corner-cards-container">
          {/* Top Left - Light Blue Card */}
          <motion.div 
            className="corner-card top-left-card"
            onClick={handleBreakfastClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <img 
              src="/images/GroupCard1.png" 
              alt="Breakfast Management System" 
              className="corner-card-image"
            />
          </motion.div>

          {/* Top Right - Pink Card */}
          <motion.div 
            className="corner-card top-right-card"
            onClick={handleCancellationClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <img 
              src="/images/PropertyCardPink.png" 
              alt="Cancellation Prediction" 
              className="corner-card-image"
            />
          </motion.div>

          {/* Bottom Left - Blue Card */}
          <motion.div 
            className="corner-card bottom-left-card"
            onClick={handleCancellationClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <img 
              src="/images/PropertyCardBlue.png" 
              alt="Cancellation Analysis" 
              className="corner-card-image"
            />
          </motion.div>

          {/* Bottom Right - Yellow Card */}
          <motion.div 
            className="corner-card bottom-right-card"
            onClick={handleReservationClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <img 
              src="/images/GroupCard2.png" 
              alt="Breakfast Management" 
              className="corner-card-image"
            />
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;