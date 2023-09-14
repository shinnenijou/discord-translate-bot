FROM python:3.10.9

WORKDIR /app
STOPSIGNAL SIGINT

ENV PATH="${PATH}:/root/.local/bin"

COPY bilibili /app/
COPY client /app/
COPY translate /app/
COPY utils /app/
COPY webhook /app/
COPY main.py /app/

RUN pip install --upgrade -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]