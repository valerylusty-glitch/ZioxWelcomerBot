FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances du bot + API
RUN pip install --no-cache-dir \
    python-telegram-bot==21.6 \
    python-dotenv==1.0.1 \
    SQLAlchemy==2.0.35 \
    Flask==3.0.3 \
    flask-cors==4.0.1

# Copier les fichiers du projet
COPY main.py .
COPY database.py .
COPY moderation.py .
COPY welcome.py .
COPY family.py .
COPY server.py .
COPY index.html .
COPY games.py .

ENV PYTHONUNBUFFERED=1

# Le port est injecté par Railway via la variable PORT (par défaut 8080)
EXPOSE 8080

CMD ["python", "server.py"]
