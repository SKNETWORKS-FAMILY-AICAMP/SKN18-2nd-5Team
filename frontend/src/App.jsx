import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import GuestManagement from './pages/GuestManagement';
import BreakfastPrediction from './pages/BreakfastPrediction';
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

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
              background: '#333',
              color: '#fff',
              borderRadius: '10px',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;