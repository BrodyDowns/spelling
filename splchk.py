'''
Phonetic Spellchecker implemented in Flask API
'''

import flask
from flask import request, jsonify
import pandas as pd
import stringdist
import numpy as np
import re

app = flask.Flask(__name__)
app.config["DEBUG"] = True

#Read in childrens spelling data
ks = pd.read_csv('data/kidsspellingv2.csv')
ks = ks.drop(['Code', 'Semester'], axis=1)
ks = ks.dropna(subset=['Target', 'Spelling'])
ks["Target"] = ks.Target.apply(lambda x: x.strip())

#reads in word frequency data
word_freq = pd.read_csv('data/word_freq.csv')

#Phonetic rules
rules = [
            (r'[^a-z]', r''),
            (r'([bcdfhjklmnpqrstvwxyz])\1+', r'\1'),
            (r'ck', r'K'),
            (r'^ocea', r'A2'),
            (r'^ae', r'A'),
            (r'^[aeiou]+', r'A'),
            (r'^[gkp]n', r'N'),
            (r'^wr', r'R'),
            (r'^x', r'S'),
            (r'^wh', r'W'),
            (r'^w', r'W'),
            (r'^gh', r'G'),
            (r'mb$', r'M'),
            #(r'(nc)e$', r'NS'),
            #(r'([aeiou][^aeiou])e$', r'\1'),
            #(r'(ng|st|pl|bl|tt|rs|cl)e$', r'\1'),
            (r'(?!^)sch', r'SK'),
            (r'th', r'0'),
            (r'^y', r'Y'),
            (r't?ch',r'1'),
            (r't?sh', r'2'),
            (r'c(?=ia|io)', r'2'),
            (r'ture$', r'1R'),
            (r'[st](?=i[ao])', r'2'),
            (r's?c(?=[iey])', r'S'),
            (r'[q]', r'Q'),
            (r'[c]', r'K'),
            (r'dg(?=[iey])', r'J'),
            (r'd', r'D'),
            (r'g(?=h[^aeiou])', r''),
            #(r'gh$', r''),
            (r'[y]$', r'A'),
            (r'gn(ed)?', r'N'),
            (r'([^g]|^)g(?=[iey])', r'\1G'),
            (r'g+', r'G'),
            (r'ph', r'F'),
            (r'([aeiou])h(?=\b|[^aeiou])', r'\1'),
            (r'[wy](?![aeiou])', r''),
            (r'[aeiou]w', r''),
            #(r'x', r'KS'),
            (r'z', r'S'),
            (r'v', r'V'),
            (r'y', r''),
            #(r'([aiou]+$)', r'A'),
            #(r'([aeiou]+)', r'A')
            (r'(?!^)[aeiou]+', r''),
        ]

#Returns phonetic version of a word
def mphone(word):
    code = word.lower()
    for rule in rules:
        code = re.sub(rule[0], rule[1], code)
    return code.upper()

#Create our dictionary
metaphone_dict = {}
for word in word_freq['word']:
    word = str(word).lower()
    try:
        word_phone = mphone(word)
    except:
        continue
    if word_phone in metaphone_dict:
        metaphone_dict[word_phone].append(word)
    else:
        metaphone_dict[word_phone] = [word]
    
#edit distance
def edit_distance_1(word):
    word = word.lower()
    letters = list('abc1dfghjklmnpqrs2t0vwxyz')
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(transposes + deletes + replaces + inserts)

def metaphone_suggestions(word, count):
    spelling_phone = mphone(word)
    suggestions = []
    if spelling_phone in metaphone_dict:
        suggestions.extend(metaphone_dict[spelling_phone])

    additional_suggestions = []
    for eword in edit_distance_1(spelling_phone):
        if eword.upper() in metaphone_dict:
            additional_suggestions.extend(metaphone_dict[eword.upper()])
    additional_suggestions.sort(key=lambda x: stringdist.levenshtein_norm(x, word))
    #suggestions.sort(key=lambda x: stringdist.levenshtein_norm(x, word))
    suggestions.extend(additional_suggestions)
    
    #return list(dict.fromkeys(suggestions))[0:5]
    suggestions = [sug[0].upper() + sug[1:] if word[0].upper() == word[0] else sug for sug in list(dict.fromkeys(suggestions)) if len(sug) > 1]
    return suggestions[:count]


@app.route('/', methods=['GET'])
def home():
    return "<h1>Spellchecking API</p>"

@app.route('/sgst', methods=['GET'])
def api_id():
    # check get variables
    if 'word' in request.args:
        word = request.args['word']
    else:
        return "Error: No word field provided. Please specify word."
    
    if 'max' in request.args:
        max = int(request.args['max'])
    else:
        max = 5

    # return object
    results = {
        "original": word,
        "suggestions": metaphone_suggestions(word,max)
    }


    # jsonify
    return jsonify(results)

app.run(port='5002')