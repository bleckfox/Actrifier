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

    # Temporary or permanently disabled
    # if (len(count_name)) >= 2:
    #     data_json = json.loads(responce.read())
    #     first_level = data_json['d'][0]
    #     try:
    #         actor_info_from_json.append({
    #             'name': first_level['l'],
    #             'id': first_level['id'],
    #             'photo': first_level['i']['imageUrl'],
    #             'description': first_level['s']
    #         })
    #     except:
    #         actor_info_from_json.append({
    #             'name': first_level['l'],
    #             'id': first_level['id'],
    #             'photo': None,
    #             'description': 'Unknown description'
    #         })
    # # Иначе собираем все id
    # else:
    try:
        data_json = json.loads(responce.read())
        # Однозначно не будет 16 людей с одним именем на imdb (их json не выдаст больше 8)
        for i in range(16):
            try:
                level = data_json['d'][i]
                if level['id'].startswith('nm'):
                    actor_info_from_json.append({
                        'name': level['l'],
                        'id': level['id'],
                        'photo': level['i']['imageUrl'] if 'i' in level and 'imageUrl' in level['i'] else None,
                        'description': level['s'] if 's' in level else None,
                    })
            except IndexError:
                # Actor count is less than set 16. It's normal. We shouldn't worry. Everything is ok. Right?
                pass
            except Exception as e:
                print(f'Actor {i} read failed with {str(e)}')
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
    res = check_actor_existence(id)
    if res is None:
        raise NameError
    soup = bs4.BeautifulSoup(res.text, features='html.parser')
    body = soup.find('div', {'class': 'pagecontent'})

    # Get actor name
    name = body.find('h1', {'class': 'header'}).find('span', {'class': 'itemprop'}).text

    # Get actor photo
    try:
        img_link = body.find('img', {'id': 'name-poster'}).get('src')
    except:
        img_link = body.find('img', {'class': 'no-pic-image'}).get('src')

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
        born_info = []
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
    count_completed = []

    try:
        movie_request = body.find('div', {'id': 'filmography'}) \
            .find('div', {'class': 'filmo-category-section'})
        title_request = movie_request.find_all('b')
        year_request = movie_request.find_all('span', {'class': 'year_column'})
        role_request = movie_request.find_all('div', {'class': 'filmo-row'})
        try:
            in_production = movie_request.find_all('a', {'class': 'in_production'})
            for i in in_production:
                count_production.append(i)

            for status in count_production:
                if status.text == 'completed':
                    count_completed.append(status.text)
        except:
            print('Нет статуса in_production')

        # Индекс от количества фильмов в in_prodution до конца
        production_len = len(count_production) - len(count_completed)
        for i in title_request[production_len:]:
            movie_title.append(i.find('a').text)
            movie_link.append(general_url + i.find('a').get('href'))
        last_movie = title_request[0].find('a').text
        all_movies_count = len(title_request)

        # То же самое для года фильма
        # Сначала приводим данные в читаемый вид
        for i in year_request[production_len:]:
            filtered_movie_year.append(unicodedata.normalize("NFKD", i.text))
        for i in filtered_movie_year:
            movie_year.append(i.strip())

        # То же самое для ролей
        # Сначала фильтруем -> замена символов, удаление пробелов и переносов строк
        for i in role_request[production_len:]:
            role_list.append(i.text.replace('...', '').strip().split('\n'))
        for i in role_list:
            try:
                if len(i) > 5:
                    role.append(i[5])
                else:
                    role.append(i[4])
            except:
                role.append('Unknown role')

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
    except:
        count_movie = 0
        last_movie = None
        movie_list = []
        all_movies_count = 0

    return_value_explaine = ['name - строка',
                             'born_info - список (см.выше)',
                             'death_info - список (см.выше)',
                             'age - число',
                             'img_link - строка',
                             'bio - строка',
                             'bio_more - строка (ссылка)',
                             'count_movie - число',
                             'movie_list - список словарей',
                             'count_completed - список',
                             'last_movie - строка',
                             'all_movies_count - число']

    return_value = {'name': name,
                    'born_info': born_info,
                    'death_info': death_info,
                    'age': age,
                    'img_link': img_link,
                    'bio': bio,
                    'bio_more': bio_more,
                    'count_movie': count_movie,
                    'movie_list': movie_list,
                    'count_completed': len(count_completed),
                    'last_movie': last_movie,
                    'all_movies_count': all_movies_count}

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