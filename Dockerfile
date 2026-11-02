FROM python:3.14.4

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "alembic upgrade head && exec fastapi run app/main.py --host 0.0.0.0 --port 8000"]

