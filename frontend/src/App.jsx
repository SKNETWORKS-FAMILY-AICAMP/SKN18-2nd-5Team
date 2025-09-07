import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
<<<<<<< HEAD
// import Layout from './components/Layout';
=======
import Navbar from './components/Navbar';
>>>>>>> origin/inha-2
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import GuestManagement from './pages/GuestManagement';
import BreakfastPrediction from './pages/BreakfastPrediction';
import './App.css';

function App() {
<<<<<<< HEAD
  const [sidebarOpen, setSidebarOpen] = useState(true);
=======
  const [sidebarOpen, setSidebarOpen] = useState(false);
>>>>>>> origin/inha-2

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

<<<<<<< HEAD
  return (
    <Router>
      <div className="app">
        <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
=======
  const handleFilter = (filterType) => {
    console.log('Global filter applied:', filterType);
  };

  return (
    <Router>
      <div className="app">
        <Navbar />
        <Sidebar 
          isOpen={sidebarOpen}
          onToggle={toggleSidebar}
          onFilter={handleFilter}
        />
>>>>>>> origin/inha-2
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/cancellation" element={<GuestManagement sidebarOpen={sidebarOpen} />} />
            <Route path="/breakfast" element={<BreakfastPrediction />} />
          </Routes>
        </main>
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