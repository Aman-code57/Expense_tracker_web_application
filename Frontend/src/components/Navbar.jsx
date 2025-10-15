import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getCookie } from '../utils/cookies';

const Navbar = () => {
  const navigate = useNavigate();

  const handleHeadingClick = () => {
    const token = getCookie('access_token');
    if (token) {
      navigate('/dashboard');
    } else {
      navigate('/signin');
    }
  };

  return (
    <nav style={{ position: 'fixed', top: 0, left: 0, width: '100%', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', padding: '10px', backgroundColor: '#007bff', color: '#ffffff', zIndex: 1000 }}>
      <h2 style={{ margin: 0, color: '#ffffff', cursor: 'pointer' }} onClick={handleHeadingClick}>Expense Tracker</h2>
    </nav>
  );
};

export default Navbar;
