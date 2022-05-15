import datetime as dt

year_now = dt.datetime.now().year


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        "year": int(year_now)
    }
