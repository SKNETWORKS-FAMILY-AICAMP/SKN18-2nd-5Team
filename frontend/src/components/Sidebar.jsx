import React from 'react';
<<<<<<< HEAD
import { Link, useLocation } from 'react-router-dom';
import { Home, TrendingDown, Coffee, X, Menu } from 'lucide-react';
import './Sidebar.css';

function Sidebar({ isOpen, toggleSidebar }) {
  const location = useLocation();

  const menuItems = [
    {
      path: '/',
      icon: <Home size={20} />,
      label: '홈',
      name: 'home'
    },
    {
      path: '/cancellation',
      icon: <TrendingDown size={20} />,
      label: '예약 관리 시스템',
      name: 'cancellation'
    },
    {
      path: '/breakfast',
      icon: <Coffee size={20} />,
      label: '조식 관리 시스템템',
      name: 'breakfast'
    }
  ];

  return (
    <>
      {/* 사이드바 토글 버튼 */}
      <button 
        className="sidebar-toggle"
        onClick={toggleSidebar}
        aria-label="메뉴 토글"
      >
        <Menu size={24} />
      </button>

      {/* 오버레이 */}
      {isOpen && (
        <div 
          className="sidebar-overlay" 
          onClick={toggleSidebar}
        />
      )}

      {/* 사이드바 */}
      <div className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <button 
            className="sidebar-close"
            onClick={toggleSidebar}
            aria-label="사이드바 닫기"
          >
            <X size={24} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <ul className="sidebar-menu">
            {menuItems.map((item) => (
              <li key={item.name} className="sidebar-item">
                <Link
                  to={item.path}
                  className={`sidebar-link ${
                    location.pathname === item.path ? 'active' : ''
                  }`}
                  onClick={toggleSidebar}
                >
                  <span className="sidebar-icon">{item.icon}</span>
                  <span className="sidebar-label">{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
=======
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import './Sidebar.css';

function Sidebar({ isOpen, onToggle, onFilter }) {
  return (
    <>
      {/* 항상 보이는 토글 버튼 - 사이드바가 닫혀있을 때만 표시 */}
      {!isOpen && (
        <button onClick={onToggle} className="sidebar-toggle-fixed">
          <div className="toggle-icon">
            <div className="toggle-bar"></div>
            <div className="toggle-bar"></div>
            <div className="toggle-bar-front"></div>
          </div>
        </button>
      )}

      {/* 사이드바 */}
      <div className="sidebar" 
       style={{ left: isOpen ? '0px' : '-300px' }}>
        {/* 사이드바 오른쪽 토글 버튼 - 사이드바가 열릴 때만 표시 */}
        {isOpen && (
          <button onClick={onToggle} className="sidebar-toggle-relative">
            <div className="toggle-icon">
              <div className="toggle-bar"></div>
              <div className="toggle-bar"></div>
              <div className="toggle-bar-front"></div>
            </div>
          </button>
        )}

        {isOpen && (
          <div className="sidebar-content">
            <div className="navigation-section">
              <Link to="/" className="nav-item" onClick={onToggle}>
                메인 화면
              </Link>
              <Link to="/breakfast" className="nav-item" onClick={onToggle}>
                조식 관리
              </Link>
              <Link to="/cancellation" className="nav-item" onClick={onToggle}>
                고객관리
              </Link>
            </div>
          </div>
        )}
>>>>>>> origin/inha-2
      </div>
    </>
  );
}

export default Sidebar;
