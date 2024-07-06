from bs4 import BeautifulSoup
from langchain_community.document_loaders import DocusaurusLoader
import nest_asyncio
import os
import requests
import html2text
import time
from ragapp import *

nest_asyncio.apply()

gls = [
    'https://www.rustore.ru/help/users/',
    'https://www.rustore.ru/help/developers/',
    'https://www.rustore.ru/help/sdk/',
    'https://www.rustore.ru/help/work-with-rustore-api/',
    'https://www.rustore.ru/help/guides/',
]


def getAllLinks(gls):
    all_links = []
    for global_link in gls:
        loader = DocusaurusLoader(
            "https://www.rustore.ru/help",
            filter_urls=[
                global_link
            ],
            # This will only include the content that matches these tags, otherwise they will be removed
            custom_html_tags=["#content", ".main"],
        )
        # Загрузка всех документов
        documents = loader.load()
        links = [doc.metadata['source'] for doc in documents]
        all_links += links
    return all_links


def save_page_to_markdown(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup_ = BeautifulSoup(response.text, 'html.parser')
    soup = soup_.find_all(['article'])
    h1tag = soup_.find_all(itemprop='name')
    # Найти все изображения и добавить префикс к их src атрибутам
    images = soup_.find_all('img')
    for img in images:
        original_src = img['src']
        if not original_src.startswith('http'):
            img['src'] = 'https://www.rustore.ru/' + original_src

    html_content = str(soup)

    str_ = " ".join([tag.text for tag in h1tag])

    # Конвертация HTML в Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    markdown_content = h.handle(html_content)

    content = f"""url: {url}\ntitle: {str_}\n\n"""
    markdown_content = content + markdown_content
    filename = url.split('help')[1][1:].replace('/', '-') + '.txt'

    with open(os.path.join('../markdown_files', filename), 'w', encoding='utf-8') as file:
        file.write(markdown_content)

    text_db = None
    db_result = db.get_conv(filename)
    if len(db_result) != 0:
        text_db = db_result[-1][-1]

    # Если есть изменения какие-то
    if not compare(
            text=markdown_content,
            db_text=text_db,
    ):
        db.delete_cond(filename)
        db.add_text(
            text=markdown_content,
            filename=filename
        )
        flow.del_files(filename)
        flow.add_file(os.path.join('../markdown_files', filename))


def md_files(all_links):
    os.makedirs('../markdown_files', exist_ok=True)
    for index, url in enumerate(all_links):
        save_page_to_markdown(url)
        print(f'Executing file №{index} url: {url}')
        time.sleep(0.5)

