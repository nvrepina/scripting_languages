from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urlparse, urljoin

def write_file(text, file_name):
    try:
        with open(file_name, 'a', encoding='UTF-8') as file:
            file.write(text + '\n')
    except IOError as e:
        print(f"Ошибка записи в файл: {e}")


def get_links(url):
    '''Возвращает все найденные URL'''
    write_file(f"Обрабатываем ссылку {url}", "log.txt")
    urls = set() # все URL-адреса, множество хранит неповторяющиеся значения
    domain = urlparse(url).netloc #домен

    while True:
        try:
            soup = BeautifulSoup(requests.get(url, timeout=10).content, "html.parser")
            break
        except:
            time.sleep(5)

    for a_tag in soup.select('div.mw-parser-output a[href^="/wiki/"]'):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # пустой тег href
            continue

        # присоединяемся к URL, если он относительный (не абсолютная ссылка) 
        # и исключаем специальные страницы (например, "File:", "Help:")
        if ":" not in href:
            href = urljoin(url, href)
        parsed_href = urlparse(href)
        # удалить параметры URL GET, фрагменты URL и т. д.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if domain not in href:
            # внешняя ссылка
            continue
        urls.add(href)

    write_file(f"Найдено {len(urls)} ссылок для {url}", "log.txt")
        
    return urls

def find_path(url_start, url_end, rate_limit):
    '''Находит путь от url_start к url_end'''

    queue = [(url_start, [url_start])] #очередь с текущей ссылкой и путь до нее (первая ссылка - начало)
    requests_count = 0 #количество запросов, чтобы отслеживать лимит (начальное значение - 0)
    viewed_links = set() #просмотренные ссылки без повторов

    while queue: #пока очередь не пуста
        url_new, path = queue.pop() #возвращает последнюю пару ссылка-путь в очереди
        write_file(f"Обрабатываем ссылку {url_new}, путь {path}", "log.txt")

        if url_new == url_end: #если обрабатываетмая ссылка совпадает с искомой
            write_file("Путь найден!", "log.txt")
            return path #возвращаем путь
        
        if len(path) > 5: #если число переходов больше 5, переходим к следующей ссылке
            write_file("Превышено число переходов!", "log.txt")
            continue

        if url_new not in viewed_links: #если ссылку еще не просматривали
            viewed_links.add(url_new) #добавляем ссылку к просмотренным
            urls = get_links(url_new) #получаем для новой страницы
            requests_count = requests_count+1 #увеличиваем количество запросов

            if requests_count >= rate_limit: #если количество запросов превышает лимит
                time.sleep(1) #делаем паузу
                requests_count = 0 #обнуляем количество запросов

            for u in urls: #для всех найденных ссылок
                if u not in viewed_links: #если ссылку еще не просматривали
                    queue.append((u, path + [u])) #добавляем в очередь ссылку и путь для нее с учетом пройденного пути

    write_file(f"Путь от {url_start} до {url_end} не найден.", "log.txt") #очередь пуста, путь не найден
    return None #возвращаем пустой результат
        
def main(url1, url2, rate_limit):
    path1 = find_path(url1, url2, rate_limit)
    if path1:
        write_file(f"Путь от {url1} к {url2}: {path1}.", "result1.txt")
    else:
        write_file(f"Путь от {url1} к {url2} не найден за 5 шагов.", "result1.txt")

    path2 = find_path(url2, url1, rate_limit)
    if path1:
        write_file(f"Путь от {url2} к {url1}: {path2}.", "result2.txt")
    else:
        write_file(f"Путь от {url2} к {url1} не найден за 5 шагов.", "result2.txt")


    


url1 = "https://en.wikipedia.org/wiki/BSI_Ltd"
url2 = "https://en.wikipedia.org/wiki/Creole_language"
limit = 10

main(url1, url2, limit)