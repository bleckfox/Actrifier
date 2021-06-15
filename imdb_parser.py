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
search_help_list = []

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
    # Нужно, чтобы посчитать количество слов
    count_name = name.split('_')
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

def get_actor_info(id):
    # Чтобы посчитать сколько актеру сейчас лет (если жив)
    now = datetime.datetime.now()
    actor_id = id
    general_url = 'https://www.imdb.com'
    main_url = 'https://www.imdb.com/name/'
    make_request = main_url + actor_id
    res = requests.get(make_request)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features='html.parser')
    body = soup.find('div', {'class': 'pagecontent'})

    # Get actor name
    name = body.find('h1', {'class': 'header'}).find('span', {'class': 'itemprop'}).text

    # Get actor photo
    img_link = body.find('img', {'id': 'name-poster'}).get('src')

    # Get actor bio
    bio_body = body.find('div', {'id': 'name-bio-text'}).find('div', {'class': 'inline'})
    bio = bio_body.text.split('\n')[1]
    bio_more = general_url + bio_body.find('span').find('a').get('href')

    # Get actor born info
    born_info = []
    death_info = []
    try:
        born_request = body.find('div', {'id': 'name-born-info'}).find_all('a')
        # ['August 20', '1974', 'Vicenza, Veneto, Italy']
        for i in born_request:
            born_info.append(i.text)

        # Проверяем жив ли актер
        try:
            # Умер
            death_request = body.find('div', {'id': 'name-death-info'}).find_all('a')
            for i in death_request:
                death_info.append(i.text)

            # Проверка месяца в дате рождения. Если есть выполним код ниже
            if len(born_info[0]) > 4:
                age = int(death_info[1]) - int(born_info[1])
            else:
                age = int(death_info[0]) - int(born_info[0])
        except:
            # Живой
            # Проверка месяца в дате рождения. Если есть выполним код ниже
            if len(born_info[0]) > 4:
                age = now.year - int(born_info[1])
            else:
                age = now.year - int(born_info[0])


    except:
        born_info = ['Not found']
        born_year = ''
        age = 'Not found'

    # Get movie title and link and role
    movie_title = []
    movie_link = []
    movie_year = []
    filtered_movie_year = []    # Вспомогательный список для фильтрации
    role_list = []              # Вспомогательный список для фильтрации
    role = []
    count_production = []
    movie_request = body.find('div', {'id': 'filmography'})\
        .find('div', {'class': 'filmo-category-section'})
    title_request = movie_request.find_all('b')
    year_request = movie_request.find_all('span', {'class': 'year_column'})
    role_request = movie_request.find_all('div', {'class': 'filmo-row'})
    try:
        in_production = movie_request.find_all('a', {'class': 'in_production'})
        for i in in_production:
            count_production.append(i)
        # if compete
    except:
        print('Нет статуса in_production')

    # Индекс от количества фильмов в in_prodution до конца
    for i in title_request[len(count_production):]:
        movie_title.append(i.find('a').text)
        movie_link.append(general_url + i.find('a').get('href'))

    # То же самое для года фильма
    # Сначала приводим данные в читаемый вид
    for i in year_request[len(count_production):]:
        filtered_movie_year.append(unicodedata.normalize("NFKD", i.text))
    for i in filtered_movie_year:
        movie_year.append(i.strip())

    # То же самое для ролей
    # Сначала фильтруем -> замена символов, удаление пробелов и переносов строк
    for i in role_request[len(count_production):]:
        role_list.append(i.text.replace('...', '').strip().split('\n'))
    for i in role_list:
        if len(i) > 5:
            role.append(i[5])
        else:
            role.append(i[4])

    # Количество фильмов
    count_movie = len(movie_title)

    # Сформируем словарь данных для фильмов
    movie_list = []
    for i in range(count_movie):
        movie_list.append({
            'title': movie_title[i],
            'year': movie_year[i],
            'link': movie_link[i],
            'role': role[i],
        })

    return_value_explaine = ['name - строка',
                             'born_info - список (см.выше)',
                             'death_info - список (см.выше)',
                             'age - число',
                             'img_link - строка',
                             'bio - строка',
                             'bio_more - строка (ссылка)',
                             'count_movie - число',
                             'movie_list - список словарей']
    return_value = [name,
                    born_info,
                    death_info,
                    age,
                    img_link,
                    bio,
                    bio_more,
                    count_movie,
                    movie_list]

    # print("count movie = " + str(count_movie))
    # print("title len " + str(len(movie_title)))
    # print("link len " + str(len(movie_link)))
    # print("role len " + str(len(role)))
    # print("year len " + str(len(movie_year)))
    # print(role)
    return return_value

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
    print(name_tag_from_html)
    print(count_movie)
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