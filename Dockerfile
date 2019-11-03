FROM python:3.7-slim
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
ENV FLASK_APP=/example FLASK_ENV=development
ENTRYPOINT flask run --with-threads --host 0.0.0.0 --port 8080
