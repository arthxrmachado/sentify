from flask import Flask
from modules.functions import index, view_result, download_output
from modules.sentiment_analysis import analyze_sentiment

app = Flask(__name__)

# Defina uma chave secreta para usar a sessão
app.secret_key = 'vascodagama'

# Configuração das rotas
app.add_url_rule('/','index', index, methods=['GET'])
app.add_url_rule('/analyze_sentiment', 'analyze_sentiment', analyze_sentiment, methods=['POST'])
app.add_url_rule('/view_result', 'view_result', view_result, methods=['GET'])
app.add_url_rule('/download', 'download_output', download_output, methods=['GET'])
app.add_url_rule('/error', 'error', methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
