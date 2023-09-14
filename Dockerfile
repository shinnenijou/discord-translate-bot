FROM python:3.10.9

WORKDIR /app
STOPSIGNAL SIGINT

ENV PATH="${PATH}:/root/.local/bin"

COPY bilibili /app/bilibili
COPY client /app/client
COPY translate /app/translate
COPY utils /app/utils
COPY webhook /app/webhook
COPY main.py /app/
COPY requirements.txt /app

RUN pip install --upgrade -r requirements.txt \
    && rm requirements.txt

ENTRYPOINT [ "python3", "main.py" ]