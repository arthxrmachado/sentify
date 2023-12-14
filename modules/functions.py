from modules.libraries import Translator, re, enchant, redirect, url_for, TextBlob, render_template, session, send_file

# Inicializando o tradutor
translator = Translator()


def index():
    try:
        # renderizando a página inicial
        return render_template('index.html', show_results=False)

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro na página inicial: {str(e)}"
        print(error_message)
        return render_template('error.html', error_message=error_message)


def error():
    try:
        error_message = request.args.get('error_message', 'Erro desconhecido')
        return render_template('error.html', error_message=error_message)
    except Exception as e:
        return render_template('error.html', error_message='Erro ao processar a solicitação')


def detect_and_translate_language(text):
    try:
        # detectando idioma
        detected_lang = translator.detect(text)

        # traduzindo para o inglês, se necessário
        if detected_lang and detected_lang.lang != 'en':
            translated_text = translator.translate(text, src=detected_lang.lang, dest='en').text
            return translated_text
        else:
            return text

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro durante a detecção e tradução de idioma: {str(e)}"
        return redirect(url_for('error', error_message=error_message))


def clean_text(text):
    try:
        # removendo caracteres indesejados, excluindo
        cleaned_text = re.sub(r'[^A-Za-z0-9\s.,!?]', '', text)

        # removendo sequências de três ou mais letras iguais consecutivas
        cleaned_text = re.sub(r'(\w)\1{2,}', r'\1\1', cleaned_text)

        # tokenização considerando pontos de exclamação, pontos finais e pontos de interrogação
        tokens = re.findall(r'\b(?:\w+|[.,!?])\b|\.+|!|\?', cleaned_text)

        # correção ortográfica usando pyenchant (tratando exceções para pontuações)
        corrected_tokens = []
        for token in tokens:
            if token in (',', '.', '!', '?'):
                corrected_tokens.append(token)
            else:
                corrected_tokens.append(enchant.Dict("en_US").suggest(token)[0] if not
                enchant.Dict("en_US").check(token) else token)

        # juntando os tokens corrigidos de volta em uma string
        clean_text = ' '.join(corrected_tokens)

        return clean_text

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro durante a limpeza do texto: {str(e)}"
        return redirect(url_for('error', error_message=error_message))


def get_sentiment_label(polarity):
    try:
        # pegando a polaridade de cada frase e retornando o resultado
        if polarity >= 0.7:
            return "Muito Positivo"
        elif 0.3 <= polarity < 0.7:
            return "Positivo"
        elif -0.3 < polarity < 0.3:
            return "Neutro"
        elif -0.7 <= polarity <= -0.3:
            return "Negativo"
        else:
            return "Muito Negativo"

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro durante a detecção de polaridade: {str(e)}"
        return redirect(url_for('error', error_message=error_message))


def summarize_results(sentiment_results):
    try:
        # calculando as estatísticas resumidas
        total_sentences = len(sentiment_results)
        positive_count = sum(1 for _, _, _, label in sentiment_results if label == 'Positivo')
        neutral_count = sum(1 for _, _, _, label in sentiment_results if label == 'Neutro')
        negative_count = sum(1 for _, _, _, label in sentiment_results if label == 'Negativo')

        # calculando a média de polaridade e subjetividade
        avg_polarity = round(sum(polarity for _, polarity, _, _ in sentiment_results) / total_sentences, 2)
        avg_subjectivity = round(sum(subjectivity for _, _, subjectivity, _ in sentiment_results) / total_sentences, 2)

        # criando um dicionário com as estatísticas resumidas
        summary_stats = {
            'Total de Frases': total_sentences,
            'Frases Positivas': positive_count,
            'Frases Neutras': neutral_count,
            'Frases Negativas': negative_count,
            'Média de Polaridade': avg_polarity,
            'Média de Subjetividade': avg_subjectivity
        }

        return summary_stats

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro durante a sumarização de resultados: {str(e)}"
        return redirect(url_for('error', error_message=error_message))



def view_result():
    try:
        # recuperando os resultados da variável de sessão
        translated_results = session.get('translated_results', [])
        summary_stats = session.get('summary_stats', [])

        # renderizando o resultado na página de visualização
        return render_template('result.html', translated_results=translated_results,
                               summary_stats=summary_stats)

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro ao visualizar resultados: {str(e)}"
        return render_template('error.html', error_message=error_message)


def download_output():
    try:
        # fazendo o download do arquivo para a máquina do usuário
        return send_file('../output.txt', as_attachment=True)

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro durante o download do arquivo: {str(e)}"
        return render_template('error.html', error_message=error_message)