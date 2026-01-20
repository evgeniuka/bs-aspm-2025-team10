import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => { 
    const initializeAuth = async () => {
      console.log('🔍 AuthContext: Initializing auth...');
      
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getCurrentUser();
          console.log('✅ AuthContext: User loaded from token:', userData);
          setUser(userData);
          

          localStorage.setItem('user', JSON.stringify(userData));
        } catch (error) {
          console.error('❌ Token validation failed:', error);
          localStorage.removeItem('token');
          sessionStorage.removeItem('token');
          localStorage.removeItem('user'); 
        }
      } else {
        console.log('ℹ️ AuthContext: No valid token found');
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password, rememberMe = false) => {
    console.log('🔐 AuthContext: Login called for:', email);
    
    const { user: userData, token } = await authService.login(email, password, rememberMe);
    
    console.log('✅ AuthContext: Login successful:', userData);
    setUser(userData);


    if (rememberMe) {
      localStorage.setItem('token', token);
    } else {
      sessionStorage.setItem('token', token);
    }

   
    localStorage.setItem('user', JSON.stringify(userData));


    if (userData.role === 'trainer') {
      navigate('/trainer/dashboard');
    } else if (userData.role === 'trainee') {
      navigate('/trainee/dashboard');
    }
  };

  const logout = async () => {
    console.log('🚪 AuthContext: Logout called');
    
    await authService.logout();
    setUser(null);
    
  
    localStorage.removeItem('user');
    
    navigate('/login');
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        Loading...
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
