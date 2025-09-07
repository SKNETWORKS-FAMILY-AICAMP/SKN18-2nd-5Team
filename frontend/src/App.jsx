import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import CancellationPrediction from './pages/CancellationPrediction';
import BreakfastPrediction from './pages/BreakfastPrediction';
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Router>
      <div className="app">
        <Layout sidebarOpen={sidebarOpen} toggleSidebar={toggleSidebar}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/cancellation" element={<CancellationPrediction />} />
            <Route path="/breakfast" element={<BreakfastPrediction />} />
          </Routes>
        </Layout>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              borderRadius: '15px',
              boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;