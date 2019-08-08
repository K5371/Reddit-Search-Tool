## CS410-Reddit-Search-Tool
This is a search engine meant to be an improvement over Reddit's current engine. Some of the shortcomings with Reddit's search tool are that each word in the query must exactly match to a post in order to retrieve it and the user cannot specify specific timeframes to search within, two features that we have implemented in our tool.

There are two main parts to the code, the frontend housed in search_server.py and the backend, search_engine.py.

The frontend uses Flask, a Python micro web framework, to take queries and server results. Currently, there are two pages that it serves, the home page where a user can make a query and the results page that displays the relevant posts. It also acts as the controller in MVC, taking the user's query, sort type, and date interval and passing it to the backend and then taking the results and displaying them.

The backend uses MeTAPy to support making queries. The class Searcher is a wrapper for MeTAPy's search engine functions. It requires a config.toml file to initialize its inverse index. The search function is extremely customizable, from what ranker to use, to specifying the order the results should be returned in.

In addition to these two files, there are also a few helper functions we built to assit in searching.

scraper.py in the scraper folder is responsible for retrieving posts from Reddit along with its associated metadata. We used r/uiuc as test data, but it can be extended to any subreddit.

evaluation.py helped us create training data for our rankers. Running the file itself allows one to judge the returned documents to a specified query as relevant or not. The results are stored in the evaluation folder

traning.py allows us to train rankers. We have currently implemented BM25 and Jelinek-Mercer, but this can be easily extended to other rankers as well. Running the file trains the two rankers on the current training data and stores the mean avg percision and params for each ranker in the training folder.

**Getting Started**  
We had some issues getting Flask to work with our computers. It works with some of our Windows systems, but not others, so we recommend using the Linux environment as that has consistently worked, but we will provide instructions for both.

For Windows:
1. Make sure you're in the root directory.
2. Activate the environment with: 
". venv/bin/activate" (without quotes)
3. Install the packages needed: flask, metapy, gevent, etc.
4. Navigate to src
5. Run search_server.py
6. The default web address is 127.0.0.1:5000
7. Specify the date interval, sort interval, and make your query

For Linux
1. Make sure you're in the root directory
2. Run these two commands to create a virtual environment:  
  virtualenv -p /usr/bin/python3 py3env  
  source py3env/bin/activate
3. Install the packages needed: flask, metapy, gevent, etc.
4. Navigate to src
5. Edit search_server.py. At the very bottom, there are two commented out lines dealing with http_server. Uncomment them and comment out app.run()
6. Now run search_server.py
7. The default web address is 127.0.0.1:5000
8. Specify the date interval, sort interval, and make your query
