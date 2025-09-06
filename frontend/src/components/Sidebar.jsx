import React from 'react';
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
      label: '취소 예측',
      name: 'cancellation'
    },
    {
      path: '/breakfast',
      icon: <Coffee size={20} />,
      label: '조식 예측',
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
          <h2>메뉴</h2>
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
      </div>
    </>
  );
}

export default Sidebar;
