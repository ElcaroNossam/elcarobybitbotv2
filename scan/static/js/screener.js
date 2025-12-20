document.addEventListener("DOMContentLoaded", () => {
    // Управление заставкой - показываем пока грузится скрипт
    const splashScreen = document.getElementById('splash-screen');
    if (splashScreen) {
        // Убеждаемся что заставка видна сразу
        splashScreen.style.opacity = '1';
        splashScreen.style.visibility = 'visible';
        splashScreen.style.display = 'flex';
        
        const splashStartTime = Date.now();
        const MIN_SPLASH_DURATION = 800; // Минимум 2.5 секунды для красоты
        const MAX_SPLASH_DURATION = 3000; // Максимум 6 секунд
        
        // Функция для скрытия заставки когда все готово
        const hideSplash = () => {
            if (splashScreen && splashScreen.classList) {
                splashScreen.classList.add('hidden');
                // Удаляем заставку из DOM после анимации
                setTimeout(() => {
                    if (splashScreen && splashScreen.parentElement) {
                        splashScreen.remove();
                    }
                }, 1000); // Увеличена задержка для плавности
            }
        };
        
        // Скрываем заставку когда:
        // 1. Данные загружены И прошло минимум 2.5 секунды для красоты
        // 2. Или через максимум 6 секунд (fallback)
        let splashHidden = false;
        let dataReady = false;
        
        const hideSplashWhenReady = () => {
            if (splashHidden) return;
            
            dataReady = true;
            const elapsed = Date.now() - splashStartTime;
            
            // Если прошло меньше минимального времени, ждем остаток
            if (elapsed < MIN_SPLASH_DURATION) {
                const remainingTime = MIN_SPLASH_DURATION - elapsed;
                setTimeout(() => {
                    splashHidden = true;
                    hideSplash();
                }, remainingTime);
            } else {
                // Уже прошло достаточно времени, скрываем сразу
                splashHidden = true;
                hideSplash();
            }
        };
        
        // Fallback: скрываем через максимальное время
        setTimeout(() => {
            if (!splashHidden) {
                splashHidden = true;
                hideSplash();
            }
        }, MAX_SPLASH_DURATION);
        
        // Сохраняем функцию для вызова из обработчиков загрузки данных
        window._hideSplashScreen = hideSplashWhenReady;
    }
    
    const screenerTableBody = document.getElementById("screener-table-body");
    
    // WebSocket connection
    let ws = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 10;
    const RECONNECT_DELAY = 3000; // 3 seconds
    let reconnectTimeoutId = null;

    const availableColumns = window.SCREENER_AVAILABLE_COLUMNS || [];
    const storageKey = "screener_visible_columns";
    const languageStorageKey = "preferred_language";
    const favoritesStorageKey = "screener_favorites"; // Максимум 20 символов
    const compactNumbersStorageKey = "screener_compact_numbers";
    const MAX_FAVORITES = 20;
    
    // Настройка компактных чисел (K, M, B суффиксы)
    let compactNumbers = loadCompactNumbers();
    
    function loadCompactNumbers() {
        try {
            const raw = localStorage.getItem(compactNumbersStorageKey);
            if (raw === null) return false; // По умолчанию выключено
            return raw === 'true';
        } catch (e) {
            return false;
        }
    }
    
    function saveCompactNumbers(value) {
        try {
            localStorage.setItem(compactNumbersStorageKey, value ? 'true' : 'false');
        } catch (e) {
            // ignore
        }
    }
    
    // Track if user is interacting with the page
    let isUserInteracting = false;
    let interactionTimeout = null;
    
    // Track last update time
    let lastRefreshTime = 0;
    
    // Track if table has been initialized (first render)
    let isTableInitialized = false;
    
    // Track user interactions to pause auto-refresh
    document.addEventListener('mousedown', () => {
        isUserInteracting = true;
        clearTimeout(interactionTimeout);
        interactionTimeout = setTimeout(() => {
            isUserInteracting = false;
        }, 2000); // Reset after 2s of no interaction
    });
    
    document.addEventListener('keydown', () => {
        isUserInteracting = true;
        clearTimeout(interactionTimeout);
        interactionTimeout = setTimeout(() => {
            isUserInteracting = false;
        }, 2000);
    });
    
    // Store previous values for comparison (for volume, ticks, volatility, OI)
    let previousValues = new Map(); // key: symbol, value: object with previous values
    
    // Store color states with update counters (for 8-update persistence)
    // key: `${symbol}_${column}`, value: { class: "value-up"|"value-down"|"", updatesLeft: 0-8 }
    let colorStates = new Map();
    const COLOR_PERSIST_UPDATES = 8; // Кількість оновлень для утримання кольору
    
    // Map для быстрого поиска строк по символу (оптимизация)
    // key: symbol, value: { row: HTMLElement, cells: Map<column, HTMLElement> }
    let rowCache = new Map();
    
    // Use global language functions from base.html
    function getLanguagePrefix() {
        if (window.getLanguagePrefix) {
            return window.getLanguagePrefix();
        }
        // Fallback if global function not available
        const currentPath = window.location.pathname;
        const langMatch = currentPath.match(/^\/(ru|en|es|he)\//);
        if (langMatch && langMatch[1]) {
            return langMatch[1];
        }
        // If no prefix in URL, it's default language (ru) - but we still need prefix for API
        // Check localStorage
        try {
            const savedLang = localStorage.getItem('preferred_language');
            if (savedLang && ['ru', 'en', 'es', 'he'].includes(savedLang)) {
                return savedLang;
            }
        } catch (e) {
            // ignore
        }
        // Default to Russian
        return 'ru';
    }

    // Default visible columns (matching initial display)
    const defaultVisible = new Set([
        "symbol",
        "price",
        "change_5m",
        "oi_change_5m",
        "volatility_5m",
        "ticks_5m",
        "vdelta_5m",
        "volume_5m",
        "vdelta_1d",
        "volume_1d",
        "funding_rate",
        "open_interest",
        "ts",
    ]);

    function loadVisibleColumns() {
        try {
            const raw = localStorage.getItem(storageKey);
            if (!raw) return defaultVisible;
            const parsed = JSON.parse(raw);
            if (!Array.isArray(parsed)) return defaultVisible;
            return new Set(parsed);
        } catch (e) {
            return defaultVisible;
        }
    }

    function saveVisibleColumns(set) {
        try {
            localStorage.setItem(storageKey, JSON.stringify(Array.from(set)));
        } catch (e) {
            // ignore
        }
    }

    const visibleColumns = loadVisibleColumns();

    function applyColumnVisibility() {
        // Apply visibility even if availableColumns is not set yet (for server-rendered HTML)
        const table = document.getElementById("screener-main-table");
        if (!table) return;
        
        // If availableColumns is not set, try to get columns from table headers
        const allColumns = availableColumns.length > 0 
            ? availableColumns 
            : Array.from(table.querySelectorAll("thead th[data-column]")).map(th => th.getAttribute("data-column")).filter(Boolean);
        
        if (allColumns.length === 0) return;

        // Apply to header cells - use more reliable method
        const headerCells = table.querySelectorAll("thead th[data-column]");
        headerCells.forEach((th) => {
            const col = th.getAttribute("data-column");
            if (!col) return;
            const visible = visibleColumns.has(col);
            // Force hide/show with !important via style attribute
            if (visible) {
                th.style.display = "table-cell";
                th.style.visibility = "visible";
                th.style.opacity = "1";
                th.removeAttribute("hidden");
                th.classList.remove("hidden-column");
            } else {
                th.style.display = "none";
                th.style.visibility = "hidden";
                th.style.opacity = "0";
                th.setAttribute("hidden", "true");
                th.classList.add("hidden-column");
            }
        });

        // Apply to body cells - use more reliable method
        const rows = table.querySelectorAll("tbody tr");
        rows.forEach((tr) => {
            tr.querySelectorAll("td[data-column]").forEach((td) => {
                const col = td.getAttribute("data-column");
                if (!col) return;
                const visible = visibleColumns.has(col);
                // Force hide/show with !important via style attribute
                if (visible) {
                    td.style.display = "table-cell";
                    td.style.visibility = "visible";
                    td.style.opacity = "1";
                    td.removeAttribute("hidden");
                    td.classList.remove("hidden-column");
                } else {
                    td.style.display = "none";
                    td.style.visibility = "hidden";
                    td.style.opacity = "0";
                    td.setAttribute("hidden", "true");
                    td.classList.add("hidden-column");
                }
            });
        });

        // Update checkboxes in settings panel if it exists.
        document
            .querySelectorAll(".screener-settings input[type=checkbox][data-column]")
            .forEach((cb) => {
                const col = cb.getAttribute("data-column");
                if (!col) return;
                cb.checked = visibleColumns.has(col);
                const label = cb.closest("label.settings-button");
                if (label) {
                    if (cb.checked) label.classList.add("selected");
                    else label.classList.remove("selected");
                }
            });
    }

    function buildSettingsPanel() {
        const btn = document.getElementById("toggle-settings");
        if (!btn) return;

        // Ищем панель или создаем в body (для правильного центрирования)
        let panel = document.getElementById("screener-settings-panel");
        if (!panel) {
            panel = document.createElement("div");
            panel.className = "screener-settings";
            panel.id = "screener-settings-panel";
            document.body.appendChild(panel);
        }
        
        // Clear existing event listeners by removing and re-adding panel content
        const existingInner = panel.querySelector(".screener-settings-inner");
        if (existingInner) {
            existingInner.remove();
        }

        // Порядок таймфреймов: 1m, 3m, 5m, 15m, 30m, 1h, 4h, 8h, 1d
        const timeframeOrder = ["_1m", "_3m", "_5m", "_15m", "_30m", "_1h", "_4h", "_8h", "_1d"];
        
        // Функция для сортировки колонок по таймфреймам
        const sortByTimeframe = (cols) => {
            return cols.sort((a, b) => {
                const aIdx = timeframeOrder.findIndex(tf => a.endsWith(tf));
                const bIdx = timeframeOrder.findIndex(tf => b.endsWith(tf));
                if (aIdx === -1 && bIdx === -1) return 0;
                if (aIdx === -1) return 1;
                if (bIdx === -1) return -1;
                return aIdx - bIdx;
            });
        };
        
        const categories = {
            "Change": sortByTimeframe(["change_1m", "change_3m", "change_5m", "change_15m", "change_30m", "change_1h", "change_4h", "change_8h", "change_1d"]),
            "OI Change": sortByTimeframe(["oi_change_1m", "oi_change_3m", "oi_change_5m", "oi_change_15m", "oi_change_30m", "oi_change_1h", "oi_change_4h", "oi_change_8h", "oi_change_1d"]),
            "Volatility": sortByTimeframe(["volatility_1m", "volatility_3m", "volatility_5m", "volatility_15m", "volatility_30m", "volatility_1h", "volatility_4h", "volatility_8h", "volatility_1d"]),
            "Ticks": sortByTimeframe(["ticks_1m", "ticks_3m", "ticks_5m", "ticks_15m", "ticks_30m", "ticks_1h", "ticks_4h", "ticks_8h", "ticks_1d"]),
            "Vdelta": sortByTimeframe(["vdelta_1m", "vdelta_3m", "vdelta_5m", "vdelta_15m", "vdelta_30m", "vdelta_1h", "vdelta_4h", "vdelta_8h", "vdelta_1d"]),
            "Volume": sortByTimeframe(["volume_1m", "volume_3m", "volume_5m", "volume_15m", "volume_30m", "volume_1h", "volume_4h", "volume_8h", "volume_1d"]),
            "Others": ["symbol", "price", "funding_rate", "open_interest", "ts"],
        };

        let html = `
            <div class="screener-settings-inner">
                <div class="settings-header">
                    <h2>${window.__ ? window.__('Screener Settings') : 'Screener Settings'}</h2>
                    <button type="button" class="close-settings" id="close-settings">×</button>
                </div>
                <p class="chart-note">${window.__ ? window.__('Customize the table display by selecting the columns you want to see.') : 'Customize the table display by selecting the columns you want to see.'}</p>
                <div class="settings-columns">
        `;

        for (const [category, cols] of Object.entries(categories)) {
            html += `<div class="settings-category"><strong>${category}:</strong>`;
            
            // Все колонки в правильном порядке (1m, 2m, 3m, 5m, 15m, 30m, 1h, 8h, 1d)
            html += `<div class="settings-buttons">`;
            cols.forEach((col) => {
                const checked = visibleColumns.has(col) ? "checked" : "";
                const selected = visibleColumns.has(col) ? "selected" : "";
                const label = col.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
                html += `<label class="settings-button ${selected}" data-column="${col}">
                    <input type="checkbox" data-column="${col}" ${checked} style="display:none">
                    ${label}
                </label>`;
            });
            html += `</div>`;
            
            html += `</div>`;
        }

        // Загружаем настройки ликвидаций
        const liquidationSettings = getLiquidationSettings();
        
        html += `
                </div>
                <div class="settings-display">
                    <h3 style="margin-bottom: 0.5rem; color: #ff40b3;">${window.__ ? window.__('Display Settings') : 'Display Settings'}</h3>
                    <div class="display-settings-group">
                        <label class="liquidation-setting-item">
                            <input type="checkbox" id="compact-numbers-toggle" ${compactNumbers ? 'checked' : ''}>
                            <span>${window.__ ? window.__('Compact numbers (K, M, B suffixes)') : 'Compact numbers (K, M, B suffixes)'}</span>
                        </label>
                        <p style="font-size: 0.8rem; color: #888; margin: 0.5rem 0 0 1.5rem;">
                            ${window.__ ? window.__('Example: 1,234,567$ → 1.23M$') : 'Example: 1,234,567$ → 1.23M$'}
                        </p>
                    </div>
                </div>
                <div class="settings-liquidation">
                    <h3 style="margin-top: 1.5rem; margin-bottom: 0.5rem; color: #ff40b3;">Liquidation Alerts</h3>
                    <div class="liquidation-settings-group">
                        <label class="liquidation-setting-item">
                            <input type="checkbox" id="liquidation-alerts-enabled" ${liquidationSettings.alertsEnabled ? 'checked' : ''}>
                            <span>Enable liquidation alerts</span>
                        </label>
                        <label class="liquidation-setting-item" for="liquidation-min-notional">
                            <span>Minimum liquidation threshold ($):</span>
                            <input type="number" id="liquidation-min-notional" 
                                   min="0" step="1000" 
                                   value="${liquidationSettings.minNotional}"
                                   style="width: 150px; padding: 0.5rem; margin-left: 0.5rem; background: #050505; border: 1px solid #ff008033; border-radius: 4px; color: #c5c6c7;">
                        </label>
                    </div>
                    <div class="liquidation-settings-group" style="margin-top: 1rem;">
                        <h4 style="color: #ff40b3; margin-bottom: 0.5rem; font-size: 0.9rem;">Notification Settings</h4>
                        <label class="liquidation-setting-item">
                            <span>Notification position:</span>
                            <select id="liquidation-notification-position" 
                                    style="width: 150px; padding: 0.5rem; margin-left: 0.5rem; background: #050505; border: 1px solid #ff008033; border-radius: 4px; color: #c5c6c7;">
                                <option value="top-right" ${liquidationSettings.notificationPosition === 'top-right' ? 'selected' : ''}>Top Right</option>
                                <option value="top-left" ${liquidationSettings.notificationPosition === 'top-left' ? 'selected' : ''}>Top Left</option>
                                <option value="bottom-right" ${liquidationSettings.notificationPosition === 'bottom-right' ? 'selected' : ''}>Bottom Right</option>
                                <option value="bottom-left" ${liquidationSettings.notificationPosition === 'bottom-left' ? 'selected' : ''}>Bottom Left</option>
                                <option value="top-center" ${liquidationSettings.notificationPosition === 'top-center' ? 'selected' : ''}>Top Center</option>
                                <option value="bottom-center" ${liquidationSettings.notificationPosition === 'bottom-center' ? 'selected' : ''}>Bottom Center</option>
                            </select>
                        </label>
                        <label class="liquidation-setting-item" style="margin-top: 0.5rem;">
                            <input type="checkbox" id="liquidation-notification-sound" ${liquidationSettings.notificationSound ? 'checked' : ''}>
                            <span>Play sound on liquidation</span>
                        </label>
                        <label class="liquidation-setting-item" style="margin-top: 0.5rem;">
                            <span>Notification duration (seconds):</span>
                            <input type="number" id="liquidation-notification-duration" 
                                   min="2" max="30" step="1" 
                                   value="${liquidationSettings.notificationDuration || 5}"
                                   style="width: 100px; padding: 0.5rem; margin-left: 0.5rem; background: #050505; border: 1px solid #ff008033; border-radius: 4px; color: #c5c6c7;">
                        </label>
                    </div>
                </div>
                <div class="settings-footer">
                    <div class="settings-reset">
                        <span>${window.__ ? window.__('Restore Default Column Order') : 'Restore Default Column Order'}</span>
                        <button type="button" class="btn-secondary" id="reset-settings">${window.__ ? window.__('Reset') : 'Reset'}</button>
                    </div>
                </div>
            </div>
        `;

        panel.innerHTML = html;
        
        // КРИТИЧНО: Удаляем все inline стили которые могут блокировать CSS !important
        panel.style.cssText = '';
        // Восстанавливаем только класс, все остальное из CSS
        panel.className = 'screener-settings';
        panel.id = 'screener-settings-panel';
        
        // Предотвращаем всплытие кликов с панели к overlay
        panel.addEventListener("click", (e) => {
            e.stopPropagation();
        });

        // Use event delegation for settings buttons
        panel.addEventListener("click", (e) => {
            const label = e.target.closest("label.settings-button");
            if (!label) return;
            
            e.preventDefault();
            
            const cb = label.querySelector("input[type=checkbox]");
            if (!cb) return;
            
            const col = label.dataset.column;
            if (!col) {
                return;
            }
            
            // Toggle checkbox state
            cb.checked = !cb.checked;
            
            // Update visibleColumns set
            if (cb.checked) {
                visibleColumns.add(col);
                label.classList.add("selected");
            } else {
                visibleColumns.delete(col);
                label.classList.remove("selected");
            }
            
            // Save to localStorage
            saveVisibleColumns(visibleColumns);
            
            // Immediately apply visibility changes - use requestAnimationFrame for reliable DOM update
            requestAnimationFrame(() => {
                applyColumnVisibility();
            });
        });

        const closeBtn = panel.querySelector("#close-settings");
        if (closeBtn) {
            closeBtn.addEventListener("click", (e) => {
                e.preventDefault();
                e.stopPropagation();
                panel.classList.remove("open");
                
                // Скрываем панель полностью (включая inline стили)
                panel.style.cssText = 'display: none !important;';
                
                // Скрываем overlay
                const overlay = document.getElementById("settings-overlay");
                if (overlay) overlay.style.display = 'none';
                
                // Apply liquidation settings when panel closes
                const settings = getLiquidationSettings();
                applyLiquidationSettings(settings);
            });
        }

        const resetBtn = panel.querySelector("#reset-settings");
        if (resetBtn) {
            resetBtn.addEventListener("click", (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // 1. Скидаємо видимість колонок до дефолтних
                visibleColumns.clear();
                defaultVisible.forEach((col) => visibleColumns.add(col));
                saveVisibleColumns(visibleColumns);
                
                // 2. Скидаємо порядок колонок
                localStorage.removeItem('screener_column_order');
                
                // 3. Скидаємо налаштування ліквідацій до дефолтних
                saveLiquidationSettings(DEFAULT_LIQUIDATION_SETTINGS);
                applyLiquidationSettings(DEFAULT_LIQUIDATION_SETTINGS);
                
                // 4. Застосовуємо зміни
                applyColumnVisibility();
                
                // 5. Перебудовуємо панель для оновлення чекбоксів і полів
                buildSettingsPanel();
                
                // 6. Перезавантажуємо сторінку для скидання порядку колонок
                window.location.reload();
            });
        }
        
        // Обработчик для compact numbers toggle
        const compactNumbersToggle = panel.querySelector("#compact-numbers-toggle");
        if (compactNumbersToggle) {
            compactNumbersToggle.addEventListener("change", (e) => {
                compactNumbers = e.target.checked;
                saveCompactNumbers(compactNumbers);
                // Перерисовываем таблицу с новым форматированием
                refreshAllRows();
            });
        }
        
        // Обработчики для настроек ликвидаций
        const alertsEnabledCheckbox = panel.querySelector("#liquidation-alerts-enabled");
        const minNotionalInput = panel.querySelector("#liquidation-min-notional");
        const notificationPositionSelect = panel.querySelector("#liquidation-notification-position");
        const notificationSoundCheckbox = panel.querySelector("#liquidation-notification-sound");
        const notificationDurationInput = panel.querySelector("#liquidation-notification-duration");
        
        if (alertsEnabledCheckbox) {
            alertsEnabledCheckbox.addEventListener("change", (e) => {
                const settings = getLiquidationSettings();
                settings.alertsEnabled = e.target.checked;
                saveLiquidationSettings(settings);
                applyLiquidationSettings(settings);
            });
        }
        
        if (minNotionalInput) {
            minNotionalInput.addEventListener("change", (e) => {
                const value = parseFloat(e.target.value) || 0;
                const settings = getLiquidationSettings();
                settings.minNotional = Math.max(0, value);
                saveLiquidationSettings(settings);
                e.target.value = settings.minNotional; // Обновляем значение в поле
                applyLiquidationSettings(settings);
            });
            
            // Также сохраняем при потере фокуса
            minNotionalInput.addEventListener("blur", (e) => {
                const value = parseFloat(e.target.value) || 0;
                const settings = getLiquidationSettings();
                settings.minNotional = Math.max(0, value);
                saveLiquidationSettings(settings);
                e.target.value = settings.minNotional;
                applyLiquidationSettings(settings);
            });
        }
        
        if (notificationPositionSelect) {
            notificationPositionSelect.addEventListener("change", (e) => {
                const settings = getLiquidationSettings();
                settings.notificationPosition = e.target.value;
                saveLiquidationSettings(settings);
                applyLiquidationSettings(settings);
            });
        }
        
        if (notificationSoundCheckbox) {
            notificationSoundCheckbox.addEventListener("change", (e) => {
                const settings = getLiquidationSettings();
                settings.notificationSound = e.target.checked;
                saveLiquidationSettings(settings);
                applyLiquidationSettings(settings);
            });
        }
        
        if (notificationDurationInput) {
            notificationDurationInput.addEventListener("change", (e) => {
                const value = parseInt(e.target.value) || 5;
                const settings = getLiquidationSettings();
                settings.notificationDuration = Math.max(2, Math.min(30, value));
                saveLiquidationSettings(settings);
                e.target.value = settings.notificationDuration;
                applyLiquidationSettings(settings);
            });
            
            notificationDurationInput.addEventListener("blur", (e) => {
                const value = parseInt(e.target.value) || 5;
                const settings = getLiquidationSettings();
                settings.notificationDuration = Math.max(2, Math.min(30, value));
                saveLiquidationSettings(settings);
                e.target.value = settings.notificationDuration;
                applyLiquidationSettings(settings);
            });
        }
    }
    
    // Функция для перерисовки всех строк таблицы с новым форматированием
    function refreshAllRows() {
        // Очищаем кэш строк чтобы форсировать перерисовку
        rowCache.clear();
        colorStates.clear();
        // Заново рендерим все данные если есть
        if (window._lastScreenerData && window._lastScreenerData.length > 0) {
            renderScreenerTable(window._lastScreenerData);
        }
    }

    function setupFiltersToggle() {
        const toggleBtn = document.getElementById("toggle-filters");
        const filtersForm = document.getElementById("screener-filters-form");
        const toggleIcon = toggleBtn ? toggleBtn.querySelector(".filters-toggle-icon") : null;
        
        if (!toggleBtn || !filtersForm) {
            return;
        }
        
        // Инициализация: форма скрыта по умолчанию
        filtersForm.style.display = "none";
        filtersForm.removeAttribute("aria-hidden"); // Убираем aria-hidden при инициализации
        toggleBtn.classList.remove("active");
        toggleBtn.setAttribute("aria-expanded", "false");
        if (toggleIcon) toggleIcon.textContent = "▼";

        // Обработчик клика
        toggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const isVisible = filtersForm.style.display !== "none" && 
                             filtersForm.style.display !== "" &&
                             window.getComputedStyle(filtersForm).display !== "none";
            
            if (isVisible) {
                // Скрываем форму
                filtersForm.style.display = "none";
                filtersForm.setAttribute("aria-hidden", "true");
                toggleBtn.classList.remove("active");
                toggleBtn.setAttribute("aria-expanded", "false");
                if (toggleIcon) {
                    toggleIcon.textContent = "▼";
                }
            } else {
                // Показываем форму
                filtersForm.style.display = "flex";
                filtersForm.removeAttribute("aria-hidden");
                toggleBtn.classList.add("active");
                toggleBtn.setAttribute("aria-expanded", "true");
                if (toggleIcon) {
                    toggleIcon.textContent = "▲";
                }
            }
        });
    }

    // Attach toggle button handler (outside buildSettingsPanel to avoid duplicates)
    function attachToggleButton() {
        const btn = document.getElementById("toggle-settings");
        if (!btn) return;
        
        // Remove all existing click handlers by cloning
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        function togglePanel() {
            const panel = document.getElementById("screener-settings-panel") || document.querySelector(".screener-settings");
            let overlay = document.getElementById("settings-overlay");
            
            // Create overlay if it doesn't exist
            if (!overlay) {
                overlay = document.createElement("div");
                overlay.id = "settings-overlay";
                overlay.className = "settings-overlay";
                overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.85); z-index: 9998; display: none;';
                // Вставляем overlay ПЕРЕД панелью чтобы панель была поверх
                if (panel && panel.parentNode) {
                    panel.parentNode.insertBefore(overlay, panel);
                } else {
                    document.body.appendChild(overlay);
                }
                
                overlay.addEventListener('click', (e) => {
                    e.stopPropagation();
                    closePanel();
                });
            }
            
            if (!panel) return;
            
            const isOpen = panel.classList.contains("open");
            if (isOpen) {
                closePanel();
            } else {
                openPanel(overlay, panel);
            }
        }
        
        function openPanel(overlay, panel) {
            // КРИТИЧНО: Переносим overlay и panel в body для правильного z-index
            if (overlay && overlay.parentNode !== document.body) {
                document.body.appendChild(overlay);
            }
            if (panel && panel.parentNode !== document.body) {
                document.body.appendChild(panel);
            }
            
            // Show overlay с правильным z-index
            overlay.style.cssText = `
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                background: rgba(0, 0, 0, 0.85) !important;
                z-index: 99999 !important;
                display: block !important;
            `;
            
            // Show panel with inline styles to ensure visibility
            panel.style.cssText = `
                display: block !important;
                position: fixed !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) scale(1) !important;
                visibility: visible !important;
                opacity: 1 !important;
                pointer-events: auto !important;
                z-index: 100000 !important;
                width: 90% !important;
                max-width: 600px !important;
                max-height: 90vh !important;
                background: linear-gradient(135deg, #0b0c10 0%, #150510 50%, #0b0c10 100%) !important;
                border: 2px solid #ff0080 !important;
                border-radius: 12px !important;
                overflow-y: auto !important;
                padding: 1.5rem !important;
                box-sizing: border-box !important;
                box-shadow: 0 0 60px rgba(255, 0, 128, 0.5), 0 20px 60px rgba(0, 0, 0, 0.9) !important;
            `;
            panel.classList.add("open");
        }
        
        function closePanel() {
            const panel = document.getElementById("screener-settings-panel");
            const overlay = document.getElementById("settings-overlay");
            
            if (panel) {
                panel.classList.remove("open");
                panel.style.cssText = 'display: none !important;';
            }
            if (overlay) overlay.style.display = 'none';
            
            // Apply liquidation settings when panel closes
            const settings = getLiquidationSettings();
            applyLiquidationSettings(settings);
        }
        
        newBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            togglePanel();
        });
    }

    // Setup draggable WebSocket status indicator
    function setupDraggableStatusIndicator() {
        const indicator = document.getElementById('ws-status-indicator');
        if (!indicator) return;

        const STORAGE_KEY = 'ws_status_position';
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        // Load saved position
        const savedPosition = localStorage.getItem(STORAGE_KEY);
        if (savedPosition) {
            try {
                const { top, left, right } = JSON.parse(savedPosition);
                if (left !== undefined) {
                    indicator.style.left = left + 'px';
                    indicator.style.right = 'auto';
                } else if (right !== undefined) {
                    indicator.style.right = right + 'px';
                    indicator.style.left = 'auto';
                }
                if (top !== undefined) {
                    indicator.style.top = top + 'px';
                }
            } catch (e) {
                console.warn('Failed to load saved position:', e);
            }
        }

        // Get header element for drag
        const header = indicator.querySelector('.ws-status-header') || indicator;

        function onMouseDown(e) {
            // Only drag from header
            if (!header.contains(e.target)) return;
            
            isDragging = true;
            indicator.classList.add('dragging');
            
            const rect = indicator.getBoundingClientRect();
            startX = e.clientX || (e.touches && e.touches[0].clientX);
            startY = e.clientY || (e.touches && e.touches[0].clientY);
            startLeft = rect.left;
            startTop = rect.top;
            
            e.preventDefault();
        }

        function onMouseMove(e) {
            if (!isDragging) return;
            
            const clientX = e.clientX || (e.touches && e.touches[0].clientX);
            const clientY = e.clientY || (e.touches && e.touches[0].clientY);
            
            const deltaX = clientX - startX;
            const deltaY = clientY - startY;
            
            let newLeft = startLeft + deltaX;
            let newTop = startTop + deltaY;
            
            // Keep within viewport bounds
            const rect = indicator.getBoundingClientRect();
            const maxLeft = window.innerWidth - rect.width;
            const maxTop = window.innerHeight - rect.height;
            
            newLeft = Math.max(0, Math.min(newLeft, maxLeft));
            newTop = Math.max(0, Math.min(newTop, maxTop));
            
            indicator.style.left = newLeft + 'px';
            indicator.style.top = newTop + 'px';
            indicator.style.right = 'auto';
        }

        function onMouseUp() {
            if (!isDragging) return;
            isDragging = false;
            indicator.classList.remove('dragging');
            
            // Save position
            const rect = indicator.getBoundingClientRect();
            const position = {
                top: parseInt(indicator.style.top),
                left: parseInt(indicator.style.left)
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(position));
        }

        // Mouse events
        header.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        // Touch events for mobile
        header.addEventListener('touchstart', onMouseDown, { passive: false });
        document.addEventListener('touchmove', onMouseMove, { passive: false });
        document.addEventListener('touchend', onMouseUp);
    }

    // Setup draggable columns for the screener table
    function setupDraggableColumns() {
        const table = document.getElementById("screener-main-table");
        if (!table) return;

        const thead = table.querySelector("thead tr");
        if (!thead) return;

        const STORAGE_KEY = 'screener_column_order';
        let draggedColumn = null;
        let draggedIndex = -1;

        // Load saved column order
        function loadColumnOrder() {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved) return;

            try {
                const order = JSON.parse(saved);
                reorderColumns(order);
            } catch (e) {
                console.warn('Failed to load column order:', e);
            }
        }

        // Save current column order
        function saveColumnOrder() {
            const headers = thead.querySelectorAll('th[data-column]');
            const order = Array.from(headers).map(th => th.getAttribute('data-column'));
            localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
        }

        // Reorder columns based on saved order
        function reorderColumns(order) {
            const tbody = document.getElementById('screener-table-body');
            
            // Get all current columns
            const headers = Array.from(thead.querySelectorAll('th'));
            const headerMap = {};
            headers.forEach(th => {
                const col = th.getAttribute('data-column');
                if (col) headerMap[col] = th;
            });

            // Reorder headers
            order.forEach(col => {
                if (headerMap[col]) {
                    thead.appendChild(headerMap[col]);
                }
            });

            // Append remaining headers not in order
            headers.forEach(th => {
                const col = th.getAttribute('data-column');
                if (col && !order.includes(col)) {
                    thead.appendChild(th);
                }
            });

            // Reorder body cells for each row
            if (tbody) {
                const rows = tbody.querySelectorAll('tr');
                rows.forEach(row => {
                    reorderRowCells(row, order);
                });
            }
        }

        // Reorder cells in a single row
        function reorderRowCells(row, order) {
            const cells = Array.from(row.querySelectorAll('td'));
            const cellMap = {};
            cells.forEach(td => {
                const col = td.getAttribute('data-column');
                if (col) cellMap[col] = td;
            });

            order.forEach(col => {
                if (cellMap[col]) {
                    row.appendChild(cellMap[col]);
                }
            });

            // Append remaining cells
            cells.forEach(td => {
                const col = td.getAttribute('data-column');
                if (col && !order.includes(col)) {
                    row.appendChild(td);
                }
            });
        }

        // Get column index
        function getColumnIndex(th) {
            const headers = Array.from(thead.querySelectorAll('th'));
            return headers.indexOf(th);
        }

        // Setup drag handlers for headers
        function setupDragHandlers() {
            const headers = thead.querySelectorAll('th[data-column]');
            
            headers.forEach(th => {
                th.setAttribute('draggable', 'true');
                th.style.cursor = 'grab';

                th.addEventListener('dragstart', (e) => {
                    draggedColumn = th;
                    draggedIndex = getColumnIndex(th);
                    th.classList.add('column-dragging');
                    th.style.opacity = '0.5';
                    
                    // Required for Firefox
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', th.getAttribute('data-column'));
                });

                th.addEventListener('dragend', () => {
                    if (draggedColumn) {
                        draggedColumn.classList.remove('column-dragging');
                        draggedColumn.style.opacity = '1';
                    }
                    draggedColumn = null;
                    draggedIndex = -1;
                    
                    // Remove all drag-over effects
                    headers.forEach(h => h.classList.remove('column-drag-over'));
                });

                th.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    
                    if (draggedColumn && draggedColumn !== th) {
                        th.classList.add('column-drag-over');
                    }
                });

                th.addEventListener('dragleave', () => {
                    th.classList.remove('column-drag-over');
                });

                th.addEventListener('drop', (e) => {
                    e.preventDefault();
                    th.classList.remove('column-drag-over');
                    
                    if (!draggedColumn || draggedColumn === th) return;

                    const targetIndex = getColumnIndex(th);
                    const tbody = document.getElementById('screener-table-body');

                    // Move header
                    if (targetIndex < draggedIndex) {
                        thead.insertBefore(draggedColumn, th);
                    } else {
                        thead.insertBefore(draggedColumn, th.nextSibling);
                    }

                    // Move body cells
                    if (tbody) {
                        const rows = tbody.querySelectorAll('tr');
                        rows.forEach(row => {
                            const cells = Array.from(row.querySelectorAll('td'));
                            const draggedCell = cells[draggedIndex];
                            const targetCell = cells[targetIndex];
                            
                            if (draggedCell && targetCell) {
                                if (targetIndex < draggedIndex) {
                                    row.insertBefore(draggedCell, targetCell);
                                } else {
                                    row.insertBefore(draggedCell, targetCell.nextSibling);
                                }
                            }
                        });
                    }

                    // Save new order
                    saveColumnOrder();
                });
            });
        }

        // Initialize
        loadColumnOrder();
        setupDragHandlers();

        // Re-setup handlers when table is updated (MutationObserver)
        const tableObserver = new MutationObserver((mutations) => {
            // Check if new rows were added
            mutations.forEach(mutation => {
                if (mutation.type === 'childList' && mutation.target.id === 'screener-table-body') {
                    // Reorder new rows to match column order
                    const saved = localStorage.getItem(STORAGE_KEY);
                    if (saved) {
                        try {
                            const order = JSON.parse(saved);
                            mutation.addedNodes.forEach(node => {
                                if (node.nodeType === 1 && node.tagName === 'TR') {
                                    reorderRowCells(node, order);
                                }
                            });
                        } catch (e) {
                            // Ignore
                        }
                    }
                }
            });
        });

        const tbody = document.getElementById('screener-table-body');
        if (tbody) {
            tableObserver.observe(tbody, { childList: true });
        }
    }

    // Add sorting functionality to table headers (works on all devices including touch)
    function setupTableSorting() {
        const table = document.getElementById("screener-main-table");
        if (!table) return;

        const headers = table.querySelectorAll("thead th[data-column]");
        headers.forEach((th) => {
            const col = th.getAttribute("data-column");
            if (!col) return;
            
            // Make all columns with data-column attribute sortable
            th.style.cursor = "pointer";
            th.classList.add("sortable");
            
            // Support both click and touch events for mobile devices
            const handleSort = (e) => {
                e.preventDefault();
                e.stopPropagation();
                sortTable(col);
            };
            
            th.addEventListener("click", handleSort);
            th.addEventListener("touchend", handleSort); // For touch devices
        });
    }

    // Локальная сортировка таблицы без перезагрузки страницы
    let currentSortColumn = 'ts'; // По умолчанию сортируем по времени обновления
    let currentSortOrder = 'desc'; // 'asc' или 'desc' - новые обновления сверху
    
    function sortTable(column) {
        const tbody = screenerTableBody;
        if (!tbody) return;
        
        // Переключаем порядок сортировки если кликнули на ту же колонку
        if (currentSortColumn === column) {
            currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            currentSortColumn = column;
            currentSortOrder = 'desc';
        }
        
        applySortToTable();
    }
    
    /**
     * Применяет текущую сортировку к таблице
     * Избранные символы всегда остаются вверху
     */
    function applySortToTable() {
        const tbody = screenerTableBody;
        if (!tbody) return;
        
        const favorites = getFavorites();
        const favoritesSet = new Set(favorites);
        
        // Получаем все строки (исключаем пустые строки)
        const rows = Array.from(tbody.querySelectorAll('tr')).filter(tr => {
            return !tr.classList.contains('empty-row') && tr.querySelector('td[data-column]');
        });
        
        if (rows.length === 0) return;
        
        // Разделяем на избранные и обычные
        const favoriteRows = [];
        const otherRows = [];
        
        rows.forEach(tr => {
            // Надежно получаем символ: сначала из data-symbol зірочки, потом из <a>
            const starEl = tr.querySelector('.favorite-star[data-symbol]');
            const linkEl = tr.querySelector('td[data-column="symbol"] a');
            const symbol = starEl ? starEl.dataset.symbol : (linkEl ? linkEl.textContent.trim() : '');
            
            if (symbol && favoritesSet.has(symbol)) {
                favoriteRows.push(tr);
            } else {
                otherRows.push(tr);
            }
        });
        
        // Функция сравнения для сортировки
        const compareRows = (a, b) => {
            const aCell = a.querySelector(`td[data-column="${currentSortColumn}"]`);
            const bCell = b.querySelector(`td[data-column="${currentSortColumn}"]`);
            
            if (!aCell || !bCell) return 0;
            
            const aText = aCell.textContent.trim();
            const bText = bCell.textContent.trim();
            
            // Для колонки symbol - сортируем как строку
            if (currentSortColumn === 'symbol') {
                return currentSortOrder === 'asc' 
                    ? aText.localeCompare(bText, undefined, { numeric: true, sensitivity: 'base' })
                    : bText.localeCompare(aText, undefined, { numeric: true, sensitivity: 'base' });
            }
            
            // Для колонки ts (timestamp) - сортируем как дату
            if (currentSortColumn === 'ts') {
                const aDate = new Date(aText);
                const bDate = new Date(bText);
                if (isNaN(aDate.getTime()) || isNaN(bDate.getTime())) {
                    return currentSortOrder === 'asc' 
                        ? aText.localeCompare(bText)
                        : bText.localeCompare(aText);
                }
                return currentSortOrder === 'asc' 
                    ? aDate.getTime() - bDate.getTime()
                    : bDate.getTime() - aDate.getTime();
            }
            
            // Парсим числовые значения (учитываем форматирование с $, K, M, B, %)
            const aNum = parseFormattedValueForSort(aText);
            const bNum = parseFormattedValueForSort(bText);
            
            // Если оба значения числовые - сортируем как числа
            if (!isNaN(aNum) && !isNaN(bNum) && aNum !== 0 && bNum !== 0) {
                return currentSortOrder === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // Если одно из значений числовое, а другое нет - числовое идет первым
            if (!isNaN(aNum) && isNaN(bNum)) return currentSortOrder === 'asc' ? -1 : 1;
            if (isNaN(aNum) && !isNaN(bNum)) return currentSortOrder === 'asc' ? 1 : -1;
            
            // Иначе сортируем как строки
            return currentSortOrder === 'asc' 
                ? aText.localeCompare(bText, undefined, { numeric: true, sensitivity: 'base' })
                : bText.localeCompare(aText, undefined, { numeric: true, sensitivity: 'base' });
        };
        
        // НЕ сортуємо избранные - вони залишаються в порядку додавання з localStorage
        // Сортуємо избранные по порядку в localStorage (порядок добавления)
        favoriteRows.sort((a, b) => {
            const starElA = a.querySelector('.favorite-star[data-symbol]');
            const linkElA = a.querySelector('td[data-column="symbol"] a');
            const symbolA = starElA ? starElA.dataset.symbol : (linkElA ? linkElA.textContent.trim() : '');
            
            const starElB = b.querySelector('.favorite-star[data-symbol]');
            const linkElB = b.querySelector('td[data-column="symbol"] a');
            const symbolB = starElB ? starElB.dataset.symbol : (linkElB ? linkElB.textContent.trim() : '');
            
            const indexA = favorites.indexOf(symbolA);
            const indexB = favorites.indexOf(symbolB);
            return indexA - indexB;
        });
        
        // Сортируем остальные по текущей колонке
        otherRows.sort(compareRows);
        
        // Собираем: сначала избранные, потом остальные
        const sortedRows = [...favoriteRows, ...otherRows];
        
        // Используем DocumentFragment для более быстрой вставки
        const fragment = document.createDocumentFragment();
        sortedRows.forEach(row => fragment.appendChild(row));
        
        // Удаляем все строки из tbody и добавляем отсортированные
        tbody.innerHTML = '';
        tbody.appendChild(fragment);
        
        // Обновляем визуальные индикаторы сортировки
        updateSortIndicators(currentSortColumn, currentSortOrder);
        
        // Обновляем rowCache после сортировки
        rowCache.clear();
        sortedRows.forEach((tr) => {
            // Надежно получаем символ: из data-symbol зірочки или из <a>
            const starEl = tr.querySelector('.favorite-star[data-symbol]');
            const linkEl = tr.querySelector('td[data-column="symbol"] a');
            const symbol = starEl ? starEl.dataset.symbol : (linkEl ? linkEl.textContent.trim() : '');
            if (!symbol) return;
            
            const cells = new Map();
            tr.querySelectorAll('td[data-column]').forEach(cell => {
                const col = cell.getAttribute('data-column');
                if (col) cells.set(col, cell);
            });
            rowCache.set(symbol, { row: tr, cells: cells });
        });
    }
    
    function parseFormattedValueForSort(text) {
        if (!text) return 0;
        text = text.trim().replace('%', '').replace('$', '').replace(/,/g, '').replace(/\s+/g, '');
        
        // Handle negative numbers
        const isNegative = text.startsWith('-');
        if (isNegative) {
            text = text.substring(1);
        }
        
        let multiplier = 1;
        if (text.endsWith('K')) {
            multiplier = 1000;
            text = text.replace('K', '');
        } else if (text.endsWith('M')) {
            multiplier = 1000000;
            text = text.replace('M', '');
        } else if (text.endsWith('B')) {
            multiplier = 1000000000;
            text = text.replace('B', '');
        }
        
        const parsed = parseFloat(text);
        if (isNaN(parsed)) return 0;
        
        return (isNegative ? -1 : 1) * parsed * multiplier;
    }
    
    function updateSortIndicators(column, order) {
        // Убираем все индикаторы
        document.querySelectorAll('th[data-column]').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Добавляем индикатор на текущую колонку
        const th = document.querySelector(`th[data-column="${column}"]`);
        if (th) {
            th.classList.add(order === 'asc' ? 'sort-asc' : 'sort-desc');
        }
    }

    function buildQueryFromCurrentLocation() {
        const url = new URL(window.location);
        // Remove duplicate market_type params first
        const marketType = url.searchParams.get("market_type") || "spot";
        url.searchParams.delete("market_type");
        url.searchParams.set("market_type", marketType);
        // Preserve language from URL path (e.g., /ru/, /en/, etc.)
        const pathParts = url.pathname.split('/').filter(p => p);
        if (pathParts.length > 0 && ['ru', 'en', 'es', 'he'].includes(pathParts[0])) {
            // Language is in path, it will be preserved automatically
        }
        // Also preserve language from query params if present
        const langFromPath = pathParts[0];
        if (langFromPath && ['ru', 'en', 'es', 'he'].includes(langFromPath)) {
            // Language is in path, no need to add to query
        }
        return url.search || "?";
    }

    function formatPrice(v) {
        if (v === null || v === undefined) return "";
        const value = Number(v);
        if (isNaN(value)) return String(v);
        // Округляем до целого и добавляем $
        const rounded = Math.round(value);
        return rounded.toLocaleString('en-US') + "$";
    }

    // Форматирование с компактными суффиксами (K, M, B)
    function formatCompact(v, suffix = "$") {
        if (v === null || v === undefined || v === "") return "0" + suffix;
        const value = Number(v);
        if (isNaN(value) || value === 0) return "0" + suffix;
        
        const isNegative = value < 0;
        const absValue = Math.abs(value);
        let formatted;
        
        if (absValue >= 1_000_000_000) {
            formatted = (absValue / 1_000_000_000).toFixed(2) + "B";
        } else if (absValue >= 1_000_000) {
            formatted = (absValue / 1_000_000).toFixed(2) + "M";
        } else if (absValue >= 1_000) {
            formatted = (absValue / 1_000).toFixed(2) + "K";
        } else {
            formatted = absValue.toFixed(2);
        }
        
        return (isNegative ? "-" : "") + formatted + suffix;
    }

    // Простое форматирование: убираем десятичные знаки, добавляем $
    function formatRawDollar(v) {
        if (v === null || v === undefined || v === "") return "0$";
        const value = Number(v);
        if (isNaN(value) || value === 0) return "0$";
        // Округляем до целого числа
        const rounded = Math.round(value);
        // Форматируем с запятыми для тысяч
        const str = rounded.toLocaleString('en-US');
        return str + "$";
    }

    // Форматирование сырых значений с десятичными знаками (без округления)
    function formatRawDollarPrecise(v) {
        if (v === null || v === undefined || v === "") return "0$";
        const value = Number(v);
        if (isNaN(value) || value === 0) return "0$";
        
        // Если включены компактные числа - используем суффиксы
        if (compactNumbers) {
            return formatCompact(value, "$");
        }
        
        // Сохраняем сырое значение с десятичными знаками
        // Используем toFixed для контроля точности, но не округляем жестко
        // Определяем количество знаков после запятой на основе величины числа
        let precision = 2; // По умолчанию 2 знака
        const absValue = Math.abs(value);
        
        if (absValue >= 1000000) {
            precision = 0; // Для миллионов - без десятичных
        } else if (absValue >= 1000) {
            precision = 1; // Для тысяч - 1 знак
        } else {
            precision = 2; // Для меньших значений - 2 знака
        }
        
        // Форматируем с сохранением точности
        const formatted = value.toLocaleString('en-US', {
            minimumFractionDigits: precision,
            maximumFractionDigits: precision
        });
        
        return formatted + "$";
    }

    function formatTicks(v) {
        // Ticks - количество сделок
        if (v === null || v === undefined || v === "") return "0";
        const value = Number(v);
        if (isNaN(value)) return "0";
        
        // Если включены компактные числа - используем суффиксы
        if (compactNumbers) {
            return formatCompact(Math.round(value), "");
        }
        
        return Math.round(value).toLocaleString('en-US');
    }

    function formatVolume(v, marketType) {
        // Используем сырые значения с десятичными знаками
        return formatRawDollarPrecise(v);
    }

    function formatVdelta(v, marketType) {
        // Используем сырые значения с десятичными знаками (без жесткого округления)
        return formatRawDollarPrecise(v);
        // Handle negative numbers properly (put minus before number, $ at the end)
        const isNegative = value < 0;
        const absValue = Math.abs(value);
        // Convert to string to preserve precision, then add commas
        let str = absValue.toString();
        // Add commas for thousands
        const parts = str.split('.');
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        str = parts.join('.');
        // Remove trailing zeros after decimal point
        if (str.includes('.')) {
            str = str.replace(/\.?0+$/, '');
        }
        return (isNegative ? "-" : "") + str + "$";
    }

    function formatChange(v) {
        // Change - это процент изменения цены (например, 1.5 = 1.5%)
        if (v === null || v === undefined || v === "") return "0%";
        const value = Number(v);
        if (isNaN(value)) return "0%";
        return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
    }

    function formatOIChange(v) {
        // OI Change - это процент изменения OI
        if (v === null || v === undefined || v === "") return "0%";
        const value = Number(v);
        if (isNaN(value)) return "0%";
        return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
    }

    function formatVolatility(v) {
        // Volatility - это процент (high - low) / open * 100
        if (v === null || v === undefined || v === "") return "0%";
        const value = Number(v);
        if (isNaN(value) || value === 0) return "0%";
        return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
    }

    /**
     * Форматирует timestamp с миллисекундами
     * @param {string} tsString - строка timestamp в ISO формате
     * @returns {string} - отформатированная строка времени (HH:MM:SS.mmm)
     */
    function formatTimestamp(tsString) {
        if (!tsString || tsString === "") return "";
        try {
            const tsDate = new Date(tsString);
            if (isNaN(tsDate.getTime())) return tsString;
            
            // Формат: HH:MM:SS.mmm (время с миллисекундами)
            const hours = String(tsDate.getHours()).padStart(2, '0');
            const minutes = String(tsDate.getMinutes()).padStart(2, '0');
            const seconds = String(tsDate.getSeconds()).padStart(2, '0');
            const milliseconds = String(tsDate.getMilliseconds()).padStart(3, '0');
            return `${hours}:${minutes}:${seconds}.${milliseconds}`;
        } catch (e) {
            console.warn('Failed to format timestamp:', tsString, e);
            return tsString;
        }
    }

    /**
     * WebSocket connection and message handling
     */
    function getWebSocketUrl() {
        // Get market_type from URL
        const url = new URL(window.location);
        const marketType = url.searchParams.get('market_type') || 'spot';
        
        // Build WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsPath = `/ws/screener/?market_type=${marketType}`;
        
        return `${protocol}//${host}${wsPath}`;
    }

    /**
     * НЕ ИСПОЛЬЗУЕТСЯ: Binance WebSocket теперь подключается на сервере
     * Сервер получает данные напрямую из Binance и передает через Django WebSocket
     * Все данные идут через Django WebSocket, не нужно подключаться к Binance напрямую
     */
    
    // Хранилище ликвидаций (если нужно будет добавить обработку ликвидаций на сервере)
    let liquidations = [];
    const MAX_LIQUIDATIONS = 50; // Храним последние 50 ликвидаций (экономия памяти)
    
    // Настройки ликвидаций (загружаются из localStorage)
    const LIQUIDATION_SETTINGS_KEY = 'screener_liquidation_settings';
    const DEFAULT_LIQUIDATION_SETTINGS = {
        alertsEnabled: true,
        minNotional: 100000, // Минимум 100k USD по умолчанию
        notificationPosition: 'top-right',
        notificationSound: true,
        notificationDuration: 5
    };
    
    // Загружаем настройки ликвидаций
    function loadLiquidationSettings() {
        try {
            const raw = localStorage.getItem(LIQUIDATION_SETTINGS_KEY);
            if (!raw) return DEFAULT_LIQUIDATION_SETTINGS;
            const parsed = JSON.parse(raw);
            // Обеспечиваем обратную совместимость с новыми полями
            return {
                alertsEnabled: parsed.alertsEnabled !== undefined ? parsed.alertsEnabled : DEFAULT_LIQUIDATION_SETTINGS.alertsEnabled,
                minNotional: parsed.minNotional || DEFAULT_LIQUIDATION_SETTINGS.minNotional,
                notificationPosition: parsed.notificationPosition || DEFAULT_LIQUIDATION_SETTINGS.notificationPosition,
                notificationSound: parsed.notificationSound !== undefined ? parsed.notificationSound : DEFAULT_LIQUIDATION_SETTINGS.notificationSound,
                notificationDuration: parsed.notificationDuration || DEFAULT_LIQUIDATION_SETTINGS.notificationDuration
            };
        } catch (e) {
            return DEFAULT_LIQUIDATION_SETTINGS;
        }
    }
    
    // Сохраняем настройки ликвидаций
    function saveLiquidationSettings(settings) {
        try {
            localStorage.setItem(LIQUIDATION_SETTINGS_KEY, JSON.stringify(settings));
        } catch (e) {
            console.error('Error saving liquidation settings:', e);
        }
    }
    
    // Получаем текущие настройки ликвидаций
    function getLiquidationSettings() {
        return loadLiquidationSettings();
    }

    // Применяем визуальные настройки ликвидаций без перезагрузки
    function applyLiquidationSettings(settings) {
        try {
            const container = document.getElementById('liquidation-alerts-container');
            if (container) {
                // Сбрасываем все позиционные классы
                container.classList.remove(
                    'pos-top-right', 'pos-top-left', 'pos-top-center',
                    'pos-bottom-right', 'pos-bottom-left', 'pos-bottom-center'
                );
                
                const pos = settings.notificationPosition || DEFAULT_LIQUIDATION_SETTINGS.notificationPosition;
                switch (pos) {
                    case 'top-left':
                        container.classList.add('pos-top-left');
                        break;
                    case 'top-center':
                        container.classList.add('pos-top-center');
                        break;
                    case 'bottom-right':
                        container.classList.add('pos-bottom-right');
                        break;
                    case 'bottom-left':
                        container.classList.add('pos-bottom-left');
                        break;
                    case 'bottom-center':
                        container.classList.add('pos-bottom-center');
                        break;
                    default:
                        container.classList.add('pos-top-right');
                }
            }
        } catch (e) {
            console.warn('Liquidation: failed to apply settings', e);
        }
    }

    
    function handleLiquidationFromServer(data) {
        // Обрабатываем данные ликвидации, полученные от сервера через Django WebSocket
        // Формат данных от сервера:
        // { symbol, side, price, quantity, notional, orderId, eventTime, tradeTime }
        
        if (!data || !data.symbol) {
            console.warn('[Liquidation] Invalid liquidation data:', data);
            return;
        }
        
        try {
            // Загружаем текущие настройки
            const settings = getLiquidationSettings();
            
            const liquidation = {
                time: new Date(data.eventTime || data.tradeTime || Date.now()),
                symbol: data.symbol,
                side: data.side || 'Long', // Long или Short
                price: parseFloat(data.price || 0),
                quantity: parseFloat(data.quantity || 0),
                notional: parseFloat(data.notional || 0),
                orderId: data.orderId || `${data.symbol}_${data.eventTime || Date.now()}`
            };
            
            // Применяем минимальный порог из настроек
            if (liquidation.notional < settings.minNotional) {
                return; // Пропускаем ликвидации ниже порога
            }
            
            // Проверяем дубликаты по orderId
            const isDuplicate = liquidations.some(liq => liq.orderId === liquidation.orderId);
            if (isDuplicate) {
                return; // Пропускаем дубликаты
            }
            
            // Добавляем в начало массива
            liquidations.unshift(liquidation);
            
            // Ограничиваем размер
            if (liquidations.length > MAX_LIQUIDATIONS) {
                liquidations.pop();
            }
            
            // Обновляем таблицу
            updateLiquidationTable();
            
        // Показываем контейнер если скрыт
        const container = document.getElementById('liquidation-container');
        if (container) {
            container.style.display = 'block';
        }
        // Применяем актуальные настройки (позиция/звук/длительность) сразу, без перезагрузки
        applyLiquidationSettings(settings);
        
        // Показываем красивое уведомление только если алерты включены
        if (settings.alertsEnabled) {
            showLiquidationAlert(liquidation);
        }
        } catch (e) {
            console.error('WebSocket: Error processing liquidation from server', e, data);
        }
    }
    
    // Хранилище текущих данных по символам (для обновления отдельных строк)
    let symbolDataCache = new Map();
    
    // Функция инициализации кеша строк (вызывается после загрузки страницы и после рендера)
    function initializeRowCache() {
        rowCache.clear();
        if (!screenerTableBody) return;
        
        const rows = screenerTableBody.querySelectorAll('tr');
        rows.forEach(rowEl => {
            const symbolCell = rowEl.querySelector('td[data-column="symbol"]');
            if (symbolCell) {
                const link = symbolCell.querySelector('a');
                if (link && link.textContent) {
                    const symbol = link.textContent;
                    const cells = new Map();
                    rowEl.querySelectorAll('td[data-column]').forEach(cell => {
                        const col = cell.getAttribute('data-column');
                        if (col) {
                            cells.set(col, cell);
                        }
                    });
                    rowCache.set(symbol, { row: rowEl, cells: cells });
                }
            }
        });
    }
    
    function updateSingleRow(row) {
        if (!row || !row.symbol) return;
        
        const symbol = row.symbol;
        
        // Используем кеш для быстрого поиска строки
        let rowData = rowCache.get(symbol);
        
        if (!rowData) {
            // Если нет в кеше, ищем и кешируем
            const rows = screenerTableBody.querySelectorAll('tr');
            for (let rowEl of rows) {
                const symbolCell = rowEl.querySelector('td[data-column="symbol"]');
                if (symbolCell) {
                    const link = symbolCell.querySelector('a');
                    if (link && link.textContent === symbol) {
                        // Кешируем строку и все ячейки
                        const cells = new Map();
                        rowEl.querySelectorAll('td[data-column]').forEach(cell => {
                            const col = cell.getAttribute('data-column');
                            if (col) {
                                cells.set(col, cell);
                            }
                        });
                        rowData = { row: rowEl, cells: cells };
                        rowCache.set(symbol, rowData);
                        break;
                    }
                }
            }
        }
        
        if (!rowData || !rowData.row) {
            // Символ еще не в таблице - НЕ обновляем его
            // Это нормально когда воркеры отправляют больше символов чем в таблице
            return;
        }
        
        const prev = previousValues.get(symbol) || {};
        const marketType = new URLSearchParams(window.location.search).get("market_type") || "spot";
        const rowMarketType = row.market_type || marketType;
        
        // Оптимизированная функция обновления ячейки (минимальные DOM операции)
        const updateCell = (column, value, formatted, className) => {
            const cell = rowData.cells.get(column);
            if (!cell) return;
            
            let valueChanged = false;
            
            // Обновляем только если значение изменилось (оптимизация)
            if (formatted !== undefined) {
                const currentText = cell.textContent;
                if (currentText !== formatted) {
                    cell.textContent = formatted;
                    valueChanged = true;
                }
            }
            if (className !== undefined) {
                const currentClass = cell.className || '';
                if (currentClass !== className) {
                    cell.className = className || '';
                }
            }
            
            // Убрано мигание обновленных значений
        };
        
        // Price - используем только серверные данные (без fallback форматирования)
        const priceValue = Number(row.price ?? 0);
        const priceFormatted = row.price_formatted || String(priceValue) + "$"; // Minimal fallback
        const priceCls = getComparisonClass(priceValue, prev.price, `${symbol}_price`);
        updateCell('price', priceValue, priceFormatted, priceCls);
        
        // Change columns - процент изменения цены (close - open) / open * 100
        // Используем только серверные данные для минимальной нагрузки на браузер
        const changeCols = ["change_1m", "change_3m", "change_5m", "change_15m", "change_30m", "change_1h", "change_4h", "change_8h", "change_1d"];
        changeCols.forEach(col => {
            const numValue = Number(row[col] ?? 0);
            const formatted = row[col + "_formatted"] || numValue.toFixed(2) + "%"; // Minimal fallback
            const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
            updateCell(col, numValue, formatted, cls);
        });
        
        // OI Change columns - процент изменения OI
        // Используем только серверные данные для минимальной нагрузки на браузер
        const oiChangeCols = ["oi_change_1m", "oi_change_3m", "oi_change_5m", "oi_change_15m", "oi_change_30m", "oi_change_1h", "oi_change_4h", "oi_change_8h", "oi_change_1d"];
        oiChangeCols.forEach(col => {
            const numValue = Number(row[col] ?? 0);
            const formatted = row[col + "_formatted"] || numValue.toFixed(2) + "%"; // Minimal fallback
            const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
            updateCell(col, numValue, formatted, cls);
        });
        
        // Volatility columns - процент (high - low) / open * 100
        // Используем только серверные данные для минимальной нагрузки на браузер
        const volCols = ["volatility_1m", "volatility_3m", "volatility_5m", "volatility_15m", "volatility_30m", "volatility_1h", "volatility_4h", "volatility_8h", "volatility_1d"];
        volCols.forEach(col => {
            const numValue = Number(row[col] ?? 0);
            const formatted = row[col + "_formatted"] || numValue.toFixed(2) + "%"; // Minimal fallback
            const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
            updateCell(col, numValue, formatted, cls);
        });
        
        // Ticks columns
        // Всегда форматируем локально для учета настройки compactNumbers
        const ticksCols = ["ticks_1m", "ticks_3m", "ticks_5m", "ticks_15m", "ticks_30m", "ticks_1h", "ticks_4h", "ticks_8h", "ticks_1d"];
        ticksCols.forEach(col => {
            const numValue = Number(row[col] ?? 0);
            const formatted = formatTicks(numValue);
            const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
            updateCell(col, numValue, formatted, cls);
        });
        
        // Vdelta columns
        // Всегда форматируем локально для учета настройки compactNumbers
        const vdeltaCols = ["vdelta_1m", "vdelta_3m", "vdelta_5m", "vdelta_15m", "vdelta_30m", "vdelta_1h", "vdelta_4h", "vdelta_8h", "vdelta_1d"];
        vdeltaCols.forEach(col => {
            const numValue = Number(row[col] ?? 0);
            const formatted = formatRawDollarPrecise(numValue);
            const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
            updateCell(col, numValue, formatted, cls);
        });
        
        // Volume columns
        // Всегда форматируем локально для учета настройки compactNumbers
        const volumeCols = ["volume_1m", "volume_3m", "volume_5m", "volume_15m", "volume_30m", "volume_1h", "volume_4h", "volume_8h", "volume_1d"];
        volumeCols.forEach(col => {
            const numValue = Number(row[col] ?? 0);
            const formatted = formatRawDollarPrecise(numValue);
            const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
            updateCell(col, numValue, formatted, cls);
        });
        
        // Funding Rate - процент (например, 0.0001 = 0.01%)
        const funding = Number(row.funding_rate ?? 0);
        // Funding rate от Binance приходит как десятичная дробь (0.0001 = 0.01%)
        // Умножаем на 100 для отображения в процентах
        const fundingPercent = funding * 100;
        const fundingFormatted = row.funding_rate_formatted || fundingPercent.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }) + "%";
        const fundClass = getComparisonClass(funding, prev.funding_rate, `${symbol}_funding_rate`);
        updateCell('funding_rate', funding, fundingFormatted, fundClass);
        
        // Open Interest - сырые данные в долларах (без округления)
        // Всегда форматируем локально для учета настройки compactNumbers
        const oiValue = Number(row.open_interest ?? 0);
        const oiFormatted = formatRawDollarPrecise(oiValue);
        const oiCls = getComparisonClass(oiValue, prev.open_interest, `${symbol}_open_interest`);
        updateCell('open_interest', oiValue, oiFormatted, oiCls);
        
        // Timestamp - используем только серверные данные для минимальной нагрузки на браузер
        const rowTs = row.ts || row.timestamp || new Date().toISOString();
        const prevTs = prev.ts || prev.timestamp || undefined;
        const tsStateKey = `${symbol}_ts`;
        const tsClass = getTimestampClass(rowTs, prevTs, tsStateKey);
        const tsFormatted = row.timestamp_formatted || new Date(rowTs).toLocaleTimeString('en-US', {hour12: false}); // Minimal fallback
        updateCell('ts', null, tsFormatted, tsClass);
        
        // Сохраняем значения для следующего сравнения
        const storeValue = (val) => {
            const num = Number(val);
            return (!isNaN(num) && num !== null && num !== undefined) ? num : 0;
        };
        
        previousValues.set(symbol, {
            ts: rowTs,
            price: storeValue(row.price),
            change_1m: storeValue(row.change_1m), change_3m: storeValue(row.change_3m), change_5m: storeValue(row.change_5m),
            change_15m: storeValue(row.change_15m), change_30m: storeValue(row.change_30m),
            change_1h: storeValue(row.change_1h), change_4h: storeValue(row.change_4h), change_8h: storeValue(row.change_8h), change_1d: storeValue(row.change_1d),
            oi_change_1m: storeValue(row.oi_change_1m), oi_change_3m: storeValue(row.oi_change_3m), oi_change_5m: storeValue(row.oi_change_5m),
            oi_change_15m: storeValue(row.oi_change_15m), oi_change_30m: storeValue(row.oi_change_30m),
            oi_change_1h: storeValue(row.oi_change_1h), oi_change_4h: storeValue(row.oi_change_4h), oi_change_8h: storeValue(row.oi_change_8h), oi_change_1d: storeValue(row.oi_change_1d),
            volatility_1m: storeValue(row.volatility_1m), volatility_3m: storeValue(row.volatility_3m), volatility_5m: storeValue(row.volatility_5m),
            volatility_15m: storeValue(row.volatility_15m), volatility_30m: storeValue(row.volatility_30m),
            volatility_1h: storeValue(row.volatility_1h), volatility_4h: storeValue(row.volatility_4h), volatility_8h: storeValue(row.volatility_8h), volatility_1d: storeValue(row.volatility_1d),
            ticks_1m: storeValue(row.ticks_1m), ticks_3m: storeValue(row.ticks_3m), ticks_5m: storeValue(row.ticks_5m),
            ticks_15m: storeValue(row.ticks_15m), ticks_30m: storeValue(row.ticks_30m),
            ticks_1h: storeValue(row.ticks_1h), ticks_4h: storeValue(row.ticks_4h), ticks_8h: storeValue(row.ticks_8h), ticks_1d: storeValue(row.ticks_1d),
            vdelta_1m: storeValue(row.vdelta_1m), vdelta_3m: storeValue(row.vdelta_3m), vdelta_5m: storeValue(row.vdelta_5m),
            vdelta_15m: storeValue(row.vdelta_15m), vdelta_30m: storeValue(row.vdelta_30m),
            vdelta_1h: storeValue(row.vdelta_1h), vdelta_4h: storeValue(row.vdelta_4h), vdelta_8h: storeValue(row.vdelta_8h), vdelta_1d: storeValue(row.vdelta_1d),
            volume_1m: storeValue(row.volume_1m), volume_3m: storeValue(row.volume_3m), volume_5m: storeValue(row.volume_5m),
            volume_15m: storeValue(row.volume_15m), volume_30m: storeValue(row.volume_30m),
            volume_1h: storeValue(row.volume_1h), volume_4h: storeValue(row.volume_4h), volume_8h: storeValue(row.volume_8h), volume_1d: storeValue(row.volume_1d),
            funding_rate: storeValue(row.funding_rate),
            open_interest: storeValue(row.open_interest),
        });
    }
    
    function updateLiquidationTable() {
        const tbody = document.getElementById('liquidation-table-body');
        if (!tbody) return;
        
        // Очищаем таблицу
        tbody.innerHTML = '';
        
        // Добавляем ликвидации
        liquidations.forEach(liq => {
            const tr = document.createElement('tr');
            tr.className = liq.side === 'Long' ? 'liquidation-long' : 'liquidation-short';
            
            const timeStr = formatTimestamp(liq.timestamp);
            const notionalStr = formatVolume(liq.notional, 'futures');
            
            tr.innerHTML = `
                <td>${timeStr}</td>
                <td><strong>${liq.symbol}</strong></td>
                <td class="liquidation-side ${liq.side.toLowerCase()}">${liq.side}</td>
                <td>${liq.price.toFixed(2)}</td>
                <td>${liq.quantity.toFixed(4)}</td>
                <td class="liquidation-notional"><strong>${notionalStr}</strong></td>
            `;
            
            tbody.appendChild(tr);
        });
    }
    
    function showLiquidationAlert(liquidation) {
        const settings = getLiquidationSettings();
        const marketType = new URLSearchParams(window.location.search).get("market_type") || "spot";
        
        // Создаем красивое уведомление
        const alert = document.createElement('div');
        alert.className = `liquidation-alert ${liquidation.side.toLowerCase()}`;
        alert.innerHTML = `
            <div class="liquidation-alert-content">
                <div class="liquidation-alert-icon">🔥</div>
                <div class="liquidation-alert-text">
                    <strong>${liquidation.symbol}</strong> ${liquidation.side} Liquidation
                    <br>
                    <span class="liquidation-alert-amount">${formatVolume(liquidation.notional, marketType)}</span>
                </div>
                <button class="liquidation-alert-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Добавляем в контейнер алертов
        let alertContainer = document.getElementById('liquidation-alerts-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'liquidation-alerts-container';
            alertContainer.className = 'liquidation-alerts-container';
            document.body.appendChild(alertContainer);
        }
        
        // Применяем позиционирование/настройки сразу для нового контейнера
        applyLiquidationSettings(settings);
        
        alertContainer.appendChild(alert);
        
        // Автоматически удаляем через 10 секунд
        const durationSec = Math.max(2, Math.min(30, settings.notificationDuration || 10));
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, durationSec * 1000);
    }
    
    // ==================== REST API POLLING (НОВАЯ АРХИТЕКТУРА) ====================
    
    let pollingInterval = null;
    let pollingActive = true;
    
    function startApiPolling() {
        // Останавливаем предыдущий интервал если есть
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
        
        // Получаем market_type из URL или используем по умолчанию 'spot'
        const urlParams = new URLSearchParams(window.location.search);
        const marketType = urlParams.get('market_type') || 'spot';
        
        // Первый запрос сразу
        fetchLatestData(marketType);
        
        // Затем каждые 500ms (2 раза в секунду) - оптимальная скорость
        pollingInterval = setInterval(() => {
            if (pollingActive) {
                fetchLatestData(marketType);
            }
        }, 500);
    }
    
    function stopApiPolling() {
        pollingActive = false;
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }
    
    async function fetchLatestData(marketType) {
        try {
            const response = await fetch(`/api/screener/latest/?market_type=${marketType}`);
            
            if (!response.ok) {
                console.error(`[REST API] Error: ${response.status} ${response.statusText}`);
                return;
            }
            
            const result = await response.json();
            const data = result.data || [];
            const timestamp = result.timestamp;
            

            
            if (data.length > 0) {
                window._lastScreenerData = data;
                
                // Скрываем заставку когда получены первые данные
                if (window._hideSplashScreen && typeof window._hideSplashScreen === 'function') {
                    window._hideSplashScreen();
                    window._hideSplashScreen = null;
                }
                
                // Обновляем график Bitcoin если есть данные BTCUSDT
                const btcData = data.find(row => row.symbol === 'BTCUSDT');
                if (btcData && window._updateBitcoinChart) {
                    const btcPrice = Number(btcData.price);
                    const btcChange = Number(btcData.change_1m || 0);
                    if (!isNaN(btcPrice) && !isNaN(btcChange)) {
                        window._updateBitcoinChart(btcPrice, btcChange);
                    }
                }
                
                // Проверяем, есть ли уже данные в таблице
                const hasServerData = screenerTableBody && 
                    screenerTableBody.querySelectorAll('tr td[data-column="symbol"]').length > 0;
                
                const tableText = screenerTableBody ? screenerTableBody.textContent : '';
                const hasEmptyMessage = tableText.includes('No data to display') || 
                                       tableText.includes('Нет данных для отображения');
                
                // Если таблица пустая - отрисовываем
                if ((!hasServerData || hasEmptyMessage) && data.length > 0) {
                    renderScreenerTable(data);
                    isTableInitialized = true;
                    requestAnimationFrame(() => {
                        initializePreviousValues();
                    });
                } else if (!isTableInitialized && hasServerData && !hasEmptyMessage) {
                    // Таблица уже отрисована сервером, но может содержать не все символы
                    isTableInitialized = true;
                    
                    // Если API вернул больше символов, чем в таблице - перерисовываем полностью
                    const rowsInTable = screenerTableBody.children.length;
                    if (data.length > rowsInTable) {
                        renderScreenerTable(data);
                    } else {
                        // Динамически обновляем существующие строки
                        data.forEach((row) => {
                            updateSingleRow(row);
                        });
                    }
                    
                    requestAnimationFrame(() => {
                        initializePreviousValues();
                    });
                } else {
                    // Динамически обновляем каждую строку (основной режим работы)
                    data.forEach((row) => {
                        updateSingleRow(row);
                    });
                }
            }
        } catch (error) {
            console.error('[REST API] Failed to fetch data:', error);
        }
    }
    
    // Останавливаем polling когда пользователь уходит со страницы
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            pollingActive = false;
        } else {
            pollingActive = true;
        }
    });
    
    // ==================== END REST API POLLING ====================
    
    function connectWebSocket() {
        // Проверяем, не подключены ли уже
        if (ws) {
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                return; // Already connected or connecting
            }
            // Закрываем старое соединение если оно в состоянии CLOSING или CLOSED
            if (ws.readyState === WebSocket.CLOSING || ws.readyState === WebSocket.CLOSED) {
                ws = null; // Сбрасываем для нового подключения
            }
        }
        
        const wsUrl = getWebSocketUrl();
        
        try {
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                reconnectAttempts = 0;
                window._ws_message_count = 0; // Сбрасываем счетчик при переподключении
                
                // Update status indicator
                const statusDot = document.getElementById('ws-status-dot');
                const statusText = document.getElementById('ws-status-text');
                const statsDiv = document.getElementById('ws-stats');
                if (statusDot) statusDot.style.background = '#4CAF50';
                if (statusText) statusText.textContent = '● LIVE';
                if (statsDiv) statsDiv.style.display = 'block';
                
                // Send ping to keep connection alive
                const pingInterval = setInterval(() => {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'ping' }));
                    } else {
                        clearInterval(pingInterval);
                    }
                }, 30000); // Ping every 30 seconds
            };
            
            // Батчинг обновлений для максимальной производительности
            let pendingUpdates = new Map();
            let rafScheduled = false;
            let sortScheduled = false;
            
            function scheduleUpdate(symbol, rowData) {
                pendingUpdates.set(symbol, rowData);
                
                if (!rafScheduled) {
                    rafScheduled = true;
                    requestAnimationFrame(() => {
                        // Батчим все обновления в один кадр для максимальной скорости
                        const updates = Array.from(pendingUpdates.values());
                        pendingUpdates.clear();
                        rafScheduled = false;
                        
                        // Обновляем все строки за один проход (оптимизировано)
                        updates.forEach((row) => {
                            updateSingleRow(row);
                        });
                        
                        // ОПТИМИЗАЦИЯ: Сортировка раз в 1 секунду (вместо 500ms) для плавности при частых обновлениях
                        if (!sortScheduled) {
                            sortScheduled = true;
                            setTimeout(() => {
                                sortScheduled = false;
                                applySortToTable();
                            }, 1000); // Применяем сортировку раз в 1000ms
                        }
                    });
                }
            }
            
            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    
                    if (message.type === 'screener_data') {
                        const data = message.data;
                        const marketType = message.market_type || 'spot';
                        const timestamp = message.timestamp || new Date().toISOString();
                        
                        // Сохраняем данные глобально для использования в updateSingleRow
                        if (data && Array.isArray(data) && data.length > 0) {
                            window._lastScreenerData = data;
                            
                            // Скрываем заставку когда получены первые данные
                            if (window._hideSplashScreen && typeof window._hideSplashScreen === 'function') {
                                window._hideSplashScreen();
                                window._hideSplashScreen = null; // Удаляем после первого вызова
                            }
                        }
                        
                        // Счетчик сообщений для статистики
                        if (!window._ws_message_count) window._ws_message_count = 0;
                        window._ws_message_count++;
                        
                        // Update status indicator
                        const messageCountEl = document.getElementById('ws-message-count');
                        const lastUpdateEl = document.getElementById('ws-last-update');
                        if (messageCountEl) messageCountEl.textContent = window._ws_message_count;
                        if (lastUpdateEl) {
                            const now = new Date();
                            lastUpdateEl.textContent = now.toLocaleTimeString();
                        }
                        
                        const dataLength = data && Array.isArray(data) ? data.length : 0;
                        
                        if (data && Array.isArray(data)) {
                            // Update Bitcoin chart if BTCUSDT data is received
                            const btcData = data.find(row => row.symbol === 'BTCUSDT');
                            if (btcData && window._updateBitcoinChart) {
                                const btcPrice = Number(btcData.price);
                                const btcChange = Number(btcData.change_1m || 0);
                                if (!isNaN(btcPrice) && !isNaN(btcChange)) {
                                    window._updateBitcoinChart(btcPrice, btcChange);
                                }
                            }
                            
                            // СПРОЩЕНА ЛОГІКА: завжди оновлюємо таблицю коли є дані
                            window._lastScreenerData = data;
                            
                            // Перевіряємо чи таблиця вже має дані
                            const hasServerData = screenerTableBody && 
                                screenerTableBody.querySelectorAll('tr td[data-column="symbol"]').length > 0;
                            
                            // КРИТИЧНО: Если это первое сообщение и количество символов в таблице не совпадает
                            // с количеством в данных - перерендерим таблицу (пагинация Django показывает только 50)
                            const currentRowCount = screenerTableBody ? screenerTableBody.querySelectorAll('tr').length : 0;
                            const needsFullRender = !isTableInitialized || 
                                                   (window._ws_message_count === 1 && currentRowCount !== data.length);
                            
                            if ((!hasServerData || needsFullRender) && data.length > 0) {
                                // Таблиця пуста АБО потрібен повний рендер - відрисовуємо повністю
                                renderScreenerTable(data);
                                isTableInitialized = true;
                                requestAnimationFrame(() => {
                                    initializePreviousValues();
                                });
                            } else if (hasServerData && !needsFullRender) {
                                // Таблиця вже є і повна - оновлюємо динамічно
                                isTableInitialized = true;
                                
                                // КРИТИЧНО: ініціалізуємо кеш рядків перед оновленням
                                if (rowCache.size === 0) {
                                    initializeRowCache();
                                }
                                
                                data.forEach((row) => {
                                    scheduleUpdate(row.symbol, row);
                                });
                            } else {
                                // Fallback: если что-то пошло не так, проверяем данные перед отрисовкой
                                if (data && data.length > 0) {
                                    window._lastScreenerData = data;
                                    renderScreenerTable(data);
                                    isTableInitialized = true;
                                    // Инициализируем previousValues после отрисовки таблицы
                                    requestAnimationFrame(() => {
                                        initializePreviousValues();
                                    });
                                }
                            }
                            
                            lastRefreshTime = Date.now();
                        }
                    } else if (message.type === 'liquidation') {
                        // Обрабатываем данные ликвидации от сервера
                        const liquidationData = message.data;
                        if (liquidationData && liquidationData.symbol) {
                            handleLiquidationFromServer(liquidationData);
                        }
                    } else if (message.type === 'pong') {
                        // Pong response, connection is alive
                    }
                } catch (e) {
                    console.error('[Binance Data] ❌ Error parsing message', e, event.data);
                }
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            ws.onclose = (event) => {
                // Update status indicator
                const statusDot = document.getElementById('ws-status-dot');
                const statusText = document.getElementById('ws-status-text');
                if (statusDot) statusDot.style.background = '#FF5722';
                if (statusText) statusText.textContent = '● Disconnected';
                
                // Attempt to reconnect
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    reconnectAttempts++;
                    const delay = RECONNECT_DELAY * reconnectAttempts;
                    
                    if (statusText) statusText.textContent = `● Reconnecting (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`;
                    
                    reconnectTimeoutId = setTimeout(() => {
                        connectWebSocket();
                    }, delay);
                } else {
                    console.error('WebSocket: Max reconnection attempts reached');
                    if (statusText) statusText.textContent = '● Failed';
                }
            };
        } catch (e) {
            console.error('WebSocket: Failed to connect', e);
            // Retry connection
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                reconnectTimeoutId = setTimeout(() => {
                    connectWebSocket();
                }, RECONNECT_DELAY * reconnectAttempts);
            }
        }
    }
    
    function disconnectWebSocket() {
        if (reconnectTimeoutId) {
            clearTimeout(reconnectTimeoutId);
            reconnectTimeoutId = null;
        }
        
        if (ws) {
            ws.close();
            ws = null;
        }
    }

    // ==================== LIQUIDATION WEBSOCKET ====================
    let liquidationWs = null;
    let liquidationReconnectAttempts = 0;
    const MAX_LIQUIDATION_RECONNECT_ATTEMPTS = 5;
    const LIQUIDATION_RECONNECT_DELAY = 3000;
    
    function connectLiquidationWebSocket() {
        if (liquidationWs && (liquidationWs.readyState === WebSocket.OPEN || liquidationWs.readyState === WebSocket.CONNECTING)) {
            return;
        }
        
        // Определяем протокол и хост
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws/liquidations/`;
        
        try {
            liquidationWs = new WebSocket(wsUrl);
            
            liquidationWs.onopen = () => {
                liquidationReconnectAttempts = 0;
                
                // Отправляем фильтры на сервер
                const settings = loadLiquidationSettings();
                const filterMessage = {
                    type: 'set_filters',
                    filters: {
                        min_notional: settings.minNotional || 100000
                    }
                };
                liquidationWs.send(JSON.stringify(filterMessage));
            };
            
            liquidationWs.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    
                    if (message.type === 'filters_updated') {
                        return;
                    }
                    
                    if (message.type === 'liquidation') {
                        const liquidation = message.data;
                        
                        // Добавляем в массив
                        liquidations.unshift(liquidation);
                        
                        // Ограничиваем длину массива до 50 для экономии памяти
                        if (liquidations.length > 50) {
                            liquidations = liquidations.slice(0, 50);
                        }
                        
                        // Обновляем таблицу
                        updateLiquidationTable();
                        
                        // Показываем контейнер
                        const container = document.getElementById('liquidation-container');
                        if (container) {
                            container.style.display = 'block';
                        }
                        
                        // Показываем flash-уведомление
                        const settings = loadLiquidationSettings();
                        if (settings.alertsEnabled) {
                            showLiquidationAlert(liquidation);
                        }
                    }
                } catch (e) {
                    console.error('[Liquidations] Error processing message:', e);
                }
            };
            
            liquidationWs.onerror = (error) => {
                console.error('[Liquidations] WebSocket error:', error);
            };
            
            liquidationWs.onclose = (event) => {
                liquidationWs = null;
                
                // Reconnect
                if (liquidationReconnectAttempts < MAX_LIQUIDATION_RECONNECT_ATTEMPTS) {
                    liquidationReconnectAttempts++;
                    setTimeout(() => {
                        connectLiquidationWebSocket();
                    }, LIQUIDATION_RECONNECT_DELAY * liquidationReconnectAttempts);
                }
            };
        } catch (e) {
            console.error('[Liquidations] Failed to connect:', e);
        }
    }
    // ==================== END LIQUIDATION WEBSOCKET ====================

    /**
     * Определяет CSS класс для цвета на основе сравнения текущего и предыдущего значений
     * Поддерживает подсветку на 5 обновлений
     * @param {number|string} currentValue - текущее значение
     * @param {number|string|null|undefined} previousValue - предыдущее значение
     * @param {string} stateKey - уникальный ключ для хранения состояния (например, "BTCUSDT_price")
     * @returns {string} "value-up" (зеленый), "value-down" (красный) или "" (белый)
     */
    function getComparisonClass(currentValue, previousValue, stateKey) {
        const current = Number(currentValue);
        if (isNaN(current)) {
            if (stateKey) colorStates.delete(stateKey);
            return "";
        }
        
        // Получаем текущее состояние цвета
        const currentState = stateKey ? colorStates.get(stateKey) : null;
        
        // Если нет предыдущего значения
        if (previousValue === null || previousValue === undefined || previousValue === "") {
            // Если есть активное состояние - продолжаем показывать цвет (БЕЗ уменьшения счетчика)
            if (currentState && currentState.updatesLeft > 0) {
                return currentState.class;
            }
            return "";
        }
        
        const previous = Number(previousValue);
        if (isNaN(previous)) {
            if (stateKey) colorStates.delete(stateKey);
            return "";
        }
        
        // Сравниваем значения
        const diff = current - previous;
        let newClass = "";
        if (diff > 0.0001) {
            newClass = "value-up";   // Выросло - зеленый
        } else if (diff < -0.0001) {
            newClass = "value-down"; // Упало - красный
        } else {
            // Значение НЕ изменилось - продолжаем показывать предыдущий цвет
            // Уменьшаем счетчик только когда значение не меняется
            if (currentState && currentState.updatesLeft > 0) {
                currentState.updatesLeft--;
                if (currentState.updatesLeft <= 0) {
                    colorStates.delete(stateKey);
                    return "";
                }
                return currentState.class;
            }
            return "";
        }
        
        // Значение ИЗМЕНИЛОСЬ - сбрасываем счетчик на максимум
        if (stateKey) {
            colorStates.set(stateKey, { class: newClass, updatesLeft: COLOR_PERSIST_UPDATES });
        }
        return newClass;
    }
    
    /**
     * Получает предыдущее значение из объекта previousValues
     * @param {Object} prev - объект с предыдущими значениями
     * @param {string} key - ключ значения
     * @returns {number|undefined} предыдущее значение или undefined
     */
    function getPreviousValue(prev, key) {
        const value = prev[key];
        if (value === undefined || value === null || value === "") return undefined;
        const num = Number(value);
        return isNaN(num) ? undefined : num;
    }

    /**
     * Определяет CSS класс для timestamp на основе времени обновления и изменения
     * Зеленый только при обновлении (timestamp изменился), красный если старое (> 1 минуты)
     * @param {string} tsString - строка timestamp в ISO формате
     * @param {string|undefined} previousTs - предыдущий timestamp для сравнения
     * @param {string} stateKey - уникальный ключ для хранения состояния
     * @returns {string} "ts-fresh" (зеленый при обновлении), "ts-stale" (красный если старое) или "" (белый)
     */
    function getTimestampClass(tsString, previousTs, stateKey) {
        if (!tsString || tsString === "") return "";
        
        try {
            const tsDate = new Date(tsString);
            const now = new Date();
            const diffMs = now - tsDate;
            const diffMinutes = diffMs / (1000 * 60);
            
            // Если обновление старое (> 1 минуты) - всегда красный
            if (diffMinutes > 1) {
                if (stateKey) colorStates.delete(stateKey);
                return "ts-stale"; // Красный - обновление старое
            }
            
            // Если обновление свежее, проверяем изменилось ли оно
            if (previousTs && previousTs !== "" && previousTs !== tsString) {
                // Timestamp изменился - показываем зеленый на COLOR_PERSIST_UPDATES обновлений
                if (stateKey) {
                    colorStates.set(stateKey, { class: "ts-fresh", updatesLeft: COLOR_PERSIST_UPDATES });
                }
                return "ts-fresh"; // Зеленый - произошло обновление
            }
            
            // Timestamp не изменился, но свежее - проверяем нужно ли продолжать показывать зеленый
            const currentState = stateKey ? colorStates.get(stateKey) : null;
            if (currentState && currentState.class === "ts-fresh" && currentState.updatesLeft > 0) {
                // Продолжаем показывать зеленый, уменьшаем счетчик
                currentState.updatesLeft--;
                return "ts-fresh";
            }
            
            // По умолчанию - белый (без подсветки)
            if (stateKey) colorStates.delete(stateKey);
            return "";
        } catch (e) {
            console.warn('Failed to parse timestamp:', tsString, e);
            if (stateKey) colorStates.delete(stateKey);
            return "";
        }
    }

    /**
     * Применяет классы подсветки к ячейкам ts при начальной загрузке страницы
     * При начальной загрузке просто проверяем возраст (красный если > 1 минуты)
     */
    function applyTimestampClasses() {
        const tsCells = document.querySelectorAll('td[data-column="ts"]');
        tsCells.forEach(cell => {
            const tsText = cell.textContent.trim();
            if (tsText) {
                // Сохраняем оригинальный timestamp в data-атрибуте для сравнения
                if (!cell.hasAttribute('data-original-ts')) {
                    cell.setAttribute('data-original-ts', tsText);
                }
                
                // Пытаемся распарсить timestamp в разных форматах
                let tsDate = null;
                try {
                    // Пробуем ISO формат
                    tsDate = new Date(tsText);
                    // Если не получилось, пробуем другие форматы
                    if (isNaN(tsDate.getTime())) {
                        // Пробуем формат Django datetime (например: "Nov. 30, 2025, 4:50 a.m.")
                        tsDate = new Date(tsText);
                    }
                } catch (e) {
                    console.warn('Failed to parse timestamp:', tsText, e);
                }
                
                if (tsDate && !isNaN(tsDate.getTime())) {
                    const now = new Date();
                    const diffMs = now - tsDate;
                    const diffMinutes = diffMs / (1000 * 60);
                    
                    // Форматируем timestamp в короткий формат (HH:MM:SS)
                    const formatted = formatTimestamp(tsText);
                    if (formatted && formatted !== tsText) {
                        cell.textContent = formatted;
                    }
                    
                    // Удаляем старые классы
                    cell.classList.remove('ts-fresh', 'ts-stale');
                    
                    // При начальной загрузке: красный только если старое (> 1 минуты)
                    // Зеленый не показываем при начальной загрузке (только при обновлении)
                    if (diffMinutes > 1) {
                        cell.classList.add('ts-stale');
                    }
                    // Иначе белый (без класса)
                }
            }
        });
    }

    /**
     * Получает список избранных символов из localStorage
     * @returns {string[]} массив символов
     */
    function getFavorites() {
        try {
            const saved = localStorage.getItem(favoritesStorageKey);
            if (saved) {
                const favorites = JSON.parse(saved);
                return Array.isArray(favorites) ? favorites : [];
            }
        } catch (e) {
            console.warn('Failed to load favorites:', e);
        }
        return [];
    }

    /**
     * Сохраняет список избранных символов в localStorage
     * @param {string[]} favorites - массив символов
     */
    function saveFavorites(favorites) {
        try {
            localStorage.setItem(favoritesStorageKey, JSON.stringify(favorites));
        } catch (e) {
            console.warn('Failed to save favorites:', e);
        }
    }

    /**
     * Переключает статус избранного для символа
     * @param {string} symbol - символ для переключения
     */
    function toggleFavorite(symbol) {
        const favorites = getFavorites();
        const index = favorites.indexOf(symbol);
        
        if (index >= 0) {
            // Удаляем из избранного
            favorites.splice(index, 1);
        } else {
            // Добавляем в избранное, но не больше MAX_FAVORITES
            if (favorites.length >= MAX_FAVORITES) {
                alert(`Maximum ${MAX_FAVORITES} favorites allowed. Please remove one first.`);
                return;
            }
            favorites.push(symbol);
        }
        
        saveFavorites(favorites);
        updateFavoriteStars();
        // Применяем сортировку чтобы переместить избранные вверх
        applySortToTable();
    }

    /**
     * Обновляет визуальное состояние звездочек избранного
     */
    function updateFavoriteStars() {
        const favorites = getFavorites();
        document.querySelectorAll('.favorite-star').forEach(star => {
            const symbol = star.dataset.symbol;
            if (favorites.includes(symbol)) {
                star.classList.add('active');
                star.textContent = '★';
            } else {
                star.classList.remove('active');
                star.textContent = '☆';
            }
        });
    }

    /**
     * Настраивает обработчики клика на звездочки в начальной таблице
     */
    function setupFavoriteStars() {
        document.querySelectorAll('.favorite-star').forEach(star => {
            star.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const symbol = star.dataset.symbol;
                if (symbol) {
                    toggleFavorite(symbol);
                }
            });
        });
        updateFavoriteStars();
    }

    /**
     * Сортирует строки: избранные сверху (с текущей сортировкой), остальные по текущей сортировке
     * @param {Array} rows - массив строк данных
     * @returns {Array} отсортированный массив
     */
    function sortRowsWithFavorites(rows) {
        const favorites = getFavorites();
        const favoriteSet = new Set(favorites);
        
        const favoriteRows = [];
        const otherRows = [];
        
        rows.forEach(row => {
            if (favoriteSet.has(row.symbol)) {
                favoriteRows.push(row);
            } else {
                otherRows.push(row);
            }
        });
        
        // Функция сравнения для текущей сортировки
        const getSortValue = (row) => {
            if (!currentSortColumn) return 0;
            
            // Пробуем получить значение напрямую по имени колонки
            if (row[currentSortColumn] !== undefined) {
                const val = row[currentSortColumn];
                if (typeof val === 'string') return val;
                return parseFloat(val) || 0;
            }
            
            // Fallback для базовых колонок
            switch(currentSortColumn) {
                case 'symbol':
                    return row.symbol || '';
                case 'ts':
                    return row.ts || 0;
                case 'price':
                    return parseFloat(row.price) || 0;
                case 'funding_rate':
                    return parseFloat(row.funding_rate) || 0;
                case 'open_interest':
                    return parseFloat(row.open_interest) || 0;
                default:
                    return 0;
            }
        };
        
        const compareRows = (a, b) => {
            const valA = getSortValue(a);
            const valB = getSortValue(b);
            
            let result;
            if (typeof valA === 'string' && typeof valB === 'string') {
                result = valA.localeCompare(valB);
            } else {
                result = valA - valB;
            }
            
            return currentSortOrder === 'asc' ? result : -result;
        };
        
        // Сортируем только НЕ-избранные по текущей сортировке
        // Избранные остаются в фиксированном порядке добавления
        if (currentSortColumn) {
            otherRows.sort(compareRows);
        }
        
        // Сортируем избранные по порядку в localStorage (порядок добавления)
        favoriteRows.sort((a, b) => {
            const indexA = favorites.indexOf(a.symbol);
            const indexB = favorites.indexOf(b.symbol);
            return indexA - indexB;
        });
        
        return [...favoriteRows, ...otherRows];
    }

    // Кэш для форматирования (ускоряет повторные вычисления)
    const formatCache = new Map();
    
    // Оптимизированная функция создания TD
    const createTdFast = (col, text, className) => {
        const td = document.createElement("td");
        td.dataset.column = col;
        if (className) td.className = className;
        td.textContent = text;
        return td;
    };
    
    function renderScreenerTable(rows) {
        if (!screenerTableBody) {
            console.error('[Binance Data] ❌ screenerTableBody not found!');
            return;
        }
        

        
        // Используем requestAnimationFrame для плавных обновлений
        requestAnimationFrame(() => {
            const startTime = performance.now();
            
            // Проверяем есть ли уже данные в таблице (серверные данные при первой загрузке)
            const hasExistingData = screenerTableBody && screenerTableBody.querySelectorAll('tr td[data-column="symbol"]').length > 0;
            
            // Скрываем таблицу во время обновления чтобы не было видно дергания
            const table = screenerTableBody.closest('table');
            if (table) {
                table.style.visibility = 'hidden';
            }
            
            // Сортируем строки: избранные сверху
            const sortedRows = sortRowsWithFavorites(rows);
            
            // Используем DocumentFragment для батчинга DOM операций (быстрее чем innerHTML)
            const fragment = document.createDocumentFragment();
            
            if (!sortedRows.length) {
                // Если нет данных из WebSocket, но есть серверные данные - не очищаем
                if (!hasExistingData) {
                    const tr = document.createElement("tr");
                    const td = document.createElement("td");
                    td.colSpan = 31;
                    td.className = "empty-row";
                    td.textContent = "No data to display.";
                    tr.appendChild(td);
                    fragment.appendChild(tr);
                }
            } else {
                // Кэшируем часто используемые значения
                const marketType = new URLSearchParams(window.location.search).get("market_type") || "spot";
                const favorites = getFavorites();
                const favoritesSet = new Set(favorites);
                
                // Предварительно вычисляем все значения для быстрого доступа
                const storeValue = (val) => {
                    const num = Number(val);
                    return (!isNaN(num) && num !== null && num !== undefined) ? num : 0;
                };
                
                for (const row of sortedRows) {
                    const symbol = row.symbol;
                    const prev = previousValues.get(symbol) || {};
                    const rowMarketType = row.market_type || marketType;
                    const isFavorite = favoritesSet.has(symbol);
                    
                    const tr = document.createElement("tr");
                    
                    // Symbol cell - оптимизированная версия
                    const symbolTd = document.createElement("td");
                    symbolTd.dataset.column = "symbol";
                    symbolTd.className = "symbol-cell";
                    const link = document.createElement("a");
                    link.href = `/symbol/${symbol}/?market_type=${rowMarketType}`;
                    link.textContent = symbol;
                    symbolTd.appendChild(link);
                    
                    // Favorite star - оптимизированная версия
                    const star = document.createElement("span");
                    star.className = "favorite-star" + (isFavorite ? " active" : "");
                    star.dataset.symbol = symbol;
                    star.title = "Add to favorites";
                    star.textContent = isFavorite ? "★" : "☆";
                    star.addEventListener("click", (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        toggleFavorite(symbol);
                    });
                    symbolTd.appendChild(star);
                    tr.appendChild(symbolTd);
            
                    // Price - форматирование с сервера, цвет на клиенте
                    const priceValue = Number(row.price ?? 0);
                    const priceFormatted = row.price_formatted || formatPrice(row.price);
                    const priceCls = getComparisonClass(priceValue, prev.price, `${symbol}_price`);
                    tr.appendChild(createTdFast("price", priceFormatted, priceCls));

                    // Change columns - сырые данные без долларов (изменение цены)
                    const changeCols = ["change_1m", "change_5m", "change_15m", "change_30m", "change_1h", "change_4h", "change_1d"];
                    for (let i = 0; i < changeCols.length; i++) {
                        const col = changeCols[i];
                        const numValue = Number(row[col] ?? 0);
                        const rounded = Math.round(numValue);
                        const formatted = row[col + "_formatted"] || rounded.toLocaleString('en-US');
                        const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
                        tr.appendChild(createTdFast(col, formatted, cls));
                    }

                    // OI Change columns - процент изменения OI
                    const oiChangeCols = ["oi_change_1m", "oi_change_3m", "oi_change_5m", "oi_change_15m", "oi_change_30m", "oi_change_1h", "oi_change_4h", "oi_change_8h", "oi_change_1d"];
                    for (let i = 0; i < oiChangeCols.length; i++) {
                        const col = oiChangeCols[i];
                        const numValue = Number(row[col] ?? 0);
                        const formatted = row[col + "_formatted"] || formatOIChange(numValue);
                        const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
                        tr.appendChild(createTdFast(col, formatted, cls));
                    }

                    // Volatility columns - процент (high - low) / open * 100
                    const volCols = ["volatility_1m", "volatility_3m", "volatility_5m", "volatility_15m", "volatility_30m", "volatility_1h", "volatility_4h", "volatility_8h", "volatility_1d"];
                    for (let i = 0; i < volCols.length; i++) {
                        const col = volCols[i];
                        const numValue = Number(row[col] ?? 0);
                        const formatted = row[col + "_formatted"] || formatVolatility(numValue);
                        const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
                        tr.appendChild(createTdFast(col, formatted, cls));
                    }

                    // Ticks columns - всегда форматируем локально для учета compactNumbers
                    const ticksCols = ["ticks_1m", "ticks_3m", "ticks_5m", "ticks_15m", "ticks_30m", "ticks_1h", "ticks_4h", "ticks_8h", "ticks_1d"];
                    for (let i = 0; i < ticksCols.length; i++) {
                        const col = ticksCols[i];
                        const numValue = Number(row[col] ?? 0);
                        const formatted = formatTicks(numValue);
                        const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
                        tr.appendChild(createTdFast(col, formatted, cls));
                    }

                    // Vdelta columns - всегда форматируем локально для учета compactNumbers
                    const vdeltaCols = ["vdelta_1m", "vdelta_3m", "vdelta_5m", "vdelta_15m", "vdelta_30m", "vdelta_1h", "vdelta_4h", "vdelta_8h", "vdelta_1d"];
                    for (let i = 0; i < vdeltaCols.length; i++) {
                        const col = vdeltaCols[i];
                        const numValue = Number(row[col] ?? 0);
                        const formatted = formatRawDollarPrecise(numValue);
                        const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
                        tr.appendChild(createTdFast(col, formatted, cls));
                    }

                    // Volume columns - всегда форматируем локально для учета compactNumbers
                    const volumeCols = ["volume_1m", "volume_3m", "volume_5m", "volume_15m", "volume_30m", "volume_1h", "volume_4h", "volume_8h", "volume_1d"];
                    for (let i = 0; i < volumeCols.length; i++) {
                        const col = volumeCols[i];
                        const numValue = Number(row[col] ?? 0);
                        const formatted = formatRawDollarPrecise(numValue);
                        const cls = getComparisonClass(numValue, prev[col], `${symbol}_${col}`);
                        tr.appendChild(createTdFast(col, formatted, cls));
                    }

                    // Funding Rate - процент (0.0001 = 0.01%)
                    const funding = Number(row.funding_rate ?? 0);
                    const fundingPercent = funding * 100;
                    const fundingFormatted = row.funding_rate_formatted || fundingPercent.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }) + "%";
                    const fundClass = getComparisonClass(funding, prev.funding_rate, `${symbol}_funding_rate`);
                    tr.appendChild(createTdFast("funding_rate", fundingFormatted, fundClass));

                    // Open Interest - сырые данные в долларах, форматируем локально для учета compactNumbers
                    const oiValue = Number(row.open_interest ?? 0);
                    const oiFormatted = formatRawDollarPrecise(oiValue);
                    const oiCls = getComparisonClass(oiValue, prev.open_interest, `${symbol}_open_interest`);
                    tr.appendChild(createTdFast("open_interest", oiFormatted, oiCls));

                    // Timestamp - используем отформатированное значение с сервера или форматируем на клиенте
                    const rowTs = row.ts || row.timestamp || "";
                    const prevTs = prev.ts || prev.timestamp || undefined;
                    const tsStateKey = `${symbol}_ts`;
                    const tsClass = getTimestampClass(rowTs, prevTs, tsStateKey);
                    const tsFormatted = row.timestamp_formatted || formatTimestamp(rowTs);
                    tr.appendChild(createTdFast("ts", tsFormatted, tsClass));

                    fragment.appendChild(tr);
                    
                    // Store ALL values for proper comparison - оптимизированная версия
                    previousValues.set(symbol, {
                        ts: rowTs,
                        price: storeValue(row.price),
                        change_1m: storeValue(row.change_1m), change_3m: storeValue(row.change_3m),
                        change_5m: storeValue(row.change_5m), change_15m: storeValue(row.change_15m), change_30m: storeValue(row.change_30m),
                        change_1h: storeValue(row.change_1h), change_4h: storeValue(row.change_4h), change_8h: storeValue(row.change_8h), change_1d: storeValue(row.change_1d),
                        oi_change_1m: storeValue(row.oi_change_1m), oi_change_3m: storeValue(row.oi_change_3m),
                        oi_change_5m: storeValue(row.oi_change_5m), oi_change_15m: storeValue(row.oi_change_15m), oi_change_30m: storeValue(row.oi_change_30m),
                        oi_change_1h: storeValue(row.oi_change_1h), oi_change_4h: storeValue(row.oi_change_4h), oi_change_8h: storeValue(row.oi_change_8h), oi_change_1d: storeValue(row.oi_change_1d),
                        volatility_1m: storeValue(row.volatility_1m), volatility_3m: storeValue(row.volatility_3m),
                        volatility_5m: storeValue(row.volatility_5m), volatility_15m: storeValue(row.volatility_15m), volatility_30m: storeValue(row.volatility_30m),
                        volatility_1h: storeValue(row.volatility_1h), volatility_4h: storeValue(row.volatility_4h), volatility_8h: storeValue(row.volatility_8h), volatility_1d: storeValue(row.volatility_1d),
                        ticks_1m: storeValue(row.ticks_1m), ticks_3m: storeValue(row.ticks_3m),
                        ticks_5m: storeValue(row.ticks_5m), ticks_15m: storeValue(row.ticks_15m), ticks_30m: storeValue(row.ticks_30m),
                        ticks_1h: storeValue(row.ticks_1h), ticks_4h: storeValue(row.ticks_4h), ticks_8h: storeValue(row.ticks_8h), ticks_1d: storeValue(row.ticks_1d),
                        vdelta_1m: storeValue(row.vdelta_1m), vdelta_3m: storeValue(row.vdelta_3m),
                        vdelta_5m: storeValue(row.vdelta_5m), vdelta_15m: storeValue(row.vdelta_15m), vdelta_30m: storeValue(row.vdelta_30m),
                        vdelta_1h: storeValue(row.vdelta_1h), vdelta_4h: storeValue(row.vdelta_4h), vdelta_8h: storeValue(row.vdelta_8h), vdelta_1d: storeValue(row.vdelta_1d),
                        volume_1m: storeValue(row.volume_1m), volume_3m: storeValue(row.volume_3m),
                        volume_5m: storeValue(row.volume_5m), volume_15m: storeValue(row.volume_15m), volume_30m: storeValue(row.volume_30m),
                        volume_1h: storeValue(row.volume_1h), volume_4h: storeValue(row.volume_4h), volume_8h: storeValue(row.volume_8h), volume_1d: storeValue(row.volume_1d),
                        funding_rate: storeValue(row.funding_rate),
                        open_interest: storeValue(row.open_interest),
                    });
                }
            }
            
            // Один раз добавляем весь fragment в DOM (быстрее чем множественные appendChild)
            // Очищаем только если есть новые данные из WebSocket
            if (sortedRows.length > 0) {
                // Есть данные из WebSocket - обновляем таблицу
                // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Очищаем таблицу ПЕРЕД добавлением новых данных
                screenerTableBody.innerHTML = '';  // Полная очистка для гарантии
                screenerTableBody.appendChild(fragment);
                
                // Обновляем кеш строк для быстрого поиска при динамических обновлениях
                rowCache.clear();
                screenerTableBody.querySelectorAll('tr').forEach(rowEl => {
                    const symbolCell = rowEl.querySelector('td[data-column="symbol"]');
                    if (symbolCell) {
                        const link = symbolCell.querySelector('a');
                        if (link && link.textContent) {
                            const symbol = link.textContent;
                            const cells = new Map();
                            rowEl.querySelectorAll('td[data-column]').forEach(cell => {
                                const col = cell.getAttribute('data-column');
                                if (col) {
                                    cells.set(col, cell);
                                }
                            });
                            rowCache.set(symbol, { row: rowEl, cells: cells });
                        }
                    }
                });
                
                // Apply visibility после рендеринга
                applyColumnVisibility();
                
                // Обновляем ширину верхнего скроллбара после рендеринга
                const scrollbarSpacer = document.getElementById("scrollbar-spacer");
                const mainTable = document.getElementById("screener-main-table");
                if (scrollbarSpacer && mainTable) {
                    // Обновляем ширину spacer для синхронизации скролла
                    scrollbarSpacer.style.width = mainTable.scrollWidth + "px";
                }
                
                // Показываем таблицу обратно после обновления
                if (table) {
                    // Используем requestAnimationFrame для плавного появления
                    requestAnimationFrame(() => {
                        table.style.visibility = 'visible';
                        const actualRows = screenerTableBody.querySelectorAll('tr td[data-column="symbol"]').length;
                        
                        // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверяем, что данные действительно отобразились
                        if (actualRows === 0 && sortedRows.length > 0) {
                            console.error(`[Binance Data] ❌ CRITICAL: Table should have ${sortedRows.length} rows but has 0! Force re-rendering...`);
                            // Принудительно перерисовываем если данные не отобразились
                            setTimeout(() => {
                                screenerTableBody.innerHTML = '';
                                renderScreenerTable(sortedRows);
                            }, 100);
                        }
                    });
                } else {
                    console.warn('[Binance Data] ⚠️ Table element not found, cannot set visibility');
                }
            } else if (!hasExistingData && fragment.children.length > 0) {
                // Нет данных из WebSocket и нет серверных данных - показываем пустое сообщение
                screenerTableBody.textContent = "";
                screenerTableBody.appendChild(fragment);
                if (table) {
                    table.style.visibility = 'visible';
                }
            } else {
                // Нет данных из WebSocket, но есть серверные данные - сохраняем их и показываем таблицу
                if (table) {
                    table.style.visibility = 'visible';
                }
            }
            

        });
    }

    // Removed syncScrollbars - no longer needed as top scrollbar is removed

    // Initialize previous values from server-rendered table on first load
    function initializePreviousValues() {
        if (!screenerTableBody) return;
        // screenerTableBody это уже tbody, поэтому ищем просто tr (не tbody tr)
        const rows = Array.from(screenerTableBody.querySelectorAll("tr"));
        
        // Пропускаем пустые строки (например, "No data to display")
        const dataRows = rows.filter(row => {
            const symbolCell = row.querySelector('td[data-column="symbol"]');
            return symbolCell && symbolCell.textContent.trim() && !row.classList.contains('empty-row');
        });
        
        // Если нет данных, не инициализируем (подождем данных от WebSocket)
        if (dataRows.length === 0) {
            return;
        }
        
        // Helper to parse formatted values
        const parseFormattedValue = (text) => {
            if (!text) return 0;
            text = text.trim().replace('%', '');
            
            if (text.endsWith('K')) {
                return parseFloat(text.replace('K', '')) * 1000;
            }
            if (text.endsWith('M')) {
                return parseFloat(text.replace('M', '')) * 1000000;
            }
            if (text.endsWith('B')) {
                return parseFloat(text.replace('B', '')) * 1000000000;
            }
            
            const parsed = parseFloat(text);
            return isNaN(parsed) ? 0 : parsed;
        };
        
        // Helper to get numeric value from cell (handles formatted values)
        const getNumericValue = (cell) => {
            if (!cell) return 0;
            const text = cell.textContent.trim();
            // Try to parse as number first (for percentages, etc.)
            const num = parseFloat(text.replace('%', '').replace(/[KM]/g, ''));
            if (!isNaN(num)) {
                // Handle K/M suffixes
                if (text.includes('K')) return num * 1000;
                if (text.includes('M')) return num * 1000000;
                if (text.includes('B')) return num * 1000000000;
                return num;
            }
            return parseFormattedValue(text);
        };
        
        // Обновляем кеш строк при инициализации
        rowCache.clear();
        
        rows.forEach((tr) => {
            const symbolCell = tr.querySelector('td[data-column="symbol"] a');
            if (!symbolCell) return;
            const symbol = symbolCell.textContent.trim();
            
            // Кешируем строку и все ячейки для быстрого доступа
            const cells = new Map();
            tr.querySelectorAll('td[data-column]').forEach(cell => {
                const col = cell.getAttribute('data-column');
                if (col) {
                    cells.set(col, cell);
                }
            });
            rowCache.set(symbol, { row: tr, cells: cells });
            
            // Store current values as previous for next update
            // This allows dynamic updates to compare with these initial values
            const storeValue = (col) => {
                const cell = cells.get(col);
                return cell ? getNumericValue(cell) : 0;
            };
            
            // Get timestamp as string
            const tsCell = cells.get("ts");
            const tsValue = tsCell ? tsCell.textContent.trim() : "";
            
            previousValues.set(symbol, {
                ts: tsValue, // Timestamp as string for comparison
                price: storeValue("price"),
                change_1m: storeValue("change_1m"),
                change_2m: storeValue("change_2m"),
                change_3m: storeValue("change_3m"),
                change_5m: storeValue("change_5m"),
                change_15m: storeValue("change_15m"),
                change_30m: storeValue("change_30m"),
                change_1h: storeValue("change_1h"),
                change_8h: storeValue("change_8h"),
                change_1d: storeValue("change_1d"),
                oi_change_1m: storeValue("oi_change_1m"),
                oi_change_2m: storeValue("oi_change_2m"),
                oi_change_3m: storeValue("oi_change_3m"),
                oi_change_5m: storeValue("oi_change_5m"),
                oi_change_15m: storeValue("oi_change_15m"),
                oi_change_30m: storeValue("oi_change_30m"),
                oi_change_1h: storeValue("oi_change_1h"),
                oi_change_8h: storeValue("oi_change_8h"),
                oi_change_1d: storeValue("oi_change_1d"),
                volatility_1m: storeValue("volatility_1m"),
                volatility_2m: storeValue("volatility_2m"),
                volatility_3m: storeValue("volatility_3m"),
                volatility_5m: storeValue("volatility_5m"),
                volatility_15m: storeValue("volatility_15m"),
                volatility_30m: storeValue("volatility_30m"),
                volatility_1h: storeValue("volatility_1h"),
                ticks_1m: storeValue("ticks_1m"),
                ticks_2m: storeValue("ticks_2m"),
                ticks_3m: storeValue("ticks_3m"),
                ticks_5m: storeValue("ticks_5m"),
                ticks_15m: storeValue("ticks_15m"),
                ticks_30m: storeValue("ticks_30m"),
                ticks_1h: storeValue("ticks_1h"),
                vdelta_1m: storeValue("vdelta_1m"),
                vdelta_2m: storeValue("vdelta_2m"),
                vdelta_3m: storeValue("vdelta_3m"),
                vdelta_5m: storeValue("vdelta_5m"),
                vdelta_15m: storeValue("vdelta_15m"),
                vdelta_30m: storeValue("vdelta_30m"),
                vdelta_1h: storeValue("vdelta_1h"),
                vdelta_8h: storeValue("vdelta_8h"),
                vdelta_1d: storeValue("vdelta_1d"),
                volume_1m: storeValue("volume_1m"),
                volume_2m: storeValue("volume_2m"),
                volume_3m: storeValue("volume_3m"),
                volume_5m: storeValue("volume_5m"),
                volume_15m: storeValue("volume_15m"),
                volume_30m: storeValue("volume_30m"),
                volume_1h: storeValue("volume_1h"),
                volume_8h: storeValue("volume_8h"),
                volume_1d: storeValue("volume_1d"),
                funding_rate: storeValue("funding_rate"),
                open_interest: storeValue("open_interest"),
            });
        });
    }

    // Initialize main screener auto-refresh if we are on the list page.
    if (screenerTableBody) {
        // REAL-TIME ARCHITECTURE через WebSocket:
        // 1. Workers получают данные от Binance WebSocket
        // 2. Workers агрегируют и форматируют на сервере
        // 3. Отправляют через Django Channels → Redis
        // 4. Клиенты получают через WebSocket (real-time, no polling)
        // WebSocket будет инициализирован ниже в секции INITIALIZE WEBSOCKETS
        
        // НЕ вызываем initializePreviousValues() здесь, так как таблица может быть пустой
        // initializePreviousValues() будет вызвана автоматически когда придут данные от WebSocket
        
        // Apply column visibility IMMEDIATELY on page load (for server-rendered HTML)
        applyColumnVisibility();
        
        // Apply timestamp classes to initial table
        applyTimestampClasses();
        
        // Setup favorite stars in initial table
        setupFavoriteStars();
        
        // Сортируем существующие строки (избранные вверх) при загрузке страницы
        applySortToTable();
        
        // Build settings panel
        buildSettingsPanel();
        attachToggleButton();
        setupFiltersToggle();
        setupTableSorting();
        setupDraggableStatusIndicator();
        setupDraggableColumns();
        
        // Инициализируем график биткоина
        if (typeof initBitcoinChart === 'function') {
            initBitcoinChart();
        }
        
        // Start auto-refresh - previousValues будет инициализирована когда придут данные
        // refreshIntervalId уже объявлен выше в области видимости
        
        // Re-initialize previous values when WebSocket data arrives (если таблица была пустая)
        // Это гарантирует, что previousValues заполнятся когда придут данные
        
        // НЕ НУЖНО: Binance WebSocket теперь подключается на сервере
        // Сервер получает данные напрямую из Binance и передает через Django WebSocket
        // Все данные идут через Django WebSocket, не нужно подключаться к Binance напрямую
        
        // Cleanup WebSocket on page unload
        window.addEventListener('beforeunload', () => {
            disconnectWebSocket();
            // Binance WebSocket больше не используется на клиенте
            // Сервер сам управляет подключением к Binance
        });
        
        // Update scrollbar spacer after table updates (для верхнего скроллбара)
        let scrollbarSyncInitialized = false;
        const observer = new MutationObserver(() => {
            setTimeout(() => {
                const scrollbarSpacerTop = document.getElementById("scrollbar-spacer-top");
                const scrollbarTop = document.getElementById("scrollbar-top");
                const table = document.getElementById("screener-main-table");
                const tableWrapper = document.getElementById("table-wrapper");
                if (scrollbarSpacerTop && table) {
                    scrollbarSpacerTop.style.width = table.scrollWidth + "px";
                }
                // Синхронизируем прокрутку верхнего скроллбара с таблицей (только один раз)
                if (scrollbarTop && tableWrapper && !scrollbarSyncInitialized) {
                    scrollbarSyncInitialized = true;
                    // Use passive: true for better scroll performance on Mac/Safari
                    scrollbarTop.addEventListener('scroll', () => {
                        tableWrapper.scrollLeft = scrollbarTop.scrollLeft;
                    }, { passive: true });
                    tableWrapper.addEventListener('scroll', () => {
                        scrollbarTop.scrollLeft = tableWrapper.scrollLeft;
                    }, { passive: true });
                }
            }, 100);
        });
        observer.observe(screenerTableBody, { childList: true, subtree: true });
    }

    // --- Symbol detail auto-refresh ---
    const symbolContainer = document.querySelector("[data-symbol-detail]");
    if (symbolContainer) {
        const symbol = symbolContainer.getAttribute("data-symbol");
        const symbolIntervalMs = 5000; // 5s for symbol detail

        async function fetchSymbolData() {
            if (!symbol) return;
            try {
                // Preserve language prefix from current URL (e.g., /ru/, /en/, etc.)
                const currentPath = window.location.pathname;
                const langPrefix = currentPath.match(/^\/(ru|en|es|he)\//)?.[1];
                const apiPath = langPrefix ? `/${langPrefix}/api/symbol/` : "/api/symbol/";
                const resp = await fetch(`${apiPath}${encodeURIComponent(symbol)}/`);
                if (!resp.ok) return;
                const data = await resp.json();
                renderSymbolDetail(data);
            } catch (e) {
                // Silently fail - will retry on next interval
            }
        }

        function renderSymbolDetail(data) {
            if (!data) return;
            const latest = data.latest || null;
            if (latest) {
                const priceEl = document.getElementById("symbol-price");
                const vol15El = document.getElementById("symbol-volatility-15m");
                const vol5mEl = document.getElementById("symbol-volume-5m");
                const oi15El = document.getElementById("symbol-oi-change-15m");
                const fundingEl = document.getElementById("symbol-funding-rate");
                const oiEl = document.getElementById("symbol-open-interest");
                const updatedEl = document.getElementById("symbol-updated-at");

                if (priceEl) priceEl.textContent = latest.price_formatted || formatPrice(latest.price);
                if (vol15El) {
                    const v = latest.volatility_15m ?? 0;
                    vol15El.textContent = latest.volatility_15m_formatted || formatVolatility(v);
                }
                if (vol5mEl) {
                    const mt = new URLSearchParams(window.location.search).get("market_type") || "spot";
                    vol5mEl.textContent = latest.volume_5m_formatted || formatVolume(latest.volume_5m, mt);
                }
                if (fundingEl) {
                    const f = latest.funding_rate ?? 0;
                    const fNumValue = Number(f);
                    if (latest.funding_rate_formatted) {
                        fundingEl.textContent = latest.funding_rate_formatted;
                    } else {
                        const fundingPercent = fNumValue * 100;
                        fundingEl.textContent = fundingPercent.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }) + "%";
                    }
                    fundingEl.classList.remove("value-up", "value-down");
                    if (!isNaN(fNumValue) && fNumValue > 0.0000001) fundingEl.classList.add("value-up");
                    else if (!isNaN(fNumValue) && fNumValue < -0.0000001) fundingEl.classList.add("value-down");
                }
                if (oiEl) {
                    const mt = new URLSearchParams(window.location.search).get("market_type") || "spot";
                    oiEl.textContent = latest.open_interest_formatted || formatVolume(latest.open_interest, mt);
                }
                if (updatedEl) updatedEl.textContent = latest.ts || "";
                if (oi15El) {
                    const v = latest.oi_change_15m ?? 0;
                    const numValue = Number(v);
                    oi15El.textContent = latest.oi_change_15m_formatted || formatOIChange(v);
                    oi15El.classList.remove("value-up", "value-down");
                    if (!isNaN(numValue) && numValue > 0.0000001) oi15El.classList.add("value-up");
                    else if (!isNaN(numValue) && numValue < -0.0000001) oi15El.classList.add("value-down");
                }
            }

            const body = document.getElementById("symbol-history-body");
            if (!body) return;
            const snapshots = data.snapshots || [];
            body.innerHTML = "";
            if (!snapshots.length) {
                const tr = document.createElement("tr");
                const td = document.createElement("td");
                td.colSpan = 7;
                td.className = "empty-row";
                td.textContent = "No data.";
                tr.appendChild(td);
                body.appendChild(tr);
                return;
            }

            snapshots.forEach((s) => {
                const tr = document.createElement("tr");

                const tsTd = document.createElement("td");
                tsTd.textContent = s.ts;

                const priceTd = document.createElement("td");
                priceTd.textContent = s.price_formatted || formatPrice(s.price);

                const change15Td = document.createElement("td");
                const c15 = s.change_15m ?? 0;
                const c15NumValue = Number(c15);
                change15Td.textContent = s.change_15m_formatted || ((!isNaN(c15NumValue) ? c15NumValue.toFixed(2) : String(c15)) + "%");
                if (!isNaN(c15NumValue) && c15NumValue > 0.0000001) change15Td.classList.add("value-up");
                else if (!isNaN(c15NumValue) && c15NumValue < -0.0000001) change15Td.classList.add("value-down");

                const vol15Td = document.createElement("td");
                {
                    const mt = new URLSearchParams(window.location.search).get("market_type") || "spot";
                    vol15Td.textContent = s.volume_15m_formatted || formatVolume(s.volume_15m, mt);
                }
                // Volume comparison - compare with previous snapshot in the list
                if (snapshots.indexOf(s) > 0) {
                    const prevSnapshot = snapshots[snapshots.indexOf(s) - 1];
                    const volCls = getComparisonClass(s.volume_15m, prevSnapshot.volume_15m);
                    if (volCls) vol15Td.classList.add(volCls);
                }

                const oiTd = document.createElement("td");
                {
                    const mt = new URLSearchParams(window.location.search).get("market_type") || "spot";
                    oiTd.textContent = formatVolume(s.open_interest, mt);
                }
                // OI comparison - compare with previous snapshot in the list
                if (snapshots.indexOf(s) > 0) {
                    const prevSnapshot = snapshots[snapshots.indexOf(s) - 1];
                    const oiCls = getComparisonClass(s.open_interest, prevSnapshot.open_interest);
                    if (oiCls) oiTd.classList.add(oiCls);
                }

                const oi15Td = document.createElement("td");
                const oi15 = s.oi_change_15m ?? 0;
                const oi15NumValue = Number(oi15);
                oi15Td.textContent = s.oi_change_15m_formatted || formatOIChange(oi15);
                if (!isNaN(oi15NumValue) && oi15NumValue > 0.0000001) oi15Td.classList.add("value-up");
                else if (!isNaN(oi15NumValue) && oi15NumValue < -0.0000001) oi15Td.classList.add("value-down");

                const fundingTd = document.createElement("td");
                const f = s.funding_rate ?? 0;
                const fNumValue = Number(f);
                if (s.funding_rate_formatted) {
                    fundingTd.textContent = s.funding_rate_formatted;
                } else {
                    const fundingPercent = fNumValue * 100;
                    fundingTd.textContent = fundingPercent.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }) + "%";
                }
                if (!isNaN(fNumValue) && fNumValue > 0.0000001) fundingTd.classList.add("value-up");
                else if (!isNaN(fNumValue) && fNumValue < -0.0000001) fundingTd.classList.add("value-down");

                tr.appendChild(tsTd);
                tr.appendChild(priceTd);
                tr.appendChild(change15Td);
                tr.appendChild(vol15Td);
                tr.appendChild(oiTd);
                tr.appendChild(oi15Td);
                tr.appendChild(fundingTd);
                body.appendChild(tr);
            });
        }

        fetchSymbolData();
        setInterval(fetchSymbolData, symbolIntervalMs);
    }

    // Bitcoin Chart Logic
    function initBitcoinChart() {
        const canvas = document.getElementById('bitcoin-chart-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let chartData = [];
        const maxDataPoints = 100; // Number of data points to display
        let animationFrameId = null;

        const bitcoinPriceEl = document.getElementById('bitcoin-price-value');
        const bitcoinChangeEl = document.getElementById('bitcoin-change-value');

        function drawChart() {
            if (!ctx) return;

            const width = canvas.width;
            const height = canvas.height;

            ctx.clearRect(0, 0, width, height);

            if (chartData.length === 0) return;

            // Find min/max price for scaling
            const prices = chartData.map(d => d.price);
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const priceRange = maxPrice - minPrice;

            // Draw gradient background for the chart area
            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, 'rgba(255, 0, 128, 0.2)'); // Top pink
            gradient.addColorStop(0.5, 'rgba(255, 64, 179, 0.1)'); // Middle lighter pink
            gradient.addColorStop(1, 'rgba(255, 102, 204, 0.05)'); // Bottom very light pink
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, width, height);

            // Draw the price line
            ctx.beginPath();
            ctx.strokeStyle = '#ff0080'; // Vibrant pink
            ctx.lineWidth = 2;
            ctx.shadowColor = 'rgba(255, 0, 128, 0.8)';
            ctx.shadowBlur = 10;

            chartData.forEach((point, i) => {
                const x = (i / (maxDataPoints - 1)) * width;
                const y = height - ((point.price - minPrice) / priceRange) * height;
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();

            ctx.shadowBlur = 0; // Reset shadow
        }

        function updateChartData(btcPrice, btcChange) {
            const now = Date.now();
            chartData.push({ time: now, price: btcPrice });

            if (chartData.length > maxDataPoints) {
                chartData.shift(); // Remove oldest data point
            }

            if (bitcoinPriceEl) {
                bitcoinPriceEl.textContent = btcPrice.toFixed(2) + '$';
            }
            if (bitcoinChangeEl) {
                bitcoinChangeEl.textContent = btcChange.toFixed(2) + '%';
                bitcoinChangeEl.className = `bitcoin-change ${btcChange >= 0 ? 'positive' : 'negative'}`;
            }

            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            animationFrameId = requestAnimationFrame(drawChart);
        }

        // Store updateChartData globally so it can be accessed from WebSocket handler
        window._updateBitcoinChart = updateChartData;

        // Initial setup for canvas size
        function resizeCanvas() {
            const container = canvas.parentElement;
            if (container) {
                canvas.width = container.clientWidth;
                canvas.height = container.clientHeight;
                if (animationFrameId) {
                    cancelAnimationFrame(animationFrameId);
                }
                animationFrameId = requestAnimationFrame(drawChart);
            }
        }

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas(); // Initial resize
    }

    // Обработчик сворачивания/разворачивания таблицы ликвидаций
    const toggleLiquidationBtn = document.getElementById('toggle-liquidation-btn');
    const liquidationContainer = document.getElementById('liquidation-container');
    const liquidationHeader = liquidationContainer ? liquidationContainer.querySelector('.liquidation-header') : null;
    const LIQUIDATION_COLLAPSED_KEY = 'liquidation_table_collapsed';

    function toggleLiquidationTable() {
        if (!liquidationContainer) return;
        liquidationContainer.classList.toggle('collapsed');
        const collapsed = liquidationContainer.classList.contains('collapsed');
        localStorage.setItem(LIQUIDATION_COLLAPSED_KEY, collapsed ? 'true' : 'false');
    }

    if (liquidationContainer) {
        // Загружаем сохраненное состояние
        const isCollapsed = localStorage.getItem(LIQUIDATION_COLLAPSED_KEY) === 'true';
        if (isCollapsed) {
            liquidationContainer.classList.add('collapsed');
        }

        // Обработчик для кнопки
        if (toggleLiquidationBtn) {
            toggleLiquidationBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Предотвращаем двойной клик
                toggleLiquidationTable();
            });
        }

        // Обработчик для заголовка (можно кликнуть на заголовок для сворачивания)
        if (liquidationHeader) {
            liquidationHeader.addEventListener('click', (e) => {
                // Клик только на заголовок, не на кнопку
                if (e.target !== toggleLiquidationBtn && !toggleLiquidationBtn.contains(e.target)) {
                    toggleLiquidationTable();
                }
            });
        }
    }

    // Применяем позиционирование/настройки алертов при загрузке страницы (для spot и futures)
    applyLiquidationSettings(getLiquidationSettings());
    
    // ==================== INITIALIZE WEBSOCKETS ====================
    // Connect to screener WebSocket for real-time updates
    connectWebSocket();
    
    // Connect to liquidations WebSocket
    connectLiquidationWebSocket();
    
    // Устанавливаем индикатор сортировки по умолчанию (timestamp, desc - новые сверху)
    updateSortIndicators(currentSortColumn, currentSortOrder);
    
    // Периодическая очистка кеша браузера (каждые 10 минут)
    setInterval(() => {
        try {
            // Очищаем старые записи из localStorage (старше 1 часа)
            const now = Date.now();
            const oneHour = 60 * 60 * 1000;
            
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith('cache_')) {
                    try {
                        const item = JSON.parse(localStorage.getItem(key));
                        if (item && item.timestamp && (now - item.timestamp) > oneHour) {
                            localStorage.removeItem(key);
                        }
                    } catch (e) {
                        // Если не JSON, просто удаляем
                        localStorage.removeItem(key);
                    }
                }
            }
            
            // Очищаем sessionStorage от старых данных
            if (sessionStorage.length > 50) {
                sessionStorage.clear();
            }
        } catch (error) {
            console.error('[Cache] Cleanup error:', error);
        }
    }, 10 * 60 * 1000); // Каждые 10 минут
});
