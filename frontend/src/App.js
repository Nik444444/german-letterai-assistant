import React, { useContext } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Auth from './components/Auth';
import SuperMainApp from './components/SuperMainApp';
import AdminPanel from './components/AdminPanel';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com';

function App() {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </GoogleOAuthProvider>
    );
}

const AppContent = () => {
    const { isAuthenticated, loading } = useContext(AuthContext);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center relative overflow-hidden">
                {/* Background Pattern */}
                <div className="absolute inset-0 bg-dots-pattern opacity-30"></div>
                
                <div className="text-center relative z-10">
                    <div className="relative mb-8">
                        <div className="w-16 h-16 border-4 border-indigo-200 rounded-full animate-spin border-t-indigo-600 mx-auto"></div>
                        <div className="absolute inset-0 w-16 h-16 border-4 border-purple-200 rounded-full animate-ping mx-auto"></div>
                    </div>
                    <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                        Загрузка...
                    </h3>
                    <p className="text-gray-600">Подготавливаем волшебство</p>
                </div>
            </div>
        );
    }

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={isAuthenticated() ? <SuperMainApp /> : <Auth />} />
                <Route path="/admin" element={<AdminPanel />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
