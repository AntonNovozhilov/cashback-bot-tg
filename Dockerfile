FROM python:3.9

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .
RUN pip install poetry
COPY . .
RUN poetry install --no-root



CMD ["poetry", "run", "python", "bot.py"]
