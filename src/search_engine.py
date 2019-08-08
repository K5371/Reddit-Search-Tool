import metapy
import sys
import os
import time
scraper_path = os.path.abspath('../scraper')
sys.path.append(scraper_path)
import scraper

def format_time(epoch_time):
    """
    Transforms an epoch timestamp to Y-M-D H:M:S string format
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(epoch_time)))
    return str(date)

class Searcher:
    """
    Wrapper for MetaPy Search Engine
    """
    def __init__(self, cfg):
        """
        cfg - str: path to config file to build inverse index
        """
        self.idx = metapy.index.make_inverted_index(cfg)

    def search(self, query_str, ranker=metapy.index.OkapiBM25(), top_k=10, start_time='', end_time='', sorting_type='date'):
        """
        Makes a query against the current inverse index with the specified ranker.
        If start_time and end_time are defined, then returned results are in that time frame
        query_str - str: query
        ranker - metapy.index object
        top_k - int: how many results to return
        start_time - string in epoch form
        end_time - string in epoch form
        sorting_type - str: either sort in reverse by 'date' or 'upvotes'
        return: list of dictionaries sorted by sorting_type
                content - str: content of post
                url - str: url of post
                doc_id - int: id of post in inv index
                date - str: date of post in Y-M-D H:M:S format
                upvotes - int: number of upvotes of post
        """
        query = metapy.index.Document()
        query.content(query_str.strip())

        results = ranker.score(self.idx, query, top_k)
        documents = []

        for doc_id, score in results:
            doc = self.idx.metadata(doc_id)
            
            add_doc = True
            
            # Check if doc needs to be within time frame
            if start_time != '' and end_time != '':
                if not self.is_doc_in_time_frame(doc_id, start_time, end_time):
                    add_doc = False

            date_str = format_time(doc.get('date'))

            if add_doc:
                documents.append({
                    'content': doc.get('content'),
                    'url': doc.get('url'),
                    'doc_id': doc_id,
                    'date': date_str,
                    'upvotes': doc.get('upvotes'),
                })

        documents.sort(key=lambda doc: doc.get(sorting_type), reverse=True)

        return documents

    def is_doc_in_time_frame(self, doc_id, start_time, end_time):
        """
        Determines whether the document is in the time frame
        """
        doc_date = float(self.idx.metadata(doc_id).get('date'))
        return doc_date >= float(start_time) and doc_date <= float(end_time)
    