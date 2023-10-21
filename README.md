# YaTube

### YaTube - социальная сеть.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Bogdan-Malina/YaTube.git
```

```
cd YaTube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/bin/activate
```

Обновить pip в виртуальном окружении
```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Выполнить миграции:
```
cd yatube
```
```
python manage.py makemigrations
```
```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Технологии:
- Python 3.7
- Django 2.2.16
- Pillow 9.5.0
- pytest 6.2.4
- pytest-django 4.4.0
- pytest-pythonpath 0.7.3

### Автор
Данил Воронин https://github.com/Bogdan-Malina


