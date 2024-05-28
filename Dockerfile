FROM python:3.11

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy --ignore-pipfile

COPY . /app

# Создаем директорию для хранения файлов данных
RUN mkdir /app/data && chown -R 1000:1000 /app/data

USER 1000

ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_IGNORE_VIRTUALENVS=1
ENV BOT_TOKEN=$BOT_TOKEN

CMD ["python", "main.py"]
