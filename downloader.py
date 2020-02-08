import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filepath


def download_txt(filename, book_id):
    url = 'http://tululu.org/txt.php?id=%s'%(book_id)

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    print(response)
    if response.status_code != 302:
        with open(filename, 'w') as file:
            file.write(response.text)


def create_directory(root_dir):
    books_dir = root_dir / 'books'
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
    return response.text


def fetch_title_and_author(book_id):
    page = download_page(book_id)
    soup = BeautifulSoup(page, 'lxml')
    book_title, book_author = soup.find('h1').text.split('   ::   ')
    return book_title


def make_filename(books_dir, book_id):
    book_title = fetch_title_and_author(book_id)
    sanitized_book_title = sanitize_filepath('%s.txt'%(book_title))
    print('dir')
    print(books_dir)
    print('title')
    print(sanitized_book_title)
    filename = books_dir / sanitized_book_title
    print(filename)
    return filename


book_id = 12
root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
books_dir = create_directory(root_dir)
filename = make_filename(books_dir, book_id)
download_txt(filename, book_id)