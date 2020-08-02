FROM python:3.7.8-alpine3.11
WORKDIR /usr/app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV FLASK_APP run.py
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
