import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import ChatAssistant from "./components/ChatAssistant";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Login from "./pages/Login";
import UserDashboard from "./pages/UserDashboard";
import TechnicianDashboard from "./pages/TechnicianDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import Unauthorized from "./pages/Unauthorized";

// Pages where Navbar is hidden (full-screen dashboards / auth)
const HIDE_NAVBAR = ["/login", "/user/dashboard", "/technician/dashboard", "/admin/dashboard", "/unauthorized"];

function AppContent() {
  const location = useLocation();
  const hideNav = HIDE_NAVBAR.some(p => location.pathname.startsWith(p));

  return (
    <>
      {!hideNav && <Navbar />}
      <Routes>
        {/* Public routes */}
        <Route path="/"             element={<Home />} />
        <Route path="/search"       element={<Search />} />
        <Route path="/login"        element={<Login />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Protected: User */}
        <Route path="/user/dashboard" element={
          <ProtectedRoute roles={["user"]}>
            <UserDashboard />
          </ProtectedRoute>
        } />

        {/* Protected: Technician */}
        <Route path="/technician/dashboard" element={
          <ProtectedRoute roles={["technician"]}>
            <TechnicianDashboard />
          </ProtectedRoute>
        } />

        {/* Protected: Admin (hidden route) */}
        <Route path="/admin/dashboard" element={
          <ProtectedRoute roles={["admin"]}>
            <AdminDashboard />
          </ProtectedRoute>
        } />
      </Routes>
      {!hideNav && <ChatAssistant />}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AuthProvider>
  );
}
