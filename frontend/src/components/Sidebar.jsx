import React from 'react';
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
      </div>
    </>
  );
}

export default Sidebar;
