# importando todas as bibliotecas necessárias
import nltk
import docx2txt
import pandas as pd
import re
import enchant

from PyPDF2 import PdfReader
from werkzeug.datastructures import FileStorage
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask import Flask, request, render_template, send_file, jsonify, session, redirect, url_for
from googletrans import Translator

nltk.download('vader_lexicon')
nltk.download('punkt')


