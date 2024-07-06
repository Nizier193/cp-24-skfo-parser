from parser_filer.globalparser import (
    getAllLinks,
    gls,
    md_files,
)

'''
Здесь происходит парсинг всех ссылок с сайта.

Главные 5 ссылок - gls. Здесь все ссылки, которые ведут
к остальным сайтам.

Далее md_files - сохранение всех спаршенных файлов в .md
Здесь выполняется сравнение файлов из бд и файлов в системе.
'''

all_links = getAllLinks(gls)
md_files(all_links)

###