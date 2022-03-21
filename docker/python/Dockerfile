FROM tensorflow/tensorflow:latest as python-base

WORKDIR /app

RUN pip install -U pip
RUN pip install poetry scikit-learn==1.5.1 tf-keras==2.17.0 sentence-transformers==3.0.1

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry config virtualenvs.create false
RUN poetry install

FROM python-base as common

WORKDIR /app

EXPOSE 8000

COPY . .

WORKDIR /app/src

FROM common as release

CMD python -m gunicorn main:app --workers 4 --timeout 300 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
