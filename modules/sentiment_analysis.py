from flask import render_template, session
from modules.functions import (translator, detect_and_translate_language, clean_text, get_sentiment_label,
                               summarize_results)
from modules.libraries import (SentimentIntensityAnalyzer, request, FileStorage, docx2txt, PdfReader, re,
                               TextBlob)

sia = SentimentIntensityAnalyzer()


def analyze_sentiment():
    try:
        # inicializando variáveis
        text = request.form['text']
        file = request.files['file']
        translated_results = []
        summary_stats = []
        show_results = False

        if text.strip():
            # detectando o idioma e traduzindo para o inglês
            text = detect_and_translate_language(text)
            # removendo caracteres indesejados
            text = clean_text(text)

        if isinstance(file, FileStorage):
            # lidando com o arquivo enviado
            file_extension = file.filename.split('.')[-1].lower()

            if file_extension == 'txt':
                file_text = file.read().decode('utf-8')

            elif file_extension == 'doc' or file_extension == 'docx':
                file_text = docx2txt.process(file)

            elif file_extension == 'csv':
                df = pd.read_csv(file)
                file_text = ' '.join(df['text'])

            elif file_extension == 'pdf':
                pdf = PdfReader(file)
                pdf_text = ""
                for page in pdf.pages:
                    pdf_text += page.extract_text()
                file_text = pdf_text

            else:
                file_text = ''

            if file_text:
                # detectando idioma e traduzindo para o inglês
                file_text = detect_and_translate_language(file_text)
                # removendo caracteres indesejados
                file_text = clean_text(file_text)

            # adicionando um ponto final à frase manual se não houver
            if text.strip() and not text.endswith(('.', '!', '?')):
                text += '.'

            # juntando as frases digitadas manualmente com as frases do arquivo
            text = text + '\n' + file_text
            # dividindo o texto inteiro em frases
            sentences = re.split(r'(?<=[.!?])\s*(?=\w)', text)

            # realizando a análise de sentimentos em inglês
            sentiment_results = []
            for sentence in sentences:
                sentiment_scores = sia.polarity_scores(sentence)
                # calculando a polaridade do texto usando o nltk
                polarity = round(sentiment_scores['compound'], 2)

                # calculando a subjetividade do texto usando o textblob
                blob = TextBlob(sentence)
                subjectivity = round(blob.sentiment.subjectivity, 2)

                sentiment_label = get_sentiment_label(polarity)
                # juntando todos os resultados em uma lista
                sentiment_results.append((sentence, polarity, subjectivity, sentiment_label))
            show_results = True

            # chamando a função para sumarizar os resultados
            summary_stats = summarize_results(sentiment_results)

            # tradução inversa das frases em inglês para o português para facilitar a leitura
            for sentence, polarity, subjectivity, sentiment_label in sentiment_results:
                translated_sentence = translator.translate(sentence, src='en', dest='pt').text
                translated_results.append((translated_sentence, polarity, subjectivity, sentiment_label))

            # armazenando resultados da análise na variável de sessão
            session['translated_results'] = translated_results
            session['summary_stats'] = summary_stats

        # renderizando o resultado numa string
        result_html = render_template('result.html', translated_results=translated_results,
                                      summary_stats=summary_stats)

        # salvando o resultado em um arquivo
        with open('../output.txt', 'w', encoding='utf-8') as output_file:
            for sentence, polarity, subjectivity, sentiment_label in translated_results:
                sentence = sentence.strip()
                output_file.write(f'Frase: {sentence}\n')
                output_file.write(f'Polaridade: {polarity}\n')
                output_file.write(f'Subjetividade: {subjectivity}\n')
                output_file.write(f'Classificação de Sentimento: {sentiment_label}\n')
                output_file.write('\n')

            # escrevendo estatísticas resumidas no arquivo
            output_file.write(f'Estatísticas Resumidas:\n')
            for stat, value in summary_stats.items():
                output_file.write(f'{stat}: {value}\n')
            output_file.write('\n')

        return render_template('index.html', show_results=show_results, result_html=result_html)

    except Exception as e:
        # tratamento de erro
        error_message = f"Erro durante a análise de sentimento: {str(e)}"
        return render_template('error.html', error_message=error_message)
