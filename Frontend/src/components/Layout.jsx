import React, { useState, useEffect } from "react";
import { useNavigate, NavLink } from "react-router-dom";
import "./Layout.css";
import { removeCookie } from "../utils/cookies";
import LogoutConfirmationModal from "./logoutConfirm";
import { PiUserBold } from "react-icons/pi";

const Layout = ({ title, sidebarLinks, children }) => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [logoutLoading, setLogoutLoading] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const email = localStorage.getItem("user_email");
    if (email) {
      setUserEmail(email);
    }
  }, []);

  const handleLogoutClick = () => {
    setIsModalOpen(true);
  };

  const handleConfirmLogout = async () => {
    setLogoutLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    removeCookie("access_token");
    localStorage.removeItem("user_email");
    navigate("/signin");
    setLogoutLoading(false);
    setIsModalOpen(false);
  };

  const toggleProfileDropdown = () => {
    setIsProfileOpen(!isProfileOpen);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="homepage">
      <nav className="navbar">
        <h1 className="navbar-title">{title}</h1>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {userEmail && (
            <div className="profile-container">
              <button onClick={toggleProfileDropdown} className="profile-btn">
              <PiUserBold  />
              </button>
              {isProfileOpen && (
                <div className="profile-dropdown">
                  <p>{userEmail}</p>
                </div>
              )}
            </div>
          )}
          <button onClick={handleLogoutClick} className="logout-btn">
            Logout
          </button>
        </div>
      </nav>

      <div className="sidebar">
        <ul className="sidebar-links">
          {sidebarLinks.map((link, idx) => (
            <li key={idx}>
              <NavLink to={link.href} className={({ isActive }) => isActive ? 'active' : ''}>
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>

      <div className="main-content">
        <div className="content-wrapper">
          {children}
        </div>
        <footer className="footer">
          <p>&copy; 2023 Expense Tracker. All rights reserved.</p>
          <div className="footer-links">
          <NavLink to="/about" className="footer-link">About</NavLink>
          <NavLink to="/contact" className="footer-link">Contact</NavLink>
          <NavLink to="/privacy" className="footer-link">Privacy Policy</NavLink>
        </div>
        </footer>
      </div>

      <LogoutConfirmationModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onConfirm={handleConfirmLogout}
        logoutLoading={logoutLoading}
      />
    </div>
  );
};

export default Layout;
