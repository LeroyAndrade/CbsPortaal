# Build stage
# FROM python:3.14-slim AS builder
FROM python:3.14 AS builder
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
# FROM python:3.14-slim
FROM python:3.14

WORKDIR /app

# Dynamische manier (werkt beter op verschillende architecturen)
COPY --from=builder /usr/local /usr/local

# Kopieer alleen de applicatie code
COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["python", "main.py"]