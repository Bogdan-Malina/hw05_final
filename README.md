# hw05_final

### YaTube - социальная сеть.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Bogdan-Malina/hw05_final/
```

```
cd yatube
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
python manage.py makemigrations
```
```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
