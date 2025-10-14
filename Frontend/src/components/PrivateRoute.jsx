import React from "react";
import { Navigate } from "react-router-dom";
import { getCookie } from "../utils/cookies";

const PrivateRoute = ({ children }) => {
  const token = getCookie("access_token");
  return token ? children : <Navigate to="/signin" replace />;
};

export default PrivateRoute;
