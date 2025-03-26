FROM python:3.9

# Instalar dependências para o Docker-in-Docker
RUN apt-get update && apt-get install -y \
    docker.io \
    firefox-esr \
    xvfb \
    xauth \
    curl \
    zip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Instalar o Selenium
RUN pip install selenium

# Baixar e instalar o geckodriver (necessário para o selenium com Firefox)
RUN curl -sSL https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar -xz -C /usr/local/bin

# Copiar o arquivo requirements para o diretório de trabalho
COPY requirements .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o restante dos arquivos do aplicativo para o diretório de trabalho
COPY . .

# Expor a porta em que o Django estará sendo executado
EXPOSE 8000

# Comando para iniciar o servidor Django quando o contêiner for iniciado
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

