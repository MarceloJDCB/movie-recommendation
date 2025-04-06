FROM python:3.9-slim

# Set working directory to the project root
WORKDIR /app

# Copiar e instalar requisitos principais
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Não copiar os arquivos do app aqui, pois serão montados como volume
# O volume no docker-compose.yml sobrescreverá esses arquivos de qualquer forma

EXPOSE 8000

# Adicionar o flag --reload-dir para monitorar explicitamente o diretório da aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]