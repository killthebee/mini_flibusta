import requests as r
from bs4 import BeautifulSoup

def download_page(page_url):
    url = 'http://tululu.org/b1/'
    response = r.get(page_url)
    response.raise_for_status()
    return response.text

# title_tag = soup.find('main').find('header').find('h1')
# title_text = title_tag.text
# print(title_text)
# print(soup.find('img', class_='attachment-post-image size-post-image wp-post-image')['src'])

print(soup.find('h1').text)
book_title, book_author = soup.find('h1').text.split('   ::   ')
print(book_title, book_author)

def fetch_title_and_author():
    page = download_page()
    soup = BeautifulSoup(page, 'lxml')
    book_title, book_author = soup.find('h1').text.split('   ::   ')
    return book_title, book_author