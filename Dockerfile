FROM brinkmanlab/psortb_commandline:1.0.2

# Usa o mirror da UFSC pra acelerar o apt
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirror.ufscar.br/ubuntu/|g' /etc/apt/sources.list

RUN mkdir -p /vaxpipe/_FEATURE/PSORTB && \
    rm -rf /tmp/results && \
    ln -sf /vaxpipe/_FEATURE/PSORTB /tmp/results

# Instala dependências de sistema e Python 3.10+
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    unzip \
    git \
    xvfb \
    xauth \
    firefox \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblapack-dev \
    libblas-dev \
    libopenblas-dev \
    build-essential \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    tk-dev \
    libncursesw5-dev \
    xz-utils \
    uuid-dev && \
    rm -rf /var/lib/apt/lists/*

# Compila e instala Python 3.6.15
RUN cd /opt && \
    wget https://www.python.org/ftp/python/3.6.15/Python-3.6.15.tgz && \
    tar -xzf Python-3.6.15.tgz && \
    cd Python-3.6.15 && \
    ./configure --enable-optimizations --prefix=/opt/python3.6 && \
    make -j"$(nproc)" && \
    make altinstall && \
    ln -s /opt/python3.6/bin/python3.6 /usr/local/bin/python3.6 && \
    /opt/python3.6/bin/python3.6 -m ensurepip && \
    ln -s /opt/python3.6/bin/pip3.6 /usr/local/bin/pip3.6

# Instala OpenSSL 1.1.1w em /opt/openssl
RUN cd /opt && \
    wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz && \
    tar -xzf openssl-1.1.1w.tar.gz && \
    cd openssl-1.1.1w && \
    ./config --prefix=/opt/openssl --openssldir=/opt/openssl shared zlib && \
    make -j"$(nproc)" && \
    make install_sw && \
    rm -rf /opt/openssl-1.1.1w*

# Configura variáveis de ambiente para o OpenSSL
ENV OPENSSL_ROOT=/opt/openssl
ENV OPENSSL_DIR=/opt/openssl
ENV PATH="/opt/openssl/bin:${PATH}"
ENV LD_LIBRARY_PATH="/opt/openssl/lib:${LD_LIBRARY_PATH}"
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Instala SQLite mais recente
RUN cd /opt && \
    wget https://www.sqlite.org/2023/sqlite-autoconf-3420000.tar.gz && \
    tar -xzf sqlite-autoconf-3420000.tar.gz && \
    cd sqlite-autoconf-3420000 && \
    ./configure --prefix=/usr/local && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /opt/sqlite-autoconf-3420000*

# Atualiza as bibliotecas do sistema
RUN ldconfig

# Compila e instala Python 3.10.14 com suporte a SSL
WORKDIR /opt
RUN cd /opt && \
    wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz && \
    tar -xzf Python-3.10.14.tgz && \
    cd Python-3.10.14 && \
    CPPFLAGS="-I/opt/openssl/include" \
    LDFLAGS="-L/opt/openssl/lib" \
    ./configure \
        --enable-optimizations \
        --with-openssl=/opt/openssl \
        --prefix=/opt/python3.10 \
        --with-ensurepip=install && \
    make -j"$(nproc)" && \
    make altinstall && \
    ln -s /opt/python3.10/bin/python3.10 /usr/local/bin/python3.10 && \
    ln -s /opt/python3.10/bin/pip3.10 /usr/local/bin/pip3.10

# Instala bibliotecas Python compatíveis com seu app + VaxignML
RUN pip3.6 install --no-cache-dir \
    numpy==1.14.2 \
    scipy==1.2.1 \
    scikit-learn==0.20.3 \
    xgboost==0.81 \
    biopython==1.72 \
    matplotlib==2.2.2 \
    pandas==0.20.3 \
    pathlib 

# Instala o Geckodriver (para Selenium + Firefox)
RUN curl -sSL https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    | tar -xz -C /usr/local/bin

# Cria diretório de trabalho
WORKDIR /vaxpipe

# Copia o restante do seu projeto (Django + VaxignML)
COPY requirements .

# Copia requirements e instala dependências do seu projeto
RUN pip3.10 install --no-cache-dir --break-system-packages -r requirements

COPY . .

# Compila os arquivos C do VaxignML
WORKDIR /vaxpipe/lib/spaan/SPAAN
RUN gcc -o standard.o standard.c -lm -w \
 && gcc -o filter.o filter.c -lm -w \
 && gcc -o annotate.o annotate.c -lm -w \
 && gcc -o AAcompo/AAcompo.o AAcompo/AAcompo.c -lm -w \
 && gcc -o AAcompo/recognize.o AAcompo/recognize.c -lm -w \
 && gcc -o charge/charge.o charge/charge.c -lm -w \
 && gcc -o charge/recognize.o charge/recognize.c -lm -w \
 && gcc -o hdr/hdr.o hdr/hdr.c -lm -w \
 && gcc -o hdr/recognize.o hdr/recognize.c -lm -w \
 && gcc -o multiplets/multiplets.o multiplets/multiplets.c -lm -w \
 && gcc -o multiplets/recognize.o multiplets/recognize.c -lm -w \
 && gcc -o dipep/dipep.o dipep/dipep.c -lm -w \
 && gcc -o dipep/recognize.o dipep/recognize.c -lm -w \
 && gcc -o finalp1.o finalp1.c -lm -w

# Volta pro diretório principal
WORKDIR /vaxpipe

RUN chmod 777 /vaxpipe/_FEATURE/PSORTB && \
    chmod 777 /tmp/results

# Expor a porta do Django
EXPOSE 8000

# Comando padrão: iniciar Django
ENTRYPOINT ["/usr/bin/env"]
CMD ["python3.10", "manage.py", "runserver", "0.0.0.0:8000"]

