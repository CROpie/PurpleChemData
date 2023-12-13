FROM python:3.10-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./data_app /code/data_app

CMD ["uvicorn", "data_app.main:app", "--host", "0.0.0.0", "--port", "82"]