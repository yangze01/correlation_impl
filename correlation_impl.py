#coding=utf8
from flask import Flask, render_template, make_response
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
# import prediction as pre
from search_relation import *
app = Flask(__name__)
app.secret_key = '!@#$%^&*()'
app.config['SESSION_TYPE'] = 'filesystem'
app.debug = False

csv_tuple_path = BasePath + '/csv/csv_tuple_pos_select.csv'
csv_dict_path = BasePath + '/csv/csv_dict_pos_select.csv'
cosearch = CoSearch(csv_tuple_path, csv_dict_path)

@app.route('/correlation', methods = ['GET','POST'])
def correlation():
    if request.method == "POST":
        word = request.form['word']
        # topn = int(request.form['topn'])
    else:
        word = request.args.get('word')
        # topn = int(request.form['topn'])
    # print(word)
    # print(topn)
    res = make_response(jsonify((cosearch.search_word(word.encode('utf8'), topn=5))))
    res.headers['Access-Control-Allow-Origin'] = "*"
    # print(res)
    return res

@app.route('/correlationSentence', methods = ['GET','POST'])
def correlation2():
    if request.method == "POST":
        sentence = request.form['sentence']
        # topn = int(request.form['topn'])
    else:
        sentence = request.args.get('sentence')
        # topn = int(request.form['topn'])
    # print(word)
    # print(topn)
    res = make_response(jsonify((cosearch.get_keywords(sentence.encode('utf8')))))
    res.headers['Access-Control-Allow-Origin'] = "*"
    # print(res)
    return res
@app.route('/', methods = ['GET','POST'])
def index():
    return "hello world!"

if __name__ == '__main__':
    print("begin flask service.")

    app.run(host='0.0.0.0', port=8080)
    # app.run()
