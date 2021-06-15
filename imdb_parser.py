import json
import bs4
import requests
import datetime
import unicodedata
from urllib.request import urlopen

lucky_list = ['Hugh Jackman',
              'Christian Bale',
              'Matthew McConaughey',
              'Gal Gadot',
              'Amy Adams',
              'Willem Dafoe',
              'Robert Downey Jr',
              'Scarlett Johansson',
              'Zoe Saldana',
              'Karen Gillan']

def input_name(name):
    search_name = name.lower()
    name_for_request = search_name.replace(' ', '_')
    first_symbol = search_name[0]
    return_value = [first_symbol, name_for_request]
    return return_value

def request_js(search):
    first_letter = search[0]
    name = search[1]
    url = "https://v2.sg.media-imdb.com/suggestion/" + first_letter + "/" + name + ".json"
    responce = urlopen(url)
    # Заменяем _ на "пробел", чтобы посчитать количество слов
    replace_name = name.replace('_', ' ')
    count_name = replace_name.split(' ')
    # Если 2 и больше слов, считаем, что ввели имя и фамилию
    # Количество id будет равно 1
    actor_info_from_json = []
    if (len(count_name)) >= 2:
        data_json = json.loads(responce.read())
        first_level = data_json['d'][0]
        actor_info_from_json.append({
            'name': first_level['l'],
            'id': first_level['id'],
            'photo': first_level['i']['imageUrl'],
            'description': first_level['s']
        })
    # Иначе собираем все id
    else:
        try:
            data_json = json.loads(responce.read())
            # Однозначно не будет 150 людей с одним именем на imdb
            for i in range(150):
                level = data_json['d'][i]
                actor_info_from_json.append({
                    'name': level['l'],
                    'id': level['id'],
                    'photo': level['i']['imageUrl'],
                    'description': level['s']
                })
        # Поэтому всегда будут выходить исключения
        # Их можно игнорировать
        except:
            print('Two or more words in search field')
            print('OR')
            print('Something fucked up ! ! !')
    return actor_info_from_json


def check_actor_existence(id):
    main_url = 'https://www.imdb.com/name/'
    make_request = main_url + id
    res = requests.get(make_request)
    #res.raise_for_status()
    if res.status_code >= 400:
        return None
    else:
        return res


def responce_html(id):
    now = datetime.datetime.now()
    general_url = 'https://www.imdb.com'
    res = check_actor_existence(id)
    if res is None:
        raise NameError
    soup = bs4.BeautifulSoup(res.text, features='html.parser')

    # Get Actor Name
    name_tag_from_html = soup.select_one('td.name-overview-widget__section h1.header span').text

    # Get born info and count current year
    # Проверить есть ли месяц
    try:
        born_info = soup.select_one('#name-born-info time').text.split()
        born_month = born_info[0] + ' ' + born_info[1]
        born_year = born_info[2]
        age = now.year - int(born_year)
    except:
        born_month = 'Not found'
        born_year = ''
        age = 'Not found'

    # Проверить умер ли актер
    # В браузере
    # Показать дату смерти и сколько ему было лет

    # Image link
    img_link = soup.select_one('#img_primary img').get('src')

    # Actor Bio Info
    actor_bio = soup.select_one('#overview-top .inline').text.split('\n')[1]
    actor_bio_more_request = soup.select_one('#overview-top .name-trivia-bio-text span a').get('href')
    actor_bio_more = general_url + actor_bio_more_request

    # Get Number of movie
    # Hide, Show, Actor, (61, credits)
    count_movie = soup.select_one('#filmography div').text.split()[3][1:]

    # Get Movie Year
    movie_year_request = soup.find_all('span', class_='year_column')
    filtered_date = []
    for i in movie_year_request:
        filtered_date.append(unicodedata.normalize("NFKD", i.text))
    movie_date = []
    for i in filtered_date:
        movie_date.append(i.strip())

    # Get Movie Title
    movie_request = soup.select('#filmography .filmo-category-section b a')
    movie_title = []
    movie_link = []
    for i in range(int(count_movie)):
        movie_title.append(movie_request[i].text)
        movie_link.append(general_url + movie_request[i].get('href'))

    # Get Actor Role
    role = soup.select('#filmography .filmo-category-section div')
    role_list = []

    for i in range(int(count_movie)):
        # получаем много инфы в выводе, берем только роль
        # заменяем точки на пустую строку, убираем пробелы перед ролью
        check_role = role[i].text.split('\n')[-2].replace('...', '').strip()
        if check_role != '':
            role_list.append(check_role)

    movie_list = []

    for i in range(int(count_movie)):
        #list_index = movie_title.index(i)
        movie_list.append({
            'title': i,
            'year': movie_date[i],
            'link': movie_link[i],
            'role': role_list[i] # здесь значений меньше
                                 # чем в списке фильмов
                                 # обработка complete
        })

    print(movie_list)
    return_value = [name_tag_from_html,
                    born_month,
                    born_year,
                    age,
                    img_link,
                    actor_bio,
                    actor_bio_more,
                    count_movie,
                    movie_list]
    return return_value