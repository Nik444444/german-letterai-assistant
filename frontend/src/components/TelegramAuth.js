import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    FileText, 
    Mail, 
    Globe, 
    Sparkles, 
    CheckCircle, 
    Clock, 
    Users,
    Brain,
    Zap,
    Shield,
    Star,
    ArrowRight,
    Play,
    Palette,
    Crown,
    Wand2,
    Rocket,
    Heart,
    MessageSquare,
    Languages,
    History,
    Key,
    User,
    Loader2
} from 'lucide-react';

const TelegramAuth = () => {
    const { loginWithTelegram } = useContext(AuthContext);
    const [isLoading, setIsLoading] = useState(false);
    const [telegramUser, setTelegramUser] = useState(null);
    const [error, setError] = useState(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        
        // Проверяем, доступно ли Telegram Web App API
        if (window.Telegram && window.Telegram.WebApp) {
            const webApp = window.Telegram.WebApp;
            
            // Расширяем приложение на весь экран
            webApp.expand();
            
            // Настраиваем тему
            webApp.setHeaderColor('bg_color');
            webApp.setBackgroundColor('#1a1a2e');
            
            // Получаем данные пользователя
            const user = webApp.initDataUnsafe?.user;
            if (user) {
                setTelegramUser(user);
                // Автоматически авторизуем пользователя
                handleTelegramAuth(user);
            }
        } else {
            setError('Telegram Web App API недоступен');
        }
    }, []);

    const handleTelegramAuth = async (user) => {
        setIsLoading(true);
        setError(null);
        
        try {
            const result = await loginWithTelegram(user);
            if (!result.success) {
                setError(result.error || 'Ошибка авторизации');
            }
        } catch (err) {
            setError('Произошла ошибка при авторизации');
        } finally {
            setIsLoading(false);
        }
    };

    const retryAuth = () => {
        if (telegramUser) {
            handleTelegramAuth(telegramUser);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
                    <div className="text-center mb-8">
                        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                            <MessageSquare className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-2">
                            German Letter AI
                        </h2>
                        <p className="text-gray-600">
                            Telegram Mini App
                        </p>
                    </div>

                    {error ? (
                        <div className="space-y-6">
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <div className="flex items-center">
                                    <div className="text-red-500 mr-3">
                                        <Shield className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-red-700">{error}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <button
                                onClick={retryAuth}
                                disabled={isLoading}
                                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center justify-center space-x-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Повторная попытка...</span>
                                    </>
                                ) : (
                                    <>
                                        <ArrowRight className="w-5 h-5" />
                                        <span>Попробовать снова</span>
                                    </>
                                )}
                            </button>
                        </div>
                    ) : isLoading ? (
                        <div className="space-y-6">
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                <div className="flex items-center">
                                    <div className="text-blue-500 mr-3">
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-blue-700">
                                            Выполняется авторизация...
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            {telegramUser && (
                                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center">
                                        <div className="text-gray-500 mr-3">
                                            <User className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">
                                                {telegramUser.first_name} {telegramUser.last_name}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                @{telegramUser.username}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                <div className="flex items-center">
                                    <div className="text-green-500 mr-3">
                                        <CheckCircle className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-green-700">
                                            Добро пожаловать в Telegram Mini App!
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {telegramUser && (
                                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center">
                                        <div className="text-gray-500 mr-3">
                                            <User className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">
                                                {telegramUser.first_name} {telegramUser.last_name}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                @{telegramUser.username}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Дополнительная информация о приложении */}
                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <div className="space-y-3">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
                                    <FileText className="w-4 h-4 text-white" />
                                </div>
                                <div>
                                    <span className="text-sm font-medium text-gray-900">Анализ документов</span>
                                    <p className="text-xs text-gray-500">PDF и изображения</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                                    <Brain className="w-4 h-4 text-white" />
                                </div>
                                <div>
                                    <span className="text-sm font-medium text-gray-900">AI анализ</span>
                                    <p className="text-xs text-gray-500">Современные модели</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-green-500 to-teal-500 flex items-center justify-center">
                                    <Languages className="w-4 h-4 text-white" />
                                </div>
                                <div>
                                    <span className="text-sm font-medium text-gray-900">Мультиязычность</span>
                                    <p className="text-xs text-gray-500">Русский, English, Deutsch</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TelegramAuth;