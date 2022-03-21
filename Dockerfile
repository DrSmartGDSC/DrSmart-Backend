FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE $PORT

CMD waitress-serve --port=$PORT run:app
