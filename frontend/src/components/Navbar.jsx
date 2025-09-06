import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, TrendingDown, Coffee, Menu, X } from 'lucide-react';
import { motion } from 'framer-motion';
import './Navbar.css';

function Navbar() {
  const [isOpen, setIsOpen] = React.useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: '홈', icon: Home },
    { path: '/cancellation', label: '고객 관리', icon: TrendingDown },
    { path: '/breakfast', label: '조식 예측', icon: Coffee },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <motion.div
            initial={{ rotate: 0 }}
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
            className="logo-icon"
          >
            🏨
          </motion.div>
          <span>HotelPredict AI</span>
        </Link>

        <div className="navbar-toggle" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </div>

        <ul className={`navbar-menu ${isOpen ? 'active' : ''}`}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path} className="navbar-item">
                <Link
                  to={item.path}
                  className={`navbar-link ${isActive ? 'active' : ''}`}
                  onClick={() => setIsOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
