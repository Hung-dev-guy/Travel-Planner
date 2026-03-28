import React from 'react';
import LoginForm from '../components/auth/LoginForm';
import AuthLayout from '../components/auth/AuthLayout';

const LoginPage = () => {
  return (
    <AuthLayout>
      <h2 style={{ color: 'var(--primary)' }}>Login</h2>
      <LoginForm />
    </AuthLayout>
  );
};

export default LoginPage;
