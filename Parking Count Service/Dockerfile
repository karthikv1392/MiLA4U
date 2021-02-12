FROM python:3.7

COPY app /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8891

CMD [ "python", "./app.py" ]