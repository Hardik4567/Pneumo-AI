/**
 * ==========================================================================
 * PneumoAI - Prediction History Manager
 * File: history.js
 * Version: 1.0.0
 * Description: Manages prediction history storage and display
 * ==========================================================================
 */

'use strict';

(function () {
    /* ==========================================================================
       CONFIGURATION & STATE
       ========================================================================== */
    const CONFIG = {
        STORAGE_KEY: 'pneumo_history',
        MAX_HISTORY: 50,
        STORAGE_TYPE: 'localStorage' // or 'sessionStorage'
    };

    let history = [];

    /* ==========================================================================
       STORAGE MANAGEMENT
       ========================================================================== */
    const storage = {
        get: (key) => {
            try {
                const data = localStorage.getItem(key);
                return data ? JSON.parse(data) : null;
            } catch (error) {
                console.error('Storage get error:', error);
                return null;
            }
        },
        set: (key, value) => {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },
        remove: (key) => {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        }
    };

    /* ==========================================================================
       HISTORY OPERATIONS
       ========================================================================== */
    const loadHistory = () => {
        history = storage.get(CONFIG.STORAGE_KEY) || [];
        return history;
    };

    const saveHistory = () => {
        // Keep only the most recent entries
        if (history.length > CONFIG.MAX_HISTORY) {
            history = history.slice(0, CONFIG.MAX_HISTORY);
        }
        return storage.set(CONFIG.STORAGE_KEY, history);
    };

    const addToHistory = (predictionData) => {
        if (!predictionData) return false;

        const entry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            prediction: predictionData.data?.prediction || predictionData.prediction || 'Unknown',
            confidence: predictionData.data?.confidence || predictionData.confidence || 0,
            imageThumbnail: predictionData.data?.thumbnail || null,
            fullData: predictionData,
            displayTime: new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'short',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }).format(new Date())
        };

        history.unshift(entry);
        return saveHistory();
    };

    const getHistory = () => {
        return loadHistory();
    };

    const clearHistory = () => {
        history = [];
        return storage.remove(CONFIG.STORAGE_KEY);
    };

    const removeFromHistory = (id) => {
        const index = history.findIndex(h => h.id === id);
        if (index !== -1) {
            history.splice(index, 1);
            return saveHistory();
        }
        return false;
    };

    const getHistoryItem = (id) => {
        return history.find(h => h.id === id) || null;
    };

    /* ==========================================================================
       DOM FUNCTIONS
       ========================================================================== */
    const renderHistoryList = (containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        loadHistory();

        if (history.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info text-center py-5">
                    <i class="fa-solid fa-inbox fa-2x mb-3 d-block"></i>
                    <p class="mb-0">No prediction history yet. Start a new analysis to see your results here.</p>
                </div>
            `;
            return;
        }

        const historyHTML = history.map(item => `
            <div class="card border-0 shadow-sm mb-3">
                <div class="card-body p-3">
                    <div class="row align-items-center g-3">
                        <div class="col-auto">
                            ${item.imageThumbnail ? 
                                `<img src="${item.imageThumbnail}" alt="Thumbnail" class="rounded" style="width: 60px; height: 60px; object-fit: cover;">` :
                                `<div class="bg-light rounded d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;"><i class="fa-solid fa-image text-muted"></i></div>`
                            }
                        </div>
                        <div class="col">
                            <div class="d-flex align-items-center gap-2">
                                <h5 class="mb-0 fw-bold">
                                    ${item.prediction === 'PNEUMONIA' ? 
                                        '<span class="badge bg-danger">Pneumonia Detected</span>' : 
                                        '<span class="badge bg-success">Normal</span>'
                                    }
                                </h5>
                            </div>
                            <small class="text-muted d-block">${item.displayTime}</small>
                            <div class="mt-1">
                                <small class="text-muted">Confidence: <strong>${item.confidence.toFixed(2)}%</strong></small>
                            </div>
                        </div>
                        <div class="col-auto">
                            <button class="btn btn-sm btn-outline-primary" onclick="window.PneumoHistory.viewItem(${item.id})">
                                <i class="fa-solid fa-eye"></i> View
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="window.PneumoHistory.deleteItem(${item.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="mb-3">
                <button class="btn btn-sm btn-outline-danger" onclick="window.PneumoHistory.clearAll()">
                    <i class="fa-solid fa-trash-can me-1"></i>Clear All History
                </button>
            </div>
            ${historyHTML}
        `;
    };

    const initHistoryUI = () => {
        const historyContainer = document.getElementById('historyContainer');
        if (historyContainer) {
            renderHistoryList('historyContainer');
        }
    };

    /* ==========================================================================
       EVENT HANDLERS
       ========================================================================== */
    const viewHistoryItem = (id) => {
        const item = getHistoryItem(id);
        if (item) {
            sessionStorage.setItem('pneumo_prediction_result', JSON.stringify(item.fullData));
            window.location.href = '/results';
        }
    };

    const deleteHistoryItem = (id) => {
        if (confirm('Are you sure you want to delete this entry?')) {
            removeFromHistory(id);
            initHistoryUI();
        }
    };

    const clearAllHistory = () => {
        if (confirm('Are you sure you want to clear all prediction history? This cannot be undone.')) {
            clearHistory();
            initHistoryUI();
        }
    };

    /* ==========================================================================
       INITIALIZATION
       ========================================================================== */
    const init = () => {
        loadHistory();
        initHistoryUI();
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose API for external use
    window.PneumoHistory = {
        add: addToHistory,
        get: getHistory,
        getItem: getHistoryItem,
        remove: removeFromHistory,
        clear: clearHistory,
        render: renderHistoryList,
        viewItem: viewHistoryItem,
        deleteItem: deleteHistoryItem,
        clearAll: clearAllHistory
    };
})();
