import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api/index";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const setSession = (accessToken) => {
    if (accessToken) {
      localStorage.setItem("token", accessToken);
      api.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
      setToken(accessToken);

      try {

        const base64Url = accessToken.split(".")[1];
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split("")
            .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
            .join("")
        );
        const payload = JSON.parse(jsonPayload);

        setUser({
          id: payload.sub,
          email: payload.email,
          is_verified: payload.is_verified,
        });
      } catch (err) {
        console.error("Failed to decode JWT payload", err);
        clearSession();
      }
    } else {
      clearSession();
    }
  };

  const clearSession = () => {
    localStorage.removeItem("token");
    delete api.defaults.headers.common["Authorization"];
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      setSession(storedToken);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await api.post("/api/auth/login", { email, password });
    if (response.data?.access_token) {
      setSession(response.data.access_token);
    }
    return response;
  };

  const register = async (email, password) => {
    return await api.post("/api/auth/register", { email, password });
  };

  const logout = async () => {
    try {
      await api.post("/api/auth/logout");
    } catch (err) {
      console.error("Logout request failed", err);
    } finally {
      clearSession();
    }
  };

  const forgotPassword = async (email) => {
    return await api.post("/api/auth/forgot-password", { email });
  };

  const verifyOTP = async (email, otp, new_password) => {
    return await api.post("/api/auth/verify-otp", {
      email,
      otp,
      new_password,
    });
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    forgotPassword,
    verifyOTP,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
