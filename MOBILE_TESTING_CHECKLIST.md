# Mobile Optimization Testing Checklist ✅

## Quick Test Guide

Дата: December 25, 2025  
Версия: 2.0.0

---

## 1. Landing Page (index.html)

### Desktop (>1024px)
- [ ] Navbar фиксированный с blur эффектом при скролле
- [ ] Все секции в 2-3 колонки
- [ ] Hero section на весь экран
- [ ] Языковое меню работает

### Tablet (768px - 1024px)
- [ ] Navbar компактный
- [ ] Features/Strategies в 2 колонки
- [ ] Pricing cards в 2 колонки
- [ ] Кнопки достаточно большие (40px)

### Mobile (<=768px)
- [ ] Hamburger menu появляется
- [ ] Меню открывается/закрывается плавно
- [ ] Все секции в 1 колонку
- [ ] Hero h1 = 32px
- [ ] CTA buttons на всю ширину
- [ ] Языковое меню внизу экрана (bottom sheet)

### Small Phone (<=480px)
- [ ] Hero h1 = 28px
- [ ] Subtitle = 14px
- [ ] Section title = 24px
- [ ] Все карточки уменьшены

---

## 2. Terminal (terminal.html)

### Desktop
- [ ] 3-column layout (orderbook | chart | orders)
- [ ] Все панели видны
- [ ] TradingView chart полностью работает

### Tablet
- [ ] Left panel (orderbook) скрыт
- [ ] 2-column layout (chart | orders)
- [ ] Sidebar toggle кнопка появляется

### Mobile
- [ ] **КРИТИЧНО**: Sidebar toggle в правом нижнем углу
- [ ] Swipe right открывает orderbook
- [ ] Swipe left закрывает orderbook
- [ ] 1-column layout (stacked vertically)
- [ ] Chart height = 400px (300px на маленьких)
- [ ] Positions table horizontal scroll
- [ ] Первая колонка таблицы sticky

### Touch Tests
- [ ] Все кнопки >=44px
- [ ] Swipe жесты работают плавно
- [ ] Double-tap не зумит
- [ ] Input focus не зумит страницу

---

## 3. Screener (screener.html)

### Desktop
- [ ] Layout: top movers sidebar | main table
- [ ] 14 колонок видны
- [ ] Real-time WebSocket updates

### Tablet
- [ ] Top movers горизонтальный скролл
- [ ] Таблица horizontal scroll
- [ ] Market toggle buttons на всю ширину

### Mobile
- [ ] Top movers - horizontal scroll с карточками
- [ ] Таблица - horizontal scroll
- [ ] Symbol column - sticky (первая колонка)
- [ ] Market buttons 50/50 ширины
- [ ] Stats grid в 2 колонки (на <480px = 1 колонка)

### Performance
- [ ] WebSocket не лагает
- [ ] Scroll плавный
- [ ] Нет horizontal body scroll

---

## 4. Backtest (backtest.html)

### Desktop
- [ ] 3-column layout
- [ ] Charts видны полностью
- [ ] Metrics в 3-4 колонки

### Tablet
- [ ] 2-column layout
- [ ] Metrics в 2 колонки

### Mobile
- [ ] 1-column stacked layout
- [ ] Strategy cards вертикально
- [ ] Form inputs на всю ширину
- [ ] Charts height = 300px
- [ ] Metrics в 1 колонку (<768px)
- [ ] Trades table horizontal scroll

---

## 5. Dashboard (dashboard.html)

### Desktop
- [ ] Multi-column grid
- [ ] Performance chart полностью виден
- [ ] Stats cards в 3-4 колонки

### Tablet
- [ ] 2-column grid
- [ ] Stats в 2 колонки

### Mobile
- [ ] 1-column stacked
- [ ] Portfolio value = 28px
- [ ] Position cards вертикально
- [ ] Chart height = 300px
- [ ] Stats в 1 колонку

---

## 6. Settings (settings.html)

### Desktop
- [ ] Sidebar + content layout
- [ ] Settings sections видны

### Tablet
- [ ] Sidebar скрыт
- [ ] Dropdown navigation появляется

### Mobile
- [ ] Dropdown navigation работает
- [ ] Smooth scroll к секциям
- [ ] Form inputs font-size = 16px (no zoom)
- [ ] Buttons на всю ширину

