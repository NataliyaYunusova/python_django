FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.5.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY mysite .
COPY mysite/shopapp/fixtures app/fixtures
COPY mysite/database/db.sqlite3 database/

RUN python manage.py makemigrations
RUN python manage.py migrate

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
