FROM python:3.11

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv

COPY . /app

RUN pipenv install --system --deploy --ignore-pipfile

USER 1000

ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_IGNORE_VIRTUALENVS=1

CMD ["python", "main.py"]
