FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install pdm && pdm install --prod --no-lock --no-editable

CMD ["pdm", "run", "start", "--host", "0.0.0.0"]
