FROM python:3.9

# Install Firefox and other dependencies
RUN apt-get update && apt-get install -y firefox-esr xvfb

# Install Python packages
RUN pip install selenium

# Install xvfb and xauth packages
RUN apt-get install -y xvfb xauth

RUN apt-get install -y zip docker*

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o restante dos arquivos do aplicativo para o diretório de trabalho
COPY . .

# Exponha a porta em que o Django está sendo executado
EXPOSE 8000

# Comando para iniciar o servidor Django quando o contêiner for iniciado
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


