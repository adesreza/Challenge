import re
import pandas as pd
import string
import sqlite3
import os

from flask import Flask, jsonify

from flask import request
import flask
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
from nltk.tokenize import RegexpTokenizer

class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

current_directory = os.path.dirname(os.path.abspath(__file__))


app = CustomFlaskAppWithEncoder(__name__)

swagger_template = dict(
    info = {
        'title' : LazyString(lambda: "API Documentation for Data Processing and Modeling"),
        'version' : LazyString(lambda: "1.0.0"),
        'description' : LazyString(lambda: "Dokumentasi API untuk Data Processing dan Modeling"),
    },
    host = LazyString(lambda: request.host)
)


swagger_config = {
    "headers" : [],
    "specs" : [
        {
            "endpoint": "docs",
            "route" : "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config = swagger_config)


def Clean (text):
        text = re.sub(r'USER',' ', text)
        text = re.sub (r'RT',' ' , text)
        text = re.sub (r'URL',' ' , text)
        text = re.sub (r'\\[a-zA-Z0-9]+',' ' , text)
        text = re.sub (r'[0-9]',' ' , text)
        text = ''.join([char for char in text if char not in string.punctuation])

        text = text.lower ()

        return text

def tokenize (regexp) :
        regexp = RegexpTokenizer(r'\w+|$[0-9]+|\S+')

def normalized_term (document) :
        normalized_word_dict={}
        for index, row in normalized_word.iterrows():
            if row [0] not in normalized_word_dict :
                normalized_word_dict[row[0]] = row [1]

        return [normalized_word_dict[term] if term in normalized_word_dict else term for term in document] 

@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    text = request.form['text']

    conn = sqlite3.connect(current_directory + "\data\Text_Processing.db")
    cursor = conn.cursor()

    query1 = "INSERT INTO Tweet VALUES ('{t}')".format(t=text)
    cursor.execute(query1)


    query2 = "INSERT INTO Tweet_Clear VALUES ('{t}')".format(t=text)
    cursor.execute(query2)

    conn.commit()


    json_response = {
        'status_code': 200,
        'description': "Teks Clear",
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', text),
    }

    response_data = jsonify(json_response)
    return response_data



@swag_from("docs/text_cleansing.yml", methods = ['POST'])
@app.route('/text-cleansing', methods=['POST'])
def text_cleansing():

    file = request.files['file']

    conn = sqlite3.connect(current_directory + "\data\Text_Cleaning.db")

    file_read = pd.read_csv(file, encoding = 'latin1')

    df_file_read = pd.DataFrame(file_read[['Tweet',]])

    df_file_read.to_sql('Tweet_CSV', conn, if_exists='append', index = False)

    df_file_read['Tweet_Clear'] = df_file_read['Tweet'].apply(lambda x: Clean(x))

    df_file_read.to_sql('Tweet_CSV_Clear', conn, if_exists='append', index = False)


    json_response = {
        'status_code': 200,
        'description': "Teks Cleansing",
        'data': 'Process Success',
    }

    response_data = jsonify(json_response)
    return response_data


@swag_from("docs/text_cleansing.yml", methods = ['POST'])
@app.route('/text-tokenize', methods=['POST'])
def text_tokenize():

    file = request.files['file']

    conn = sqlite3.connect(current_directory + "\data\Text_Cleaning.db")

    file_read = pd.read_csv(file, encoding = 'latin1')

    df_file_read_tk = pd.DataFrame(file_read[['Tweet',]])

    df_file_read_tk.to_sql('Tweet_CSV', conn, if_exists='append', index = False)

    df_file_read_tk ['Token'] = df_file_read_tk ['Tweet'].apply(lambda x: Clean(x))

    df_file_read_tk.to_sql('Tweet_CSV_Token', conn, if_exists='append', index = False)

    json_response = {
        'status_code': 200,
        'description': "Teks Tokenize",
        'data': 'Process Success',
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_cleansing.yml", methods = ['POST'])
@app.route('/text-normalized', methods=['POST'])
def text_normalized():

    file = request.files['file']

    conn = sqlite3.connect(current_directory + "\data\Text_Cleaning.db")

    file_read = pd.read_csv(file, encoding = 'latin1')

    df_file_read_nr = pd.DataFrame(file_read[['Tweet',]])

    df_file_read_nr.to_sql('Tweet_CSV', conn, if_exists='append', index = False)

    df_file_read_nr ['Normalisasi'] = df_file_read_nr ['Tweet'].apply(lambda x: Clean(x))

    df_file_read_nr.to_sql('Tweet_CSV_Normal', conn, if_exists='append', index = False)

    json_response = {
        'status_code': 200,
        'description': "Teks Normalized",
        'data': 'Process Success',
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()