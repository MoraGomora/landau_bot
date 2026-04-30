from datetime import date


def next_ban_duration(
    prev_duration: int | None,
    *,
    base: int = 35,
    multiplier: float = 1.5,
    step: int = 0,
    max_duration: int | None = 86400
) -> int:
    """
    Вычисляет следующую длительность бана.
    
    Args:
        prev_duration: предыдущее время бана (в секундах)
        base: начальное значение (для первого бана)
        multiplier: коэффициент роста
        step: дополнительный прирост
        max_duration: максимальная длительность (потолок)
    
    Returns:
        Длительность в секундах
    """
    if prev_duration is None:
        return base

    new = int(prev_duration * multiplier + step)

    if max_duration:
        new = min(new, max_duration)

    return new


def today() -> str:
    """Возвращает сегодняшнюю дату в ISO формате."""
    return date.today().isoformat()
