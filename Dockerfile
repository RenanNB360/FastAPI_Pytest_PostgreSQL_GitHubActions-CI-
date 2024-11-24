FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
COPY . /app/
COPY entrypoint.sh /app/entrypoint.sh

RUN pip install poetry psycopg2-binary
RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "fast_postgres.app:app"]