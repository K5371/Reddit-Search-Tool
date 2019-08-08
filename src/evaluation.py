import metapy
import os
from search_engine import Searcher

yes_input = {'yes', 'y', '1'}
no_input = {'no', 'n', '0'}

def modify_query_file(netid, query):
    """
    Adds the query to the appropriate file defined by netid
    Updates the total number of queries in file located on line 1
    returns the query number 
    """
    query_file = 'evaluation/' + netid + '_queries.txt'
    
    query_num = 1
    try:
        with open(query_file, 'r+') as f:
            lines = f.readlines()
            query_num = int(lines[0])
            query_num += 1
            
            lines[0] = str(query_num) + '\n'
            lines.append(query + '\n')
            
            f.seek(0)
            f.writelines(lines)
    except FileNotFoundError:
        # Create a new file
        with open(query_file, 'w') as f:
            lines = ['1\n', query + '\n']
            f.writelines(lines)
    return query_num

def modify_evaluation_file(netid, query_num, relevant_docs):
    """
    Adds the relevant documents for a query to the file defined by netid
    Lines are of the form 'query_num doc_id 1'
    returns nothing
    """
    evaluation_file = 'evaluation/' + netid + '_evals.txt'
    
    with open(evaluation_file, 'a') as f:
        lines = []
        
        for doc in relevant_docs:
            lines.append(str(query_num) + ' ' + str(doc) + ' 1\n')
        f.writelines(lines)

def write_evals(netid, query, relevant_docs, directory='evaluation'):
    """
    Makes a directory to put the evaluation files in if it does not exist
    
    Creates two files:
        netid_queries.txt - contains the queries made
        netid_evals.txt - contains the doc id of the relevant documents to the query
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    query_num = modify_query_file(netid, query)
    modify_evaluation_file(netid, query_num, relevant_docs)

def evaluate(netid='', cfg='config.toml', top_k=10):
    """
    Create evaluation data for a ranker
    netid: str - used to create unique files
        netid_queries.txt
        netid_evals.txt
    cfg: str - defines the path to the config file to use
    top_k: int - defines the number of documents to rank
    
    return - nothing
    """
    
    if netid == '':
        netid = input('Please enter your netid: ')
    query = input('Please enter your query: ')
    relevant_docs = []
    
    searcher = Searcher(cfg)
    results = searcher.search(query, top_k=top_k)
    
    print('Please decide whether the result is relevant. (Y/N)')
    for res in results:
        print(res['url'])
        
        input_valid = False
        
        while (not input_valid):
            relevance = input('Is this result relevant? ').lower()
            if relevance in yes_input:
                relevant_docs.append(res['doc_id'])
                input_valid = True
            elif relevance in no_input:
                input_valid = True
            else:
                print('Unidentified input, please try again.')
        print('')
    write_evals(netid, query, relevant_docs)
    
def merge_evaluation_files(netid, master_prefix='uiuc'):
    """
    Merge the evaluation files defined by netid to the one defined by master_prefix
    """
    
    m_query_file = 'evaluation/' + master_prefix + '_queries.txt'
    m_eval_file = 'evaluation/' + master_prefix + '_evals.txt'
    
    target_query_file = 'evaluation/' + netid + '_queries.txt'
    target_eval_file = 'evaluation/' + netid + '_evals.txt'
    
    # Create master files if not exists
    if not os.path.isfile(m_query_file):
        open(m_query_file, 'w').close()
    if not os.path.isfile(m_eval_file):
        open(m_eval_file, 'w').close()
    
    # Just gets the number of queries in master
    with open(m_query_file, 'r') as f:
        m_num_queries = sum(1 for line in f)

    with open(target_query_file, 'r') as f:
        query_lines = f.readlines()
    
    # Assumes first line of target query file is the number of queries
    with open(m_query_file, 'a') as f:
        f.writelines(query_lines[1:])
        
    with open(target_eval_file, 'r') as f:
        eval_lines = f.readlines()
    
    m_eval_lines = []
    
    # Need to update the query number in the eval master file
    for line in eval_lines:
        evaluation = line.split(' ')
        query_num = int(evaluation[0])
        evaluation[0] = str(query_num + m_num_queries)
        m_eval_lines.append(" ".join(evaluation))
    
    with open(m_eval_file, 'a') as f:
        f.writelines(m_eval_lines)
    
if __name__ == "__main__":
    # Run this file to make evaluations
    netid = ''
    cfg = 'config.toml'
    top_k = 10
    evaluate(netid, cfg, top_k)