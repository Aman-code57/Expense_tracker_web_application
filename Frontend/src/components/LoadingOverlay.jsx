import React from 'react';
import { TailSpin } from 'react-loader-spinner';
import './LoadingOverlay.css';

const LoadingOverlay = ({ isVisible }) => {
  if (!isVisible) return null;

  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <TailSpin height="50" width="50" color="#007bff" ariaLabel="loading" />
        <p>Loading...</p>
      </div>
    </div>
  );
};

export default LoadingOverlay;

