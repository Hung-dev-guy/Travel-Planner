import React from 'react';
import RegisterForm from '../components/auth/RegisterForm';
import AuthLayout from '../components/auth/AuthLayout';

const RegisterPage = () => {
  return (
    <AuthLayout>
      <h2>Register</h2>
      <RegisterForm />
    </AuthLayout>
  );
};

export default RegisterPage;
