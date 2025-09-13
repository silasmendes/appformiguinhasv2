# Usa imagem baseada em Debian com Python 3.12
FROM python:3.12-slim-bullseye

# Instala dependências do sistema, incluindo ODBC Driver 17
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates apt-transport-https software-properties-common gcc g++ unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia o conteúdo do projeto
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Flask
EXPOSE 5000

# Comando para iniciar a aplicação com Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]

