FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
# RUN python ./kepler/manage.py collectstatic --noinput

CMD ["sh", "-c", "python ./kepler/manage.py migrate && python ./kepler/manage.py runserver 0.0.0.0:8000"]