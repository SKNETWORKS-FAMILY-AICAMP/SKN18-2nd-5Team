import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import './Header.css';

function Header({ title, subtitle }) {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { path: '/', label: '홈', icon: '🏛️' },
    { path: '/cancellation', label: '고객관리 페이지', icon: '📋' },
    { path: '/breakfast', label: '조식예측', icon: '🥂' }
  ];

  const handleNavigation = (path) => {
    if (location.pathname !== path) {
      navigate(path);
    }
  };

  return (
    <motion.div 
      className="hotel-header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="header-left">
        <div className="hotel-logo" onClick={() => handleNavigation('/')}>
          🏨
        </div>
      </div>

      <div className="header-center">
        <h1>{title || 'GRAND HOTEL MONOPOLY'}</h1>
        <div className="decorative-line"></div>
        <div className="hotel-name">{subtitle || '호텔 관리 시스템'}</div>
      </div>

      <div className="header-right">
        <nav className="navigation-menu">
          {navigationItems.map((item) => (
            <motion.button
              key={item.path}
              className={`nav-button ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => handleNavigation(item.path)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </motion.button>
          ))}
        </nav>

        <div className="hotel-icons">
          <span>👑</span>
          <span>⭐</span>
          <span>💎</span>
        </div>
      </div>
    </motion.div>
  );
}

export default Header;
