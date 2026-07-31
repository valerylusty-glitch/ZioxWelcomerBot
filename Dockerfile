FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers du projet
COPY bot/ ./bot/
COPY api/ ./api/
COPY webapp/ ./webapp/
COPY start.py .

ENV PYTHONUNBUFFERED=1

# Le port est injecté par Railway via la variable PORT
EXPOSE 8080

CMD ["python", "start.py"]
