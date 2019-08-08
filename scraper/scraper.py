import urllib.request as ur
import json
import time
import calendar
from bs4 import BeautifulSoup as BS
import re

def build_api_request_url(base_url, after, before, sort_type, sort, subreddit, size):
    """
    Builds and returns pushshift.io API request url from given parameters.
    """
    return base_url+'after='+str(after)+'&before='+str(before)+'&sort_type='+sort_type+'&sort='+sort+'&subreddit='+subreddit+'&size='+str(size)

def get_creation_datetime(subreddit):
    """
    Scrapes subreddit home page to get the exact creation datetime.
    Returns creation datetime as an epoch timestamp.
    subreddit: str - subreddit to scrape for creation datetime
    """
    req = ur.Request("https://old.reddit.com/r/"+subreddit)
    html = ''
    connected = False
    # Keep trying to scrape subreddit until connection doesn't fail
    while not connected:
        try:
            res = ur.urlopen(req)
            html = res.read()
            res.close()
            connected = True
        except:
            time.sleep(.05)

    # Use BeautifulSoup to find the tag where creation datetime is stored
    soup = BS(html, "html.parser")
    time_tag = soup.find('time')
    creation_time = time_tag['datetime']
    formatted_time = creation_time.split('+')[0].replace('T', ' ')
    pattern = '%Y-%m-%d %H:%M:%S'
    utc_epoch = calendar.timegm(time.strptime(formatted_time, pattern))
    return utc_epoch

def scrape_data_from_to(api_base_url, sort_type, sort, subreddit, size, start, end):
    """
    Gets all posts on a subreddit between start and end timestamp
    Gathers metadata associated with each post
    Returns two lists, one containing posts and one containing metadata, with each item on a new line
    api_base_url: str - pushshift.io base_url
    sort_type: str - determines how posts are sorted
    sort: str - determines if sort is ascending or descending
    subreddit: str - subreddit to scrape
    size: int - how many posts to get with one API call
    start: int - beginning timestamp of period to scrape
    end: int - end timestamp of period to scrape
    """
    after = start
    before = end
    post_texts = []
    meta_data = []
    done = False
    # Gathers first 500 posts, then moves start up to last of those 500 posts and repeats
    while after <= end and not done:
        api_url = build_api_request_url(api_base_url, after, before, sort_type, sort, subreddit, size)
        req = ur.Request(api_url)
        res = ur.urlopen(req)
        data = res.read()
        json_data = json.loads(data)
        res.close()
        print('len', len(json_data['data']), api_url)
        last_end = 0
        if len(json_data['data']) == 0:
            done = True
        for post in json_data['data']:
            single_post_text = post['title'] + ' '
            try:
                single_post_text += post['selftext']
            except:
                continue
            post_texts.append(process_text(single_post_text))
            meta_data.append(post['full_link'] + '\t' + str(post['created_utc']) + '\t' + str(post['score']))
            last_end = post['created_utc']
        after = last_end
    return post_texts, meta_data

def process_text(text):
    """
    Removes non-ascii characters and repeated whitespace characters from text
    From https://lab.textdata.org/cs410-sp19/MP2/blob/master/sample/scraper.ipynb
    """
    text = text.encode('ascii',errors='ignore').decode('utf-8')
    text = re.sub('\s+',' ',text)
    return text

def write_lst(lst,file_):
    """
    Writes lst to a file with name file_, with each list item on a new line
    From https://lab.textdata.org/cs410-sp19/MP2/blob/master/sample/scraper.ipynb
    """
    with open(file_, 'w', encoding='utf-8') as f:
        for l in lst:
            f.write(l)
            f.write('\n')

if __name__ == "__main__":
    # Set parameters that we desire for scraping a subreddit
    subreddit = 'UIUC'
    api_base_url = 'https://api.pushshift.io/reddit/submission/search/?'
    start_date = get_creation_datetime(subreddit) #Very beginning of subreddit
    end_date = int(time.time()) #Now
    sort_type = 'created_utc'
    sort = 'asc'
    size = 500

    # Scrape posts and create lists of posts and metadata
    post_texts, meta_data = scrape_data_from_to(api_base_url, sort_type, sort, subreddit, size, start_date, end_date)

    # Write these two lists to their respective files
    text_file = 'r_' + subreddit + '.dat'
    meta_data_file = 'metadata.dat'
    write_lst(post_texts, text_file)
    write_lst(meta_data, meta_data_file)
