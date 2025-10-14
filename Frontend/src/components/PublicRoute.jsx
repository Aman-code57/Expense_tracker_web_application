import React from "react";
import { Navigate } from "react-router-dom";
import { getCookie } from "../utils/cookies";

const PublicRoute = ({ children }) => {
  const token = getCookie("access_token");
  return token ? <Navigate to="/dashboard" replace /> : children;
};

export default PublicRoute;
