// Language Switcher Component
const LANGUAGE_NAMES = {
    en: { name: 'English', flag: '🇬🇧' },
    ru: { name: 'Русский', flag: '🇷🇺' },
    uk: { name: 'Українська', flag: '🇺🇦' },
    de: { name: 'Deutsch', flag: '🇩🇪' },
    es: { name: 'Español', flag: '🇪🇸' },
    fr: { name: 'Français', flag: '🇫🇷' },
    it: { name: 'Italiano', flag: '🇮🇹' },
    pl: { name: 'Polski', flag: '🇵🇱' },
    ja: { name: '日本語', flag: '🇯🇵' },
    zh: { name: '中文', flag: '🇨🇳' },
    ar: { name: 'العربية', flag: '🇸🇦' },
    he: { name: 'עברית', flag: '🇮🇱' },
    cs: { name: 'Čeština', flag: '🇨🇿' },
    lt: { name: 'Lietuvių', flag: '🇱🇹' },
    sq: { name: 'Shqip', flag: '🇦🇱' }
};

function createLangSwitcher(containerId = 'lang-switcher') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const currentLang = i18n.getLang();
    const current = LANGUAGE_NAMES[currentLang] || LANGUAGE_NAMES.en;
    
    container.innerHTML = `
        <div class="lang-dropdown">
            <button class="lang-btn" onclick="toggleLangMenu()">
                <span class="lang-flag">${current.flag}</span>
                <span class="lang-code">${currentLang.toUpperCase()}</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="lang-menu" id="langMenu">
                ${Object.entries(LANGUAGE_NAMES).map(([code, info]) => `
                    <div class="lang-option ${code === currentLang ? 'active' : ''}" 
                         onclick="selectLang('${code}')">
                        <span class="lang-flag">${info.flag}</span>
                        <span class="lang-name">${info.name}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function toggleLangMenu() {
    const menu = document.getElementById('langMenu');
    menu.classList.toggle('show');
}

function selectLang(code) {
    i18n.setLang(code);
    createLangSwitcher();
    document.getElementById('langMenu').classList.remove('show');
}

// Close menu on outside click
document.addEventListener('click', (e) => {
    if (!e.target.closest('.lang-dropdown')) {
        const menu = document.getElementById('langMenu');
        if (menu) menu.classList.remove('show');
    }
});

// CSS for language switcher
const langSwitcherStyles = `
<style>
.lang-dropdown {
    position: relative;
    display: inline-block;
}

.lang-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--bg-secondary, #12121a);
    border: 1px solid var(--border, #2a2a3a);
    border-radius: 8px;
    color: var(--text-primary, #fff);
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s;
}

.lang-btn:hover {
    border-color: var(--accent, #00d4aa);
}

.lang-flag {
    font-size: 1.2rem;
}

.lang-menu {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 0.5rem;
    background: var(--bg-card, #1a1a24);
    border: 1px solid var(--border, #2a2a3a);
    border-radius: 8px;
    min-width: 160px;
    max-height: 300px;
    overflow-y: auto;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s;
    z-index: 1000;
}

.lang-menu.show {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.lang-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1rem;
    cursor: pointer;
    transition: background 0.2s;
}

.lang-option:hover {
    background: rgba(0, 212, 170, 0.1);
}

.lang-option.active {
    background: rgba(0, 212, 170, 0.2);
    color: var(--accent, #00d4aa);
}

.lang-name {
    font-size: 0.85rem;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', langSwitcherStyles);

// Auto-init on load
document.addEventListener('DOMContentLoaded', () => {
    createLangSwitcher();
});
