import React from 'react';
import { ThemeProvider } from './context/ThemeContext';
import AppRoutes from './routes/AppRoutes';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import './assets/styles/global.css';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <div className="app-container">
        <Navbar />
        <div className="main-layout">
          <Sidebar />
          <main className="content">
            <AppRoutes />
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
