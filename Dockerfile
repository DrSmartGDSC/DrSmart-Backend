FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE $PORT

WORKDIR src

CMD waitress-serve --port=$PORT run:app
