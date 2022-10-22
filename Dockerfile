FROM python:3.10

ENV token $token
ENV owner_id $owner_id

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
