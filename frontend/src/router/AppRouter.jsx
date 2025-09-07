import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import CancellationPrediction from '../pages/CancellationPrediction';
import BreakfastPrediction from '../pages/BreakfastPrediction';

function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/cancellation" element={<CancellationPrediction />} />
        <Route path="/breakfast" element={<BreakfastPrediction />} />
      </Routes>
    </Router>
  );
}

export default AppRouter;
