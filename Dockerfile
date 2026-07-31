FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers du projet
COPY main.py .
COPY database.py .
COPY moderation.py .
COPY welcome.py .
COPY family.py .
COPY server.py .
COPY index.html .
COPY games.py .

# Variables d'environnement par défaut
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Exposer le port pour l'API
EXPOSE 8080

# Lancer l'API Flask (bot et API dans le même conteneur)
CMD ["python", "server.py"]
