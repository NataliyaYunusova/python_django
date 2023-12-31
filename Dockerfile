FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.5.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY mysite .

RUN python manage.py makemigrations
RUN python manage.py migrate
COPY mysite/shopapp/fixtures app/shopapp/fixtures

CMD ["python", "manage.py", "loaddata", "*.json"]
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000",  "--timeout", "120"]