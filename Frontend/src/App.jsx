import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import SignIn from './pages/Auth/SignIn/SignIn';
import SignUp from './pages/Auth/SignUp/SignUp'
import ForgotPassword from './pages/Auth/ForgotPassword/ForgotPassword'
import OTPForgotPassword from './pages/Auth/ForgotPassword/OTPForgotPassword';
import ResetPassword from './pages/Auth/ForgotPassword/ResetPassword';
import Dashboard from './pages/Dashboard/Dashboard';
import Income from './pages/Income/Income';
import Expense from './pages/Expense/Expense';
import PrivateRoute from "./components/PrivateRoute";
import PublicRoute from "./components/PublicRoute";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  return (
    <Router>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        pauseOnHover
        draggable
        theme="colored"
      />

      <Routes>
        <Route path="/" element={<Navigate to="/signin" replace />} />
        <Route path="/signin" element={<PublicRoute><SignIn /></PublicRoute>} />
        <Route path="/signup" element={<PublicRoute><SignUp /></PublicRoute>} />
        <Route path="/forgotpassword" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
        <Route path="/otp-forgot-password" element={<PublicRoute><OTPForgotPassword /></PublicRoute>} />
        <Route path="/reset-password" element={<PublicRoute><ResetPassword /></PublicRoute>} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/income"
          element={
            <PrivateRoute>
              <Income />
            </PrivateRoute>
          }
        />
        <Route
          path="/expense"
          element={
            <PrivateRoute>
              <Expense />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<PublicRoute><Navigate to="/signin" replace /></PublicRoute>} />
      </Routes>
    </Router>
  );
}

export default App;
