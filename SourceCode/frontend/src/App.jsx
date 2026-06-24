import React from 'react';
import { useLocation } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import AppRoutes from './routes/AppRoutes';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import Footer from './components/common/Footer';
import './assets/styles/global.css';
import './App.css';

function App() {
  const location = useLocation();
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';
  const showFooter = location.pathname === '/dashboard';

  return (
    <ThemeProvider>
      <div className="app-container">
        {!isAuthPage && <Navbar />}
        <div className={isAuthPage ? "" : "main-layout"}>
          <main className={isAuthPage ? "" : "content"} style={isAuthPage ? { width: '100vw', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'var(--bg-default)' } : { flex: 1 }}>
            <div style={{ minHeight: 'calc(100vh - 80px)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ flex: 1, padding: '30px' }}>
                <AppRoutes />
              </div>
              {showFooter && <Footer />}
            </div>
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
