FROM python:3.11

RUN pip install pipenv python-dotenv

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --deploy --ignore-pipfile

COPY . /app

CMD ["pipenv", "run", "python", "main.py"]
