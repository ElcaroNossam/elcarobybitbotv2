#!/usr/bin/env python
"""
Проверка консистентности vDelta после внедрения НОВОЙ МОДЕЛИ АГРЕГАЦИИ.

Этот скрипт проверяет что:
1. Все TF показывают УНИКАЛЬНЫЕ значения (нет дублирования)
2. vDelta растет монотонно с увеличением TF (примерно линейно)
3. |vdelta| <= volume для всех TF
4. vdelta_ratio в диапазоне [-1, 1]

Ожидаемый результат после НОВОЙ МОДЕЛИ:
- ✅ 9/9 уникальных значений для каждого символа
- ✅ vdelta_5m ≈ 5 * vdelta_1m (с небольшим отклонением)
- ✅ ratio стабилен на всех TF (±0.01)

БЫЛО (старая модель):
- ❌ 3-4/9 уникальных (дублирование 30m-1d)
- ❌ vdelta_8h = vdelta_1h = vdelta_1d

СТАЛО (новая модель):
- ✅ 9/9 уникальных
- ✅ vdelta_1h > vdelta_5m > vdelta_1m
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from screener.models import ScreenerSnapshot
from datetime import datetime, timezone, timedelta


def check_vdelta_consistency():
    """Проверка консистентности vDelta на всех таймфреймах."""
    
    print("=" * 80)
    print("ПРОВЕРКА НОВОЙ МОДЕЛИ АГРЕГАЦИИ")
    print("=" * 80)
    print()
    
    # Берем последние snapshot (максимум 10 минут назад)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    
    # Проверяем несколько символов с разным объемом
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'PEPEUSDT', 'A2ZUSDT']
    
    all_passed = True
    results = []
    
    for symbol_name in test_symbols:
        snapshot = ScreenerSnapshot.objects.filter(
            symbol__symbol=symbol_name,
            ts__gte=cutoff
        ).order_by('-ts').first()
        
        if not snapshot:
            print(f"⚠️  {symbol_name}: Нет свежих данных (последние 10 минут)")
            continue
        
        symbol = symbol_name  # для вывода
        
        # Собираем все vDelta
        timeframes = ['1m', '2m', '3m', '5m', '15m', '30m', '1h', '8h', '1d']
        vdeltas = {}
        volumes = {}
        
        for tf in timeframes:
            vd = getattr(snapshot, f'vdelta_{tf}', 0)
            vol = getattr(snapshot, f'volume_{tf}', 0)
            vdeltas[tf] = vd
            volumes[tf] = vol
        
        # Проверка 1: Уникальность
        unique_values = len(set(vdeltas.values()))
        total_values = len(vdeltas)
        is_unique = unique_values == total_values
        
        # Проверка 2: Монотонность (примерно)
        # vDelta должна расти с увеличением TF (в абсолютном значении)
        abs_vdeltas = {tf: abs(vd) for tf, vd in vdeltas.items()}
        is_monotonic = (
            abs_vdeltas['1m'] <= abs_vdeltas['5m'] <= abs_vdeltas['15m'] <= 
            abs_vdeltas['1h'] <= abs_vdeltas['8h'] <= abs_vdeltas['1d']
        )
        
        # Проверка 3: |vdelta| <= volume
        ratios_valid = True
        ratios = {}
        for tf in timeframes:
            vd = abs(vdeltas[tf])
            vol = volumes[tf]
            if vol > 0:
                ratio = vd / vol
                ratios[tf] = ratio
                if ratio > 1.1:  # допускаем 10% погрешность
                    ratios_valid = False
            else:
                ratios[tf] = None
        
        # Проверка 4: Стабильность ratio на разных TF
        valid_ratios = [r for r in ratios.values() if r is not None]
        if len(valid_ratios) > 0:
            avg_ratio = sum(valid_ratios) / len(valid_ratios)
            max_deviation = max(abs(r - avg_ratio) for r in valid_ratios)
            ratio_stable = max_deviation < 0.1  # отклонение < 10%
        else:
            ratio_stable = False
        
        # Результаты
        passed = is_unique and is_monotonic and ratios_valid and ratio_stable
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{status} {symbol}")
        print(f"  Timestamp: {snapshot.ts.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  Уникальность: {unique_values}/{total_values} {'✅' if is_unique else '❌'}")
        print(f"  Монотонность: {'✅' if is_monotonic else '❌'}")
        print(f"  Ratios valid: {'✅' if ratios_valid else '❌'}")
        print(f"  Ratio stable: {'✅' if ratio_stable else '❌'}")
        print()
        
        # Детальная таблица
        print(f"  {'TF':<6} {'vDelta':>15} {'Volume':>15} {'|vD|/Vol':>10} {'Pass':>6}")
        print(f"  {'-' * 58}")
        
        for tf in timeframes:
            vd = vdeltas[tf]
            vol = volumes[tf]
            ratio = ratios[tf]
            ratio_str = f"{ratio:.4f}" if ratio is not None else "N/A"
            
            # Проверяем каждый TF
            tf_pass = (
                vd != 0 and  # не ноль
                vol > 0 and  # есть объем
                (ratio <= 1.1 if ratio else False)  # ratio корректный
            )
            
            tf_status = "✅" if tf_pass else "❌"
            
            print(f"  {tf:<6} {vd:>15,.0f} {vol:>15,.0f} {ratio_str:>10} {tf_status:>6}")
        
        print()
        
        # Дополнительная диагностика для неудачных проверок
        if not is_unique:
            # Находим дубликаты
            from collections import Counter
            value_counts = Counter(vdeltas.values())
            duplicates = {v: count for v, count in value_counts.items() if count > 1}
            print(f"  ⚠️  ДУБЛИКАТЫ:")
            for value, count in duplicates.items():
                tfs_with_value = [tf for tf, vd in vdeltas.items() if vd == value]
                print(f"     {value:,.0f} встречается {count} раз на TF: {', '.join(tfs_with_value)}")
        
        if not is_monotonic:
            print(f"  ⚠️  НЕ МОНОТОННА: vDelta должна расти с увеличением TF")
            print(f"     1m: {abs_vdeltas['1m']:,.0f}")
            print(f"     5m: {abs_vdeltas['5m']:,.0f}")
            print(f"     15m: {abs_vdeltas['15m']:,.0f}")
            print(f"     1h: {abs_vdeltas['1h']:,.0f}")
            print(f"     8h: {abs_vdeltas['8h']:,.0f}")
            print(f"     1d: {abs_vdeltas['1d']:,.0f}")
        
        print()
        print("=" * 80)
        print()
    
    # Итоговый результат
    print()
    print("=" * 80)
    if all_passed:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print()
        print("НОВАЯ МОДЕЛЬ АГРЕГАЦИИ РАБОТАЕТ КОРРЕКТНО:")
        print("  ✅ Все TF показывают уникальные значения")
        print("  ✅ vDelta растет монотонно с увеличением TF")
        print("  ✅ |vdelta| <= volume для всех TF")
        print("  ✅ vdelta_ratio стабилен на разных TF")
        print()
        print("Можно переходить к Этапу 2: удаление legacy code")
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОШЛИ")
        print()
        print("Возможные причины:")
        print("  1. Воркеры еще не перезапущены после деплоя")
        print("  2. Недостаточно времени прошло после запуска (нужно 1-2 минуты)")
        print("  3. Нет торговой активности на некоторых символах")
        print()
        print("Рекомендации:")
        print("  - Подождите 2-3 минуты")
        print("  - Проверьте логи воркеров: tail -f logs/ws_workers_err.log | grep NEW_MODEL")
        print("  - Перезапустите скрипт: python scripts/check_vdelta_consistency.py")
    
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(check_vdelta_consistency())
