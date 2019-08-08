from flask import Flask, request, render_template
from gevent.pywsgi import WSGIServer
import sys
import os
import training
import metapy
import time
import datetime

from search_engine import Searcher

app = Flask(__name__)

@app.route("/")
def home():
    """
    Render homepage
    """
    return render_template('index.html')

@app.route("/search", methods = ['POST'])
def search():
    """
    Make a search against the current index
    """
    query = request.form['query']
    startDate = request.form['startDate']
    endDate = request.form['endDate']
    sorting_type = request.form['sortingType']

    if startDate != '' and endDate != '':
        startTime = time.mktime(datetime.datetime.strptime(startDate, "%Y-%m-%d").timetuple())
        endTime = time.mktime(datetime.datetime.strptime(endDate, "%Y-%m-%d").timetuple())
        # Add a day's worth of seconds
        endTime += 60*60*24
    else:
        startTime = ''
        endTime = ''

    ranker = training.load_ranker('best')
    if ranker is None:
        ranker = metapy.index.OkapiBM25()

    docs = app.searcher.search(query, ranker, start_time=startTime, end_time=endTime, sorting_type=sorting_type)
    return render_template('posts_display.html', documents=docs, start_time=startTime, end_time=endTime, sorting_type=sorting_type)

if __name__ == "__main__":
    app.searcher = Searcher('config.toml')
    '''
    If on linux, use the two http_sever lines
    Otherwise, use app.run()
    '''
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

    #app.run()

