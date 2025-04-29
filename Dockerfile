FROM docker:dind

# Evitar prompts interativos na instalação
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar pacotes e instalar dependências do sistema
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    xvfb \
    xauth \
    curl \
    wget \
    zip \
    sudo \
    ca-certificates \
    gnupg \
    fuse-overlayfs \
    bash \
    firefox \
    build-base \
    python3-dev \
    libffi-dev \
    musl-dev \
    openssl-dev \
    lapack-dev \
    freetype-dev \
    libpng-dev \
    openblas-dev \
    libxml2-dev \
    libxslt-dev \
    jpeg-dev \
    zlib-dev

RUN pip3 install --no-cache-dir selenium --break-system-packages


# Baixar e instalar o geckodriver (necessário para Selenium + Firefox)
RUN curl -sSL https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz | tar -xz -C /usr/local/bin

# Definir o diretório de trabalho
WORKDIR /vaxpipe

# Copiar e instalar dependências do Python
COPY requirements .
RUN pip3 install --no-cache-dir -r requirements --break-system-packages

# Copiar o restante dos arquivos do aplicativo para o diretório de trabalho
COPY . .

# Expor a porta do Django
EXPOSE 8000

# Iniciar o Docker dentro do contêiner e rodar o Django
CMD ["sh", "-c", "dockerd-entrypoint.sh & sleep 3 && python manage.py runserver 0.0.0.0:8000"]

