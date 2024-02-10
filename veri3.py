import requests
from bs4 import BeautifulSoup
from datasets import Dataset
import re
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_page_data(session, url, page, class_name, count):
    """
        get all text from the urls in the given web page
    """
    full_url = f'{url}{page}'
    try:
        r = session.get(full_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup.find('div', class_=class_name).find_all('a')
        logging.info(f'New page link: {full_url}')
        print(f'New page link: {full_url}')
        
    except Exception as e:
        logging.error(f'Error connecting to {full_url}: {e}')
        return [], count

    articles = []
    for link in links:
        href = link.get('href')
        if href:
            try:
                link_response = session.get(href)
                link_soup = BeautifulSoup(link_response.content, 'html.parser')
                
            except Exception as e:
                logging.error(f'Error connecting to {href}: {e}')
                continue

            article_body = link_soup.find('p', itemprop='articleBody')
            if article_body:
                text = article_body.text.strip()
                articles.append(text)
                
            else:
                content_div = link_soup.find('div', id='content')
                if content_div:
                    text = content_div.text.strip()
                    text = re.sub(r'\*\*\*', '', text)
                    articles.append(text)
                    
            logging.info(f'Processing article {count}: {href}')
            print(f'Processing article {count}: {href}')
            count += 1

    return articles, count


def get_all_data(url, class_name, page_prefix, page_count):
    """
        get authors all texts and store them
    """
    all_data = []
    
    with requests.Session() as session:
        count = 1
        for i in range(1, page_count + 1):
            page_data, count = get_page_data(session, url, f'{page_prefix}{i}', class_name, count)
            all_data.extend(page_data)
            
    return all_data


def save_data(author, data):
    """
        save collected data to disk as datasetDict
    """
    article_count = len(data)
    author_len = [author] * article_count
    author_dataset = Dataset.from_dict({'author': author_len, 'writing': data})
    path = f"data/{author}_dataset"
    author_dataset.save_to_disk(path)


if __name__ == '__main__':

    authors_pages = {
        'hincal-uluc': 417,
        'omer-urundul': 205
    }
    
    for author, page_count in authors_pages.items():
        url = f"https://www.koseyazisioku.com/sabah/{author}"
        class_name = 'yazaryazilari'
        page_prefix = '?s='
        all_pages_data = get_all_data(url, class_name, page_prefix, page_count)
        save_data(author, all_pages_data)
