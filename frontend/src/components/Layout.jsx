import React from 'react';
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Coffee, 
  TrendingDown, 
  BarChart3, 
  Calendar,
  Settings,
  Menu,
  X,
  Hotel,
  Sun,
  Moon
} from 'lucide-react';
import './Layout.css';

function Layout({ children, sidebarOpen, toggleSidebar }) {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: <Home size={20} />, label: '홈 대시보드' },
    { path: '/breakfast', icon: <Coffee size={20} />, label: '조식 예측' },
    { path: '/cancellation', icon: <TrendingDown size={20} />, label: '취소율 예측' },
    { path: '/statistics', icon: <BarChart3 size={20} />, label: '통계 분석' },
    { path: '/calendar', icon: <Calendar size={20} />, label: '예약 캘린더' },
  ];

  return (
    <div className="layout-container">
      {/* Header */}
      <motion.header 
        className="layout-header"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        <div className="header-left">
          <button className="menu-toggle" onClick={toggleSidebar}>
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <div className="logo">
            <Hotel size={32} className="logo-icon" />
            <span className="logo-text">Hotel AI</span>
          </div>
        </div>

        <div className="header-center">
          <h1 className="page-title">호텔 예측 관리 시스템</h1>
        </div>

        <div className="header-right">
          <motion.div 
            className="weather-widget"
            whileHover={{ scale: 1.05 }}
          >
            <Sun size={20} />
            <span>맑음 24°C</span>
          </motion.div>
          <motion.button 
            className="theme-toggle"
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.3 }}
          >
            <Moon size={20} />
          </motion.button>
        </div>
      </motion.header>

      {/* Sidebar */}
      <motion.aside 
        className={`layout-sidebar ${sidebarOpen ? 'open' : ''}`}
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        <nav className="sidebar-nav">
          {menuItems.map((item, index) => (
            <motion.div
              key={item.path}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link 
                to={item.path}
                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                {location.pathname === item.path && (
                  <motion.div 
                    className="active-indicator"
                    layoutId="activeIndicator"
                  />
                )}
              </Link>
            </motion.div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">👤</div>
            <div className="user-details">
              <span className="user-name">관리자</span>
              <span className="user-role">호텔 매니저</span>
            </div>
          </div>
          <button className="settings-btn">
            <Settings size={20} />
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className={`layout-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <motion.div 
          className="content-wrapper"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Footer */}
      <motion.footer 
        className="layout-footer"
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        <div className="footer-content">
          <div className="footer-section">
            <h3>Hotel AI System</h3>
            <p>머신러닝 기반 호텔 운영 최적화 솔루션</p>
          </div>
          <div className="footer-section">
            <h4>빠른 링크</h4>
            <ul>
              <li><Link to="/breakfast">조식 예측</Link></li>
              <li><Link to="/cancellation">취소율 분석</Link></li>
              <li><Link to="/statistics">통계 대시보드</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>시스템 상태</h4>
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>정상 운영중</span>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2024 Hotel AI System. All rights reserved.</p>
        </div>
      </motion.footer>
    </div>
  );
}

export default Layout;
