import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const response = await api.get('/api/auth/me');
        setUser(response.data);
      } catch (error) {
        console.error('Session check failed:', error);
        // Only invalidate session if backend explicitly returns 401 Unauthorized or 403 Forbidden
        // Do NOT log out on connection errors, backend restarts, or network flickers
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          console.warn('Token expired or invalid. Logging out.');
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
        } else {
          console.info('Backend temporarily unreachable. Preserving user session.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCurrentUser();
  }, [token]);

  const login = async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  };

  const updateProfile = async (profileData) => {
    const response = await api.put('/api/auth/profile', profileData);
    setUser(response.data);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    api.post('/api/auth/logout').catch(() => {});
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        updateProfile,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
