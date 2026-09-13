PREMIUM_COST = 200


def calculate_weekly_coins(streak_days: int, progress_percent: float) -> int:
    """Kelishilgan jadval asosida haftalik coin miqdorini hisoblaydi."""
    if streak_days == 7 and progress_percent >= 100:
        return 100
    elif streak_days >= 6 and progress_percent >= 80:
        return 75
    elif streak_days == 5 and progress_percent >= 70:
        return 70
    elif streak_days == 4 and progress_percent >= 70:
        return 50
    elif streak_days == 3 and progress_percent >= 70:
        return 30
    elif 1 <= streak_days <= 2 and progress_percent >= 70:
        return 10
    elif streak_days >= 5 and progress_percent < 70:
        return 20
    return 0
