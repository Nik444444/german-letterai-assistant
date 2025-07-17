import React, { useContext, useState, useCallback, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import UserProfile from './UserProfile';
import ImprovedAnalysisResult from './ImprovedAnalysisResult';
import SpectacularAnalysisResult from './SpectacularAnalysisResult';
import SpectacularDocumentAnalysis from './SpectacularDocumentAnalysis';
import TelegramNews from './TelegramNews';
import MobileOptimizations from './MobileOptimizations';
import TelegramWebApp from './TelegramWebApp';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { 
    Upload, 
    User, 
    LogOut, 
    FileText, 
    Image, 
    Clock, 
    AlertCircle,
    CheckCircle,
    Eye,
    History,
    Settings,
    Download,
    Trash2,
    X,
    Sparkles,
    Zap,
    Star,
    Heart,
    Crown,
    Wand2,
    Rainbow,
    Flame,
    Rocket,
    Key,
    Palette,
    Shield,
    Menu,
    ChevronDown,
    ChevronUp,
    Camera,
    Smartphone
} from 'lucide-react';
import { 
    GlassCard, 
    GradientText
} from './UIEffects';
import { 
    isTelegramWebApp, 
    getTelegramWebApp, 
    hapticFeedback, 
    showTelegramAlert 
} from '../utils/telegramWebApp';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const SuperMainApp = () => {
    const { user, logout } = useContext(AuthContext);
    const [showProfile, setShowProfile] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [showAnalysisResult, setShowAnalysisResult] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [geminiKeyLoading, setGeminiKeyLoading] = useState(false);
    const [geminiKeyMessage, setGeminiKeyMessage] = useState('');
    const [showGeminiSetup, setShowGeminiSetup] = useState(false);
    const [geminiApiKey, setGeminiApiKey] = useState('');
    const [geminiKeySuccessful, setGeminiKeySuccessful] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [showMobileNews, setShowMobileNews] = useState(false);
    const [isLandscape, setIsLandscape] = useState(window.innerWidth > window.innerHeight);

    // Обработка изменения ориентации
    React.useEffect(() => {
        const handleResize = () => {
            setIsLandscape(window.innerWidth > window.innerHeight);
        };

        const handleOrientationChange = () => {
            // Небольшая задержка для корректного определения размеров
            setTimeout(() => {
                setIsLandscape(window.innerWidth > window.innerHeight);
            }, 100);
        };

        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', handleOrientationChange);
        
        // Telegram Web App specific event handlers
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            
            // Handle viewport changes
            tg.onEvent('viewportChanged', () => {
                const newHeight = tg.viewportHeight;
                const newIsExpanded = tg.isExpanded;
                
                // Update state based on Telegram Web App viewport
                setIsLandscape(newHeight < 500);
                
                // Adjust UI for expanded/collapsed state
                if (newIsExpanded) {
                    document.body.classList.add('telegram-expanded');
                } else {
                    document.body.classList.remove('telegram-expanded');
                }
            });
            
            // Handle theme changes
            tg.onEvent('themeChanged', () => {
                const newTheme = tg.colorScheme || 'light';
                document.body.className = newTheme === 'dark' ? 'dark' : 'light';
            });
        }
        
        return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('orientationchange', handleOrientationChange);
        };
    }, []);

    // Drag and drop configuration
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            analyzeFile(acceptedFiles[0]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
            'application/pdf': ['.pdf']
        },
        maxFiles: 1,
        onDragEnter: () => setDragActive(true),
        onDragLeave: () => setDragActive(false)
    });

    const analyzeFile = async (file) => {
        setLoading(true);
        setError('');
        setAnalysisResult(null);
        setDragActive(false);

        try {
            // Telegram Web App haptic feedback
            if (isTelegramWebApp()) {
                hapticFeedback('light');
            }

            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(`${BACKEND_URL}/api/analyze-file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setAnalysisResult(response.data);
            setShowAnalysisResult(true);
            
            // Success feedback
            if (isTelegramWebApp()) {
                hapticFeedback('success');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка анализа файла');
            
            // Error feedback
            if (isTelegramWebApp()) {
                hapticFeedback('error');
                showTelegramAlert('Ошибка анализа файла');
            }
        } finally {
            setLoading(false);
        }
    };

    const loadHistory = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/analysis-history`);
            setHistory(response.data.analyses);
        } catch (err) {
            console.error('Ошибка загрузки истории:', err);
        }
    };

    const handleShowHistory = () => {
        if (!showHistory) {
            loadHistory();
        }
        setShowHistory(!showHistory);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const openGeminiSetup = () => {
        setShowGeminiSetup(true);
    };

    const handleGeminiKeySubmit = async () => {
        if (!geminiApiKey.trim()) {
            setGeminiKeyMessage('Введите API ключ');
            if (isTelegramWebApp()) {
                hapticFeedback('warning');
            }
            return;
        }
        
        setGeminiKeyLoading(true);
        setGeminiKeyMessage('');
        
        try {
            if (isTelegramWebApp()) {
                hapticFeedback('light');
            }
            
            const response = await axios.post(`${BACKEND_URL}/api/quick-gemini-setup`, {
                api_key: geminiApiKey
            }, {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            
            if (response.data.status === 'success') {
                setGeminiKeySuccessful(true);
                setGeminiKeyMessage('API ключ успешно сохранен!');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                }
                
                setTimeout(() => {
                    setShowGeminiSetup(false);
                    setGeminiApiKey('');
                }, 2000);
            } else {
                setGeminiKeyMessage(response.data.message || 'Ошибка сохранения API ключа');
                if (isTelegramWebApp()) {
                    hapticFeedback('error');
                }
            }
        } catch (error) {
            setGeminiKeyMessage('Ошибка сохранения API ключа');
            if (isTelegramWebApp()) {
                hapticFeedback('error');
            }
        } finally {
            setGeminiKeyLoading(false);
        }
    };

    const generateGeminiKey = async () => {
        setGeminiKeyLoading(true);
        setGeminiKeyMessage('');
        
        try {
            const response = await axios.post(`${BACKEND_URL}/api/auto-generate-gemini-key`, {}, {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            
            setGeminiKeyMessage(response.data.message);
            
            // Обновляем информацию о пользователе в контексте
            if (response.data.status === 'demo' || response.data.status === 'active') {
                // Можно обновить состояние пользователя здесь при необходимости
            }
            
        } catch (err) {
            setGeminiKeyMessage(err.response?.data?.detail || 'Ошибка при создании API ключа');
        } finally {
            setGeminiKeyLoading(false);
        }
    };

    return (
        <TelegramWebApp>
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 relative overflow-hidden">
                
                {/* Mobile Optimizations */}
                <MobileOptimizations />
                
                {/* Background Pattern */}
                <div className="absolute inset-0 bg-grid-pattern opacity-30"></div>
                
                {/* Mobile Header */}
                <header className="relative">
                    <GlassCard className="mx-2 sm:mx-4 mt-2 sm:mt-4 p-4 sm:p-6 bg-white/20 backdrop-blur-xl border border-white/30">
                        <div className="max-w-7xl mx-auto">
                            <div className="flex justify-between items-center">
                                {/* Logo Section - Mobile Optimized */}
                                <div className="flex items-center space-x-3 sm:space-x-6">
                                    <div className="relative">
                                        <div className="h-12 w-12 sm:h-16 sm:w-16 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg">
                                            <Crown className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
                                        </div>
                                    </div>
                                    <div className="hidden sm:block">
                                        <h1 className="text-2xl sm:text-3xl font-bold mb-1">
                                            <GradientText className="text-3xl sm:text-4xl">German Letter AI</GradientText>
                                        </h1>
                                        <p className="text-gray-600 flex items-center space-x-2 text-sm sm:text-base">
                                            <Sparkles className="h-4 w-4 text-purple-500" />
                                            <span>Революционный анализ немецких писем</span>
                                            <Wand2 className="h-4 w-4 text-pink-500" />
                                        </p>
                                    </div>
                                    <div className="sm:hidden">
                                        <h1 className="text-lg font-bold">
                                            <GradientText>German AI</GradientText>
                                        </h1>
                                        <p className="text-xs text-gray-600">Анализ документов</p>
                                    </div>
                                </div>
                                
                                {/* Mobile Menu Button */}
                                <div className="sm:hidden">
                                    <button
                                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                        className="p-2 text-gray-700 hover:text-gray-900 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                                    >
                                        <Menu className="h-6 w-6" />
                                    </button>
                                </div>
                                
                                {/* Desktop Navigation */}
                                <div className="hidden sm:flex items-center space-x-4">
                                    <button
                                        onClick={handleShowHistory}
                                        className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl transition-all duration-300 backdrop-blur-sm border border-white/20"
                                    >
                                        <History className="h-5 w-5 text-gray-700" />
                                        <span className="text-gray-700 font-medium">История</span>
                                    </button>
                                    
                                    <button
                                        onClick={() => setShowProfile(true)}
                                        className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl transition-all duration-300 backdrop-blur-sm border border-white/20"
                                    >
                                        <Settings className="h-5 w-5 text-gray-700" />
                                        <span className="text-gray-700 font-medium">Настройки</span>
                                    </button>

                                    {/* Desktop User Section */}
                                    <div className="flex items-center space-x-4 bg-white/20 backdrop-blur-sm rounded-xl p-3 border border-white/20">
                                        <div className="text-right">
                                            <p className="text-sm font-bold text-gray-900">{user.name}</p>
                                            <p className="text-xs text-gray-600">{user.email}</p>
                                        </div>
                                        {user.picture && (
                                            <div className="relative">
                                                <img 
                                                    src={user.picture} 
                                                    alt={user.name} 
                                                    className="h-10 w-10 rounded-full ring-2 ring-white/50"
                                                />
                                            </div>
                                        )}
                                        <button
                                            onClick={logout}
                                            className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                                        >
                                            <LogOut className="h-5 w-5" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </GlassCard>
                    
                    {/* Mobile Menu */}
                    {mobileMenuOpen && (
                        <div className="sm:hidden fixed inset-0 bg-black/50 z-40" onClick={() => setMobileMenuOpen(false)}>
                            <div className="absolute right-0 top-0 h-full w-80 bg-white/95 backdrop-blur-xl border-l border-white/30 p-4" onClick={(e) => e.stopPropagation()}>
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-lg font-bold text-gray-900">Меню</h2>
                                    <button
                                        onClick={() => setMobileMenuOpen(false)}
                                        className="p-2 text-gray-500 hover:text-gray-700"
                                    >
                                        <X className="h-5 w-5" />
                                    </button>
                                </div>
                                
                                {/* Mobile User Info */}
                                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-xl mb-6">
                                    <div className="flex items-center space-x-3">
                                        {user.picture && (
                                            <img 
                                                src={user.picture} 
                                                alt={user.name} 
                                                className="h-12 w-12 rounded-full ring-2 ring-white"
                                            />
                                        )}
                                        <div>
                                            <p className="font-bold text-gray-900">{user.name}</p>
                                            <p className="text-sm text-gray-600">{user.email}</p>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Mobile Menu Items */}
                                <div className="space-y-3">
                                    <button
                                        onClick={() => {
                                            handleShowHistory();
                                            setMobileMenuOpen(false);
                                        }}
                                        className="w-full flex items-center space-x-3 p-3 bg-white/50 hover:bg-white/70 rounded-xl transition-colors"
                                    >
                                        <History className="h-5 w-5 text-gray-700" />
                                        <span className="text-gray-700 font-medium">История анализов</span>
                                    </button>
                                    
                                    <button
                                        onClick={() => {
                                            setShowProfile(true);
                                            setMobileMenuOpen(false);
                                        }}
                                        className="w-full flex items-center space-x-3 p-3 bg-white/50 hover:bg-white/70 rounded-xl transition-colors"
                                    >
                                        <Settings className="h-5 w-5 text-gray-700" />
                                        <span className="text-gray-700 font-medium">Настройки</span>
                                    </button>
                                    
                                    <button
                                        onClick={() => {
                                            setShowMobileNews(!showMobileNews);
                                        }}
                                        className="w-full flex items-center justify-between p-3 bg-white/50 hover:bg-white/70 rounded-xl transition-colors"
                                    >
                                        <div className="flex items-center space-x-3">
                                            <Globe className="h-5 w-5 text-gray-700" />
                                            <span className="text-gray-700 font-medium">Последние новости</span>
                                        </div>
                                        {showMobileNews ? (
                                            <ChevronUp className="h-5 w-5 text-gray-700" />
                                        ) : (
                                            <ChevronDown className="h-5 w-5 text-gray-700" />
                                        )}
                                    </button>
                                    
                                    {/* Mobile News */}
                                    {showMobileNews && (
                                        <div className="pl-8 pr-3">
                                            <div className="max-h-64 overflow-y-auto">
                                                <TelegramNews compact={true} />
                                            </div>
                                        </div>
                                    )}
                                    
                                    <button
                                        onClick={() => {
                                            logout();
                                            setMobileMenuOpen(false);
                                        }}
                                        className="w-full flex items-center space-x-3 p-3 bg-red-50 hover:bg-red-100 rounded-xl transition-colors text-red-700"
                                    >
                                        <LogOut className="h-5 w-5" />
                                        <span className="font-medium">Выйти</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </header>

                {/* Main Content */}
                <div className="max-w-7xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-8 items-start">
                        
                        {/* Left Panel - Main Content */}
                        <div className="lg:col-span-2 space-y-4 sm:space-y-8">
                            
                            {/* Auto Gemini API Key Generation - Mobile Optimized */}
                            <GlassCard className="p-4 sm:p-6 bg-white/30 backdrop-blur-xl border border-white/30">
                                <div className="flex items-center space-x-3 sm:space-x-4 mb-3 sm:mb-4">
                                    <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl">
                                        <Zap className="h-5 w-5 text-white" />
                                    </div>
                                    <h2 className="text-lg sm:text-xl font-bold">
                                        <GradientText>Автоматический API ключ</GradientText>
                                    </h2>
                                </div>
                                
                                <div className="space-y-3 sm:space-y-4">
                                    {!geminiKeySuccessful && (
                                        <div className="p-3 sm:p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2 sm:space-x-3">
                                                    <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                                        <Sparkles className="h-4 w-4 text-white" />
                                                    </div>
                                                    <div>
                                                        <h3 className="font-semibold text-gray-900 text-sm">Нужен API ключ для работы с AI</h3>
                                                        <p className="text-xs text-gray-600">Получите бесплатный API ключ от Google</p>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={openGeminiSetup}
                                                    className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 sm:px-4 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg text-sm"
                                                >
                                                    <Key className="h-4 w-4" />
                                                    <span className="hidden sm:inline">Получить</span>
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                    
                                    {/* Compact Features */}
                                    <div className="grid grid-cols-3 gap-2 sm:gap-3 text-xs">
                                        <div className="text-center p-2 bg-white/20 rounded-lg">
                                            <Sparkles className="h-4 w-4 text-emerald-600 mx-auto mb-1" />
                                            <span className="text-gray-700 font-medium">Мгновенно</span>
                                        </div>
                                        <div className="text-center p-2 bg-white/20 rounded-lg">
                                            <Shield className="h-4 w-4 text-teal-600 mx-auto mb-1" />
                                            <span className="text-gray-700 font-medium">Безопасно</span>
                                        </div>
                                        <div className="text-center p-2 bg-white/20 rounded-lg">
                                            <Heart className="h-4 w-4 text-pink-600 mx-auto mb-1" />
                                            <span className="text-gray-700 font-medium">Бесплатно</span>
                                        </div>
                                    </div>
                                </div>
                            </GlassCard>

                            {/* Spectacular Document Analysis */}
                            <SpectacularDocumentAnalysis
                                onFileSelect={analyzeFile}
                                loading={loading}
                                error={error}
                                apiKeyConfigured={user?.has_gemini_api_key || user?.has_api_key_1 || user?.gemini_api_key}
                            />

                            {/* Loading State */}
                            {loading && (
                                <GlassCard className="p-6 sm:p-8 text-center bg-white/40 backdrop-blur-xl">
                                    <div className="space-y-4 sm:space-y-6">
                                        <div className="flex justify-center">
                                            <div className="relative">
                                                <div className="w-12 h-12 sm:w-16 sm:h-16 border-4 border-indigo-200 rounded-full animate-spin border-t-indigo-600"></div>
                                                <div className="absolute inset-0 w-12 h-12 sm:w-16 sm:h-16 border-4 border-purple-200 rounded-full animate-ping"></div>
                                            </div>
                                        </div>
                                        <div>
                                            <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2">
                                                <GradientText>Анализирую документ...</GradientText>
                                            </h3>
                                            <p className="text-sm sm:text-base text-gray-600">AI обрабатывает ваш файл</p>
                                        </div>
                                        <div className="flex justify-center space-x-2">
                                            {[1, 2, 3].map((i) => (
                                                <div 
                                                    key={i}
                                                    className="w-2 h-2 sm:w-3 sm:h-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full animate-bounce"
                                                    style={{ animationDelay: `${i * 0.1}s` }}
                                                ></div>
                                            ))}
                                        </div>
                                    </div>
                                </GlassCard>
                            )}

                            {/* Error */}
                            {error && (
                                <GlassCard className="p-4 sm:p-6 bg-red-50/80 border border-red-200">
                                    <div className="flex items-center space-x-3 sm:space-x-4">
                                        <div className="p-2 sm:p-3 bg-red-500 rounded-xl">
                                            <AlertCircle className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-red-900 mb-1 text-sm sm:text-base">Ошибка анализа</h3>
                                            <p className="text-red-700 text-sm">{error}</p>
                                        </div>
                                    </div>
                                </GlassCard>
                            )}

                            {/* Success Message */}
                            {analysisResult && !showAnalysisResult && (
                                <GlassCard className="p-6 sm:p-8 bg-gradient-to-r from-green-50/80 to-emerald-50/80 border border-green-200">
                                    <div className="flex items-center space-x-4 sm:space-x-6">
                                        <div className="p-3 sm:p-4 bg-green-500 rounded-xl sm:rounded-2xl shadow-lg">
                                            <CheckCircle className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="text-lg sm:text-2xl font-bold text-green-900 mb-2">
                                                🎉 Анализ завершен успешно!
                                            </h3>
                                            <p className="text-green-700 text-sm sm:text-lg">
                                                Файл <span className="font-semibold">"{analysisResult.file_name}"</span> обработан успешно
                                            </p>
                                        </div>
                                        <button
                                            onClick={() => setShowAnalysisResult(true)}
                                            className="px-4 sm:px-8 py-2 sm:py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg sm:rounded-xl transition-all duration-300 font-bold text-sm sm:text-lg shadow-lg"
                                        >
                                            <span className="hidden sm:inline">✨ Показать результат</span>
                                            <span className="sm:hidden">Результат</span>
                                        </button>
                                    </div>
                                </GlassCard>
                            )}
                        </div>

                        {/* Right Panel - Telegram News (Desktop Only) */}
                        <div className="hidden lg:block space-y-6 sticky top-8">
                            <TelegramNews />
                        </div>
                    </div>
                </div>

                {/* History Modal */}
                {showHistory && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
                        <GlassCard className="max-w-6xl w-full mx-4 max-h-[80vh] overflow-y-auto bg-white/90 backdrop-blur-xl">
                            <div className="p-8 border-b border-white/20">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl">
                                            <History className="h-6 w-6 text-white" />
                                        </div>
                                        <h2 className="text-3xl font-bold">
                                            <GradientText>История анализов</GradientText>
                                        </h2>
                                    </div>
                                    <button
                                        onClick={() => setShowHistory(false)}
                                        className="p-3 hover:bg-white/20 rounded-xl transition-all duration-300"
                                    >
                                        <X className="h-6 w-6 text-gray-500" />
                                    </button>
                                </div>
                            </div>
                            
                            <div className="p-8">
                                {history.length === 0 ? (
                                    <div className="text-center py-16">
                                        <Clock className="h-24 w-24 text-gray-400 mx-auto mb-6" />
                                        <h3 className="text-xl font-bold text-gray-900 mb-2">История пуста</h3>
                                        <p className="text-gray-500">Пока что нет выполненных анализов</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {history.map((item, index) => (
                                            <div key={index} className="bg-white/50 rounded-xl p-6 hover:bg-white/70 transition-all duration-300 border border-white/30">
                                                <div className="flex items-center justify-between mb-4">
                                                    <span className="font-bold text-gray-900 text-lg">{item.file_name}</span>
                                                    <span className="text-sm text-gray-500">{formatDate(item.timestamp)}</span>
                                                </div>
                                                <div className="flex items-center space-x-4 text-sm text-gray-600">
                                                    <span className="flex items-center space-x-1">
                                                        <FileText className="h-4 w-4" />
                                                        <span>{item.file_type}</span>
                                                    </span>
                                                    <span className="flex items-center space-x-1">
                                                        <Globe className="h-4 w-4" />
                                                        <span>{item.analysis_language}</span>
                                                    </span>
                                                    <span className="flex items-center space-x-1">
                                                        <Star className="h-4 w-4" />
                                                        <span>AI-анализ</span>
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </GlassCard>
                    </div>
                )}

                {/* Profile Modal */}
                {showProfile && (
                    <UserProfile onClose={() => setShowProfile(false)} />
                )}

                {/* Analysis Result Modal */}
                {showAnalysisResult && analysisResult && (
                    <SpectacularAnalysisResult 
                        analysisResult={analysisResult} 
                        onClose={() => setShowAnalysisResult(false)} 
                    />
                )}

                {/* Gemini API Key Setup Modal */}
                {showGeminiSetup && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full">
                            {/* Header */}
                            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-t-2xl">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center">
                                            <Sparkles className="h-5 w-5 text-white" />
                                        </div>
                                        <div>
                                            <h2 className="text-xl font-bold">Получить API ключ</h2>
                                            <p className="text-blue-100 text-sm">Быстрое получение за 1 минуту</p>
                                        </div>
                                    </div>
                                    <button 
                                        onClick={() => setShowGeminiSetup(false)}
                                        className="p-2 hover:bg-white/20 rounded-full transition-colors"
                                    >
                                        <X className="h-5 w-5" />
                                    </button>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="p-6">
                                <div className="space-y-4">
                                    <div className="bg-blue-50 rounded-xl p-4">
                                        <h3 className="font-semibold text-blue-900 mb-2">Получите бесплатный API ключ</h3>
                                        <p className="text-sm text-blue-800 mb-3">
                                            Нажмите кнопку ниже, чтобы перейти к Google AI Studio и получить API ключ
                                        </p>
                                        <div className="flex items-center space-x-2 mb-3">
                                            <span className="text-sm text-blue-700">Мы перенаправим вас на:</span>
                                            <code className="px-2 py-1 bg-blue-100 rounded text-sm font-mono">
                                                aistudio.google.com/apikey
                                            </code>
                                        </div>
                                    </div>

                                    <div className="bg-yellow-50 rounded-xl p-4">
                                        <h4 className="font-semibold text-yellow-800 mb-2">Простая инструкция:</h4>
                                        <ol className="text-sm text-yellow-700 space-y-1">
                                            <li>1. Нажмите "Получить API ключ"</li>
                                            <li>2. Войдите в Google аккаунт</li>
                                            <li>3. Нажмите "Create API key"</li>
                                            <li>4. Скопируйте ключ и вернитесь сюда</li>
                                        </ol>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Gemini API Key
                                        </label>
                                        <input
                                            type="password"
                                            placeholder="Вставьте ваш Gemini API ключ"
                                            value={geminiApiKey}
                                            onChange={(e) => setGeminiApiKey(e.target.value)}
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                        />
                                        <p className="text-xs text-gray-500 mt-1">
                                            Формат: AIza...
                                        </p>
                                    </div>

                                    {geminiKeyMessage && (
                                        <div className={`p-3 rounded-lg ${
                                            geminiKeySuccessful 
                                                ? 'bg-green-50 border border-green-200' 
                                                : 'bg-red-50 border border-red-200'
                                        }`}>
                                            <div className="flex items-center space-x-2">
                                                {geminiKeySuccessful ? (
                                                    <CheckCircle className="h-4 w-4 text-green-500" />
                                                ) : (
                                                    <AlertCircle className="h-4 w-4 text-red-500" />
                                                )}
                                                <span className={`text-sm ${
                                                    geminiKeySuccessful ? 'text-green-700' : 'text-red-700'
                                                }`}>
                                                    {geminiKeyMessage}
                                                </span>
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex space-x-3">
                                        <button
                                            onClick={() => window.open('https://aistudio.google.com/apikey', '_blank')}
                                            className="flex-1 inline-flex items-center justify-center space-x-2 bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-3 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
                                        >
                                            <Globe className="h-4 w-4" />
                                            <span>Получить API ключ</span>
                                        </button>
                                        <button
                                            onClick={handleGeminiKeySubmit}
                                            disabled={geminiKeyLoading || !geminiApiKey.trim()}
                                            className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                        >
                                            {geminiKeyLoading ? (
                                                <>
                                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                    <span>Сохраняю...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Sparkles className="h-4 w-4" />
                                                    <span>Сохранить</span>
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </TelegramWebApp>
    );
};

export default SuperMainApp;