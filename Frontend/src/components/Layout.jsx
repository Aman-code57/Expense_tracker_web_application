import React, { useState } from "react";
import { useNavigate, NavLink } from "react-router-dom";
import "./Layout.css";
import { removeCookie } from "../utils/cookies";
import LogoutConfirmationModal from "./logoutConfirm";

const Layout = ({ title, sidebarLinks, children }) => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [logoutLoading, setLogoutLoading] = useState(false);

  const handleLogoutClick = () => {
    setIsModalOpen(true);
  };

  const handleConfirmLogout = async () => {
    setLogoutLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000)); 
    removeCookie("access_token");
    navigate("/signin");
    setLogoutLoading(false);
    setIsModalOpen(false);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="homepage">
      <nav className="navbar">
        <h1 className="navbar-title">{title}</h1>
        <button onClick={handleLogoutClick} className="logout-btn">
          Logout
        </button>
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
        {children}
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
