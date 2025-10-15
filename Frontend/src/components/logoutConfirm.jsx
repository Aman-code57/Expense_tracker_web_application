import React from 'react';
import { TailSpin } from "react-loader-spinner";
import "./logoutconfirm.css";

const LogoutConfirmationModal = ({ isOpen, onClose, onConfirm, logoutLoading }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlayss">
      <div className="modals-contents">
        <h3>Confirm Logout</h3>
        <p>Are you sure you want to logout? This will end your session.</p>
        <div className="modals-actionss">
          <button className="btns-cancels" onClick={onClose} disabled={logoutLoading}>Cancel</button>
          <button className="btns-confirms" onClick={onConfirm} disabled={logoutLoading} style={{ position: 'relative' }}>
            {logoutLoading ? (
              <>
                <TailSpin height="20" width="20" color="#fff" ariaLabel="loading" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
                <span>Logging out...</span>
              </>
            ) : (
              "Logout"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogoutConfirmationModal;
