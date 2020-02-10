import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filepath
from urllib.parse import urljoin
import json
import argparse


def download_txt(filepath, book_id):
    url = 'http://tululu.org/txt.php?id=%s'%(book_id)

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 200:
        with open(filepath, 'w') as file:
            file.write(response.text)


def create_directory(root_dir, name):
    dir_path = root_dir / name
    dir_path.mkdir(exist_ok=True)
    return dir_path


def download_pagesoup(book_id):
    url = 'http://tululu.org/b%s/'%(book_id)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def make_filepath(path_to_dir, extension, book_title):
    sanitized_book_title = sanitize_filepath('%s.%s'%(book_title, extension))
    filepath = path_to_dir / sanitized_book_title
    return filepath


def download_image(soup, filepath, book_id):
    page_url = 'http://tululu.org/b%s/'%(book_id)
    img_selector = 'div.bookimage img'
    short_url = soup.select_one(img_selector)['src']
    full_url = urljoin(page_url, short_url)
    response = requests.get(full_url)
    response.raise_for_status()

    with open(filepath, 'wb') as file:
        file.write(response.content)


def fetch_book_ids(start_page, end_page):
    urls = ['http://tululu.org/l55/%s'%(page) for page in range(start_page, end_page + 1)]
    book_ids = []
    for url in urls:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        book_cards_selector = 'table.d_book'
        book_cards = soup.select(book_cards_selector)
        for card in book_cards:
            book_short_url = card.select_one('a')['href']
            book_id = book_short_url[2:]
            book_ids.append(book_id)

    return book_ids


def main():
    root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    books_dir_path = create_directory(root_dir, 'books')
    images_dir_path = create_directory(root_dir, 'images')

    parser = argparse.ArgumentParser(
        description='Choose start and end page'
    )
    parser.add_argument('-s', '--start_page', help='Start page')
    parser.add_argument('-e', '--end_page', help='End page', default=100000)
    args = parser.parse_args()
    book_ids = fetch_book_ids(int(args.start_page), int(args.end_page))

    books_info = []
    for book_id in book_ids:
        soup = download_pagesoup(book_id)
        book_title, book_author = soup.select_one('h1').text.split('   ::   ')

        text_filepath = make_filepath(books_dir_path, 'txt', book_title)
        download_txt(text_filepath, book_id)
        img_filepath = make_filepath(images_dir_path, 'jpg', book_title)
        download_image(soup, img_filepath, book_id)

        comments_selector = 'div.texts span'
        comments = [comment.text for comment in soup.select(comments_selector)]
        genres_selector = 'span.d_book a'
        genres = [genre.text for genre in soup.select(genres_selector)]

        book_info ={
            "title": book_title,
             "author": book_author,
            "img_src": str(img_filepath),
            "book_path": str(text_filepath),
            "comments": comments,
            "genres": genres,
        }
        books_info.append(book_info)

    with open('books_info.json', 'w') as file:
        json.dump(books_info, file, ensure_ascii=False)


if __name__ == "__main__":
    main()