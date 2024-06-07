FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV $(cat .env | grep -v ^# | xargs)

CMD ["cat", ".env"]
