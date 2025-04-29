import os
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env

sendgrid_api_key = os.getenv("SENDGRID_API_KEY")


def enviar_email():
    try:
        # Gerar novo nome para o arquivo
        agora = datetime.datetime.now()
        data_atual = agora.strftime('%d-%m-%Y')
        hora_atual = agora.strftime('%H-%M-%S')
        nome_atual = 'Final.zip'
        novo_nome = f'Final_{data_atual}_{hora_atual}.zip'
        os.rename(nome_atual, novo_nome)
        arquivos_intermed = "MHCintermediariesFILES.zip"

        # Ler destinatário do arquivo
        with open("email.str", "r") as email_file:
            email_content = email_file.read().strip()
        
        # Ler nome da análise
        with open ("analysisname.str", "r") as analysisname_file:
            analysisname = analysisname_file.read().strip()

        # Criar mensagem
        mensagem = Mail(
            from_email="info@satyasistemas.com.br",
            to_emails=email_content,
            subject = f"VaxPIPE Results - Analysis: {analysisname} ({datetime.datetime.now().strftime('%Y-%m-%d')})",
            plain_text_content="VaxPIPE Results\nThanks for using"
        )

        # Função para anexar arquivos
        def anexar_arquivo(mensagem, caminho_anexo):
            if os.path.exists(caminho_anexo):
                with open(caminho_anexo, 'rb') as f:
                    conteudo = base64.b64encode(f.read()).decode()
                anexo = Attachment(
                    FileContent(conteudo),
                    FileName(os.path.basename(caminho_anexo)),
                    FileType('application/zip'),
                    Disposition('attachment')
                )
                mensagem.add_attachment(anexo)

        # Anexar os arquivos
        anexar_arquivo(mensagem, novo_nome)
        anexar_arquivo(mensagem, arquivos_intermed)

        # Enviar e-mail pelo SendGrid
        api_key = os.getenv("SENDGRID_API_KEY")  # Pega a chave da API do ambiente
        if not api_key:
            raise ValueError("SENDGRID_API_KEY não está configurada")

        sg = SendGridAPIClient(api_key)
        resposta = sg.send(mensagem)

        if resposta.status_code in [200, 202]:
            print("E-mail enviado com sucesso!")
        else:
            print(f"Erro ao enviar e-mail: {resposta.status_code} - {resposta.body}")

    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")

def apagar_arquivos():
    diretorio_atual = os.getcwd()
    extensoes = ['.txt', '.csv', '.faa', '.png', 'str', 'zip', 'tsv', 'sh']
    for arquivo in os.listdir(diretorio_atual):
        # Verificar se o arquivo tem uma das extensões a serem excluídas
        if any(arquivo.endswith(extensao) for extensao in extensoes):
            # Construir o caminho completo do arquivo
            caminho_arquivo = os.path.join(diretorio_atual, arquivo)
            # Tentar excluir o arquivo
            try:
                os.remove(caminho_arquivo)
                print(f"Arquivo {arquivo} excluído com sucesso.")
            except Exception as e:
                print(f"Erro ao excluir o arquivo {arquivo}: {e}")

