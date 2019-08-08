import metapy
import os


def evaluate_ranker(ranker, cfg='config.toml', top_k=10, query_path='evaluation/uiuc_queries.txt', query_start=1):
    """
    Evaluates the current ranker with the training data
    query_path: str - path to the queries to evaluate on
    query_start: int - which query to start with

    return: int - mean average precision of ranker
    """
    idx = metapy.index.make_inverted_index(cfg)
    query = metapy.index.Document()
    ev = metapy.index.IREval(cfg)


    #Evaluation code from MP2-Part 2
    with open(query_path, 'r') as query_file:
        for query_num, line in enumerate(query_file):
            query.content(line.strip())
            results = ranker.score(idx, query, top_k)
            avg_p = ev.avg_p(results, query_start + query_num, top_k)

    return ev.map()


def train_bm25_ranker(cfg='config.toml', top_k=10, query_path='evaluation/uiuc_queries.txt'):
    """
    Trains the Okapi BM25 ranker based on the training data.
    Since there are 3 params, this method only finds the optimal param along each dimension separately
    Assumes a directory called training exists
    Writes the results to training/okapi_bm25_ranker_params.txt in "map, k1, b, k3" order on separate lines

    cfg - str: path to config file
    top_k - int: how many results to compare
    query_path - str: path to query file
    returns - list of best map, k1, b, k3 in that order
    """
    #Default values
    best_k1 = 1.2
    best_b = 0.75
    best_k3 = 500.0
    best_map = evaluate_ranker(metapy.index.OkapiBM25(), cfg, top_k, query_path)

    for k1 in [0.1 * x for x in range(1, 21)]:
        ranker = metapy.index.OkapiBM25(k1=k1, b=best_b, k3=best_k3)
        map_score = evaluate_ranker(ranker, cfg, top_k, query_path)
        if map_score > best_map:
            best_map = map_score
            best_k1 = k1

    for b in [0.1 * x for x in range(1, 21)]:
        ranker = metapy.index.OkapiBM25(k1=best_k1, b=b, k3=best_k3)
        map_score = evaluate_ranker(ranker, cfg, top_k, query_path)
        if map_score > best_map:
            best_map = map_score
            best_b = b

    for k3 in [100 * x for x in range(0, 11)]:
        ranker = metapy.index.OkapiBM25(k1=best_k1, b=best_b, k3=k3)
        map_score = evaluate_ranker(ranker, cfg, top_k, query_path)
        if map_score > best_map:
            best_map = map_score
            best_k3 = k3

    file_name = 'training/okapi_bm25_ranker_params.txt'
    lines = [str(best_map) + '\n', str(best_k1) + '\n', str(best_b) + '\n', str(best_k3) + '\n']
    with open(file_name, 'w') as f:
        f.writelines(lines)

    return [best_map, best_k1, best_b, best_k3]


def load_best_bm25_ranker():
    """
    Loads a BM25 ranker with the params found in train_bm25_ranker if the file exists
    Otherwise, return None
    """
    if os.path.isdir('training') and os.path.isfile('training/okapi_bm25_ranker_params.txt'):
        with open('training/okapi_bm25_ranker_params.txt', 'r') as f:
            lines = f.readlines()
        k1 = float(lines[1].strip('\n'))
        b = float(lines[2].strip('\n'))
        k3 = float(lines[3].strip('\n'))
        return metapy.index.OkapiBM25(k1=k1, b=b, k3=k3)
    else:
        return None


def train_jelinek_mercer_ranker(cfg = 'config.toml', top_k = 10, query_path = 'evaluation/uiuc_queries.txt'):
    """
    Trains the Jelinek Mercer ranker based on the training data.
    Assumes a directory called training exists
    Writes the results to training/jelinek_mercer_ranker_params.txt in "map, lambda" order on separate lines

    cfg - str: path to config file
    top_k - int: how many results to compare
    query_path - str: path to query file
    returns - list of best map, lambda in that order
    """
    #Default value
    lam = 0.7
    best_map = evaluate_ranker(metapy.index.JelinekMercer(), cfg, top_k, query_path)
    for lbda in [0.1 * x for x in range(1,10)]:
        ranker = metapy.index.JelinekMercer(lbda)
        map_score = evaluate_ranker(ranker, cfg, top_k, query_path)
        if map_score > best_map:
            best_map = map_score
            lam = lbda
    file_name = 'training/jelinek_mercer_ranker_params.txt'
    lines = [str(best_map) + '\n', str(lam) + '\n']
    with open(file_name, 'w') as f:
        f.writelines(lines)
    return [best_map, lam]


def load_best_jelinek_mercer_ranker():
    """
    Loads a Jelinek Mercer ranker with the params found in jelinek_mercer_ranker_params if the file exists
    Otherwise, return None
    """
    if os.path.isdir('training') and os.path.isfile('training/jelinek_mercer_ranker_params.txt'):
        with open('training/jelinek_mercer_ranker_params.txt', 'r') as f:
            lines = f.readlines()
        lam = float(lines[1].strip('\n'))
        return metapy.index.JelinekMercer(lam)
    else:
        return None

def best_ranker():
    """
    Trains both rankers with the same training data set and generates a map score for each ranker
    Selects the ranker with the best mean average precision
    """
    bm25_map = 0.0
    jemin_map = 0.0
    if os.path.isdir('training') and os.path.isfile('training/okapi_bm25_ranker_params.txt'):
        with open('training/okapi_bm25_ranker_params.txt', 'r') as f:
            lines = f.readlines()
        bm25_map = float(lines[0].strip('\n'))
    if os.path.isdir('training') and os.path.isfile('training/jelinek_mercer_ranker_params.txt'):
        with open('training/jelinek_mercer_ranker_params.txt', 'r') as f:
            lines = f.readlines()
        jemin_map = float(lines[0].strip('\n'))
    if bm25_map > jemin_map:
        return load_best_bm25_ranker()
    else:
        return load_best_jelinek_mercer_ranker()

def load_ranker(id = 'best'):
    if id == 'bm25':
        return load_best_bm25_ranker()
    if id == 'jelink':
        return load_best_jelinek_mercer_ranker()
    if id == 'best':
        return best_ranker()
    return None


if __name__ == "__main__":
    if not os.path.isdir('training'):
        os.makedirs('training')
    train_bm25_ranker()
    train_jelinek_mercer_ranker()