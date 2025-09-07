import React from 'react';
import { motion } from 'framer-motion';
import './Header.css';

function Header({ title, subtitle }) {
  return (
    <motion.div 
      className="hotel-header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="hotel-icons">
        <span>👑</span>
        <span>⭐</span>
        <span>💎</span>
      </div>
      <h1>{title || 'GRAND HOTEL MONOPOLY'}</h1>
      <div className="decorative-line"></div>
      <div className="hotel-name">{subtitle || '호텔 관리 시스템'}</div>
    </motion.div>
  );
}

export default Header;
