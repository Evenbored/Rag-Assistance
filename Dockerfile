# Инициализируем uv через официальный образ
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

FROM python:3.11-slim

# Копируем uv и uvx в систему
COPY --from=uv_bin /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Используем uv с системным флагом и монтированием кэша
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]