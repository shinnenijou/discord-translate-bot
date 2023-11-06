FROM python:3.10.9

WORKDIR /app
STOPSIGNAL SIGINT

ENV PATH="${PATH}:/root/.local/bin"

COPY . /app

RUN pip install --upgrade -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]