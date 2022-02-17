FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# testing github secrects
RUN echo $SKIN_MODEL_ID > test.txt
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id='"$SKIN_MODEL_ID" -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=""$SKIN_MODEL_ID" -O test_skin_model.h5 && rm -rf /tmp/cookies.txt

EXPOSE $PORT

CMD waitress-serve --port=$PORT run:app
