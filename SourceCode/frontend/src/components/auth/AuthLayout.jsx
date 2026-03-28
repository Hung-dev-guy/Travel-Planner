import React from 'react';

const AuthLayout = ({ children }) => {
  return (
    <div className="auth-layout" style={{ 
      minHeight: '80vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="card-premium" style={{ width: '100%', maxWidth: '400px' }}>
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
