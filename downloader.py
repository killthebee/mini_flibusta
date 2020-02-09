import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filepath
from urllib.parse import urljoin


def download_txt(filename, book_id):
    url = 'http://tululu.org/txt.php?id=%s'%(book_id)

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    print(response)
    if response.status_code != 302:
        with open(filename, 'w') as file:
            file.write(response.text)


def create_directory(root_dir, name):
    books_dir = root_dir / name
    Path(books_dir).mkdir(exist_ok=True)
    return books_dir


def d_10():
    frst_book_id = 32168
    new_book_ids = [frst_book_id + add for add in range(0,10)]
    for counter, book_id in enumerate(new_book_ids, 1):
        download_book(book_id, counter)


def download_page(book_id):
    url = 'http://tululu.org/b%s/'%(book_id)
    response = requests.get(url)
    response.raise_for_status()
    return response.text, url


def fetch_title_and_author(book_id):
    page, url = download_page(book_id)
    soup = BeautifulSoup(page, 'lxml')
    book_title, book_author = soup.find('h1').text.split('   ::   ')
    return book_title


def make_filename(books_dir, book_id, prefix):
    book_title = fetch_title_and_author(book_id)
    sanitized_book_title = sanitize_filepath('%s.%s'%(book_title, prefix))
    print('dir')
    print(books_dir)
    print('title')
    print(sanitized_book_title)
    filename = books_dir / sanitized_book_title
    print(filename)
    return filename


def download_image(filename, book_id):
    page, page_url = download_page(book_id)
    soup = BeautifulSoup(page, 'lxml')
    short_url = soup.find('div', class_="bookimage").find('img')['src']
    full_url = urljoin(page_url, short_url)
    response = requests.get(full_url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def download_comments():
    page, page_url = download_page()
    soup = BeautifulSoup(page, 'lxml')
    comments = soup.find_all('div', class_='texts')
    for com in comments:
        print(com.find('span').text)


def fetch_genre():
    page, page_url = download_page()
    soup = BeautifulSoup(page, 'lxml')
    links_to_genre = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in links_to_genre]



book_id = 12
root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
books_dir = create_directory(root_dir, 'images')
filename = make_filename(books_dir, book_id, 'jpg')
download_image(filename, book_id)