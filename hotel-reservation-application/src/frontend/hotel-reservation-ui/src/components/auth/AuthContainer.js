import React, { useState } from 'react';
import SignInPage from './SignInPage';
import SignUpPage from './SignUpPage';

const AuthContainer = ({ onAuthSuccess }) => {
  const [currentPage, setCurrentPage] = useState('signin'); // 'signin' or 'signup'

  const handleSignIn = (authData) => {
    onAuthSuccess(authData);
  };

  const handleSignUp = (userData) => {
    // Could show success message here
    console.log('User registered:', userData);
  };

  const switchToSignUp = () => {
    setCurrentPage('signup');
  };

  const switchToSignIn = () => {
    setCurrentPage('signin');
  };

  return (
    <>
      {currentPage === 'signin' ? (
        <SignInPage 
          onSignIn={handleSignIn}
          onSwitchToSignUp={switchToSignUp}
        />
      ) : (
        <SignUpPage 
          onSignUp={handleSignUp}
          onSwitchToSignIn={switchToSignIn}
        />
      )}
    </>
  );
};

export default AuthContainer;