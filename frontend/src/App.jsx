import React from 'react';
import { Toaster } from 'react-hot-toast';
import AppRouter from './router/AppRouter';
import './App.css';

function App() {
  return (
    <div className="app">
      <AppRouter />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'linear-gradient(135deg, #8b4513 0%, #daa520 100%)',
            color: '#fff',
            borderRadius: '0',
            border: '3px solid #654321',
            boxShadow: '0 10px 30px rgba(139, 69, 19, 0.3)',
          },
        }}
      />
    </div>
  );
}

export default App;