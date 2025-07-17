import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState(localStorage.getItem('authToken'));

    // Configure axios defaults
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [token]);

    // Check if user is authenticated
    const isAuthenticated = () => {
        return !!token && !!user;
    };

    // Login with Google
    const loginWithGoogle = async (credential) => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/auth/google/verify`, {
                credential: credential
            });

            const { access_token, user: userData } = response.data;

            // Store token and user data
            localStorage.setItem('authToken', access_token);
            setToken(access_token);
            setUser({...userData, token: access_token});

            return { success: true };
        } catch (error) {
            console.error('Google login failed:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось войти'
            };
        }
    };

    // Logout
    const logout = () => {
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    // Get user profile
    const fetchUserProfile = async () => {
        try {
            if (!token) return;

            const response = await axios.get(`${BACKEND_URL}/api/profile`);
            setUser({...response.data, token: token});
        } catch (error) {
            console.error('Failed to fetch user profile:', error);
            if (error.response?.status === 401) {
                logout();
            }
        }
    };

    // Update user profile
    const updateProfile = async (data) => {
        try {
            const response = await axios.put(`${BACKEND_URL}/api/profile`, data);
            setUser(response.data);
            return { success: true };
        } catch (error) {
            console.error('Failed to update profile:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось обновить профиль'
            };
        }
    };

    // Save API keys
    const saveApiKeys = async (apiKeys) => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/api-keys`, apiKeys);

            // Update user object
            setUser(prev => ({ 
                ...prev, 
                has_api_key_1: !!(apiKeys.api_key_1 || prev.has_api_key_1),
                has_api_key_2: !!(apiKeys.api_key_2 || prev.has_api_key_2),
                has_api_key_3: !!(apiKeys.api_key_3 || prev.has_api_key_3)
            }));

            return { success: true, message: response.data.message };
        } catch (error) {
            console.error('Failed to save API keys:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось сохранить API ключи'
            };
        }
    };

    // Initialize authentication state
    useEffect(() => {
        const initAuth = async () => {
            if (token) {
                await fetchUserProfile();
            }
            setLoading(false);
        };

        initAuth();
    }, [token]);

    const value = {
        user,
        token,
        loading,
        isAuthenticated,
        loginWithGoogle,
        logout,
        fetchUserProfile,
        updateProfile,
        saveApiKeys
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};