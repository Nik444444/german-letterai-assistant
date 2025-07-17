// Utility functions for Telegram Web App detection and handling

export const isTelegramWebApp = () => {
    // Более надёжная проверка Telegram Web App API
    if (typeof window === 'undefined') return false;
    
    // Проверяем URL параметры для Telegram (только если они действительно есть)
    const urlParams = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    
    // Проверяем наличие реальных Telegram-специфических параметров
    if (urlParams.has('tgWebAppData') && urlParams.get('tgWebAppData')) {
        return true;
    }
    
    if (hashParams.has('tgWebAppData') && hashParams.get('tgWebAppData')) {
        return true;
    }
    
    // Если мы на /telegram роуте и есть реальный Telegram API, считаем это Telegram средой
    if (window.location.pathname === '/telegram' && window.Telegram && window.Telegram.WebApp) {
        const webApp = window.Telegram.WebApp;
        // Проверяем что это не browser automation
        const hasRealTelegramData = !!(
            webApp.initData && 
            webApp.initData.length > 0 && 
            webApp.version &&
            webApp.platform &&
            webApp.platform !== 'unknown' &&
            !webApp.initData.includes('browser_automation') // исключаем browser automation
        );
        return hasRealTelegramData;
    }
    
    // Проверяем наличие реального Telegram Web App API
    if (!window.Telegram || !window.Telegram.WebApp) return false;
    
    const webApp = window.Telegram.WebApp;
    
    // Проверяем специфические свойства которые есть только в реальном Telegram
    // и исключаем случаи browser automation
    const hasRealTelegramData = !!(
        webApp.initData && 
        webApp.initData.length > 0 && 
        webApp.version &&
        webApp.platform &&
        webApp.platform !== 'unknown' &&
        !webApp.initData.includes('browser_automation') // исключаем browser automation
    );
    
    return hasRealTelegramData;
};

export const getTelegramWebApp = () => {
    if (isTelegramWebApp()) {
        return window.Telegram.WebApp;
    }
    return null;
};

export const getTelegramUser = () => {
    const webApp = getTelegramWebApp();
    if (webApp && webApp.initDataUnsafe && webApp.initDataUnsafe.user) {
        return webApp.initDataUnsafe.user;
    }
    return null;
};

export const setupTelegramWebApp = () => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        // Расширяем приложение на весь экран
        webApp.expand();
        
        // Настраиваем тему
        webApp.setHeaderColor('bg_color');
        webApp.setBackgroundColor('#1a1a2e');
        
        // Скрываем кнопку Back, если она есть
        webApp.BackButton.hide();
        
        // Готовим приложение
        webApp.ready();
        
        return webApp;
    }
    return null;
};

export const showTelegramAlert = (message) => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        webApp.showAlert(message);
    } else {
        alert(message);
    }
};

export const showTelegramConfirm = (message, callback) => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        webApp.showConfirm(message, callback);
    } else {
        const result = confirm(message);
        callback(result);
    }
};

export const closeTelegramWebApp = () => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        webApp.close();
    }
};

export const hapticFeedback = (type = 'light') => {
    const webApp = getTelegramWebApp();
    if (webApp && webApp.HapticFeedback) {
        switch (type) {
            case 'light':
                webApp.HapticFeedback.impactOccurred('light');
                break;
            case 'medium':
                webApp.HapticFeedback.impactOccurred('medium');
                break;
            case 'heavy':
                webApp.HapticFeedback.impactOccurred('heavy');
                break;
            case 'soft':
                webApp.HapticFeedback.impactOccurred('soft');
                break;
            case 'rigid':
                webApp.HapticFeedback.impactOccurred('rigid');
                break;
            case 'success':
                webApp.HapticFeedback.notificationOccurred('success');
                break;
            case 'warning':
                webApp.HapticFeedback.notificationOccurred('warning');
                break;
            case 'error':
                webApp.HapticFeedback.notificationOccurred('error');
                break;
            default:
                webApp.HapticFeedback.impactOccurred('light');
        }
    }
};