---

## Cross-Browser Tests

### iOS Safari (iPhone)
- [ ] Viewport height корректен (--vh)
- [ ] Toolbar не перекрывает контент
- [ ] Touch gestures работают
- [ ] No zoom on input focus

### Chrome Android
- [ ] Touch ripple effects работают
- [ ] Swipe gestures без конфликтов
- [ ] Keyboard не ломает layout

### Samsung Internet
- [ ] Все стили применяются
- [ ] Touch events работают
- [ ] WebSocket соединение стабильное

---

## Orientation Tests

### Portrait → Landscape
- [ ] Layout перестраивается плавно
- [ ] Меню закрывается автоматически
- [ ] Charts resize корректно
- [ ] Header уменьшается (48px)

### Landscape → Portrait
- [ ] Все элементы возвращаются
- [ ] Scroll position сохраняется
- [ ] Sidebar закрывается

---

## Performance Tests

### Page Load
- [ ] Mobile CSS загружается (<100ms)
- [ ] Mobile JS загружается (<200ms)
- [ ] No layout shift (CLS < 0.1)
- [ ] First paint < 1s

### Lighthouse Scores
```bash
lighthouse https://your-domain.com --preset=perf --view
```
Target:
- [ ] Performance: 90+
- [ ] Accessibility: 95+
- [ ] Best Practices: 90+
- [ ] SEO: 90+

### Network Throttling (3G)
- [ ] Page загружается < 5s
- [ ] Images lazy load
- [ ] Критичный CSS inline
- [ ] Fonts не блокируют render

---

## Accessibility Tests

### Touch Targets
- [ ] Все кнопки >= 44x44px
- [ ] Gap между targets >= 8px
- [ ] No overlapping touch areas

### Screen Reader
- [ ] aria-labels присутствуют
- [ ] role attributes корректны
- [ ] Headings структура логична

### Keyboard Navigation
- [ ] Tab order логичен
- [ ] Focus visible
- [ ] Skip links работают
- [ ] Escape закрывает модалы

---

## Real Device Testing

### iPhone SE (320px)
- [ ] Ничего не обрезано
- [ ] Текст читаем
- [ ] Кнопки нажимаемые
- [ ] Формы работают

### iPhone 12/13 (390px)
- [ ] Standard mobile layout
- [ ] Все features работают
- [ ] Portrait + Landscape

### iPad (768px)
- [ ] Tablet layout корректен
- [ ] 2-column где нужно
- [ ] Touch targets удобны

### iPad Pro (1024px)
- [ ] Desktop-like layout
- [ ] Sidebar видимый
- [ ] Full functionality

---

## Common Issues to Check

### ❌ Avoid
- [ ] Horizontal scroll на body
- [ ] Text overflow без ellipsis
- [ ] Buttons < 44px
- [ ] Input font-size < 16px
- [ ] Fixed positioning блокирует scroll
- [ ] Zoom на input focus

### ✅ Verify
- [ ] Smooth scrolling
- [ ] Touch feedback (ripple/highlight)
- [ ] Loading states видны
- [ ] Error messages читаемы
- [ ] Success toasts не перекрывают кнопки

---

## Test Commands

### Start Dev Server
```bash
./start.sh --webapp
```

### Run Lighthouse
```bash
lighthouse http://localhost:8765 --preset=perf --view
```

### Check Mobile CSS
```bash
cat webapp/static/css/mobile.css | wc -l
# Should be 1080+ lines
```

### Check Mobile JS
```bash
cat webapp/static/js/mobile-navigation.js | wc -l
# Should be 560+ lines
```

---

## Sign-off

Tester: ___________________  
Date: ___________________  
Build: 2.0.0  

### Overall Status
- [ ] All tests passed ✅
- [ ] Minor issues (document below) ⚠️
- [ ] Major issues (fix required) ❌

### Notes:
```
[Add testing notes here]
```

---

**Next Steps After Testing:**
1. Fix any found issues
2. Re-test on real devices
3. Update MOBILE_OPTIMIZATION_GUIDE.md
4. Deploy to production
5. Monitor analytics for mobile usage

---

**Quick Test URL:**
- Local: http://localhost:8765
- Staging: https://staging.elcaro.com
- Production: https://elcaro.com

**Contact:** @elcaro_support
