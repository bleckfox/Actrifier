import json
import bs4
import datetime
import unicodedata
from urllib.request import urlopen

import requests

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
# search_help_list = []


# Name to [First Letter, name_with_underscore_instead_of_spaces_and_lower_symbols] converter
def input_name(name):
    search_name = name.lower()
    name_for_request = search_name.replace(' ', '_')
    first_symbol = search_name[0]
    return_value = [first_symbol, name_for_request]
    return return_value


# Quick actor search
def actor_search(search):
    first_letter = search[0]
    name = search[1]
    url = "https://v2.sg.media-imdb.com/suggestion/" + first_letter + "/" + name + ".json"
    response = urlopen(url)
    actor_info_from_json = []
    try:
        data_json = json.loads(response.read())
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
    except Exception as e:
        print('Two or more words in search field')
        print('OR')
        print('Something fucked up ! ! !')
        print(f'Exception is {str(e)}')
    return actor_info_from_json


# Checks if actor exists on IMDb and if they do, returns their profile webpage content
def check_actor_existence(actor_id):
    main_url = 'https://www.imdb.com/name/'
    make_request = main_url + actor_id
    res = requests.get(make_request, headers={'accept-language': 'en-US;en'})
    if res.status_code >= 400:
        return None
    else:
        return res


# Extended actor information
def get_actor_info(actor_id):
    # Чтобы посчитать сколько актеру сейчас лет (если жив)
    now = datetime.datetime.now()
    general_url = 'https://www.imdb.com'
    res = check_actor_existence(actor_id)
    if res is None:
        raise NameError
    soup = bs4.BeautifulSoup(res.text, features='html.parser')
    body = soup.find('div', {'class': 'pagecontent'})

    # Get actor name
    name = body.find('h1', {'class': 'header'}).find('span', {'class': 'itemprop'}).text
    if name not in lucky_list:
        lucky_list.append(name)

    # Get actor photo
    try:
        img_link = body.find('img', {'id': 'name-poster'}).get('src')
    except AttributeError:
        img_link = body.find('img', {'class': 'no-pic-image'}).get('src')

    # Get actor bio
    bio_body = body.find('div', {'id': 'name-bio-text'}).find('div', {'class': 'inline'})
    bio = bio_body.text.split('\n')[1]
    bio_more = general_url + bio_body.find('span').find('a').get('href')

    # Get actor born info
    birth_info = []
    death_info = []
    try:
        born_request = body.find('div', {'id': 'name-born-info'}).find_all('a')
        # ['August 20', '1974', 'Vicenza, Veneto, Italy']
        for i in born_request:
            birth_info.append(i.text)

        # Проверяем жив ли актер
        try:
            # Умер
            death_request = body.find('div', {'id': 'name-death-info'}).find_all('a')
            for i in death_request:
                death_info.append(i.text)

            # Проверка месяца в дате рождения. Если есть выполним код ниже
            if len(birth_info[0]) > 4:
                age = int(death_info[1]) - int(birth_info[1])
            else:
                age = int(death_info[0]) - int(birth_info[0])
        except AttributeError:
            # Живой
            # Проверка месяца в дате рождения. Если есть выполним код ниже
            if len(birth_info[0]) > 4:
                age = now.year - int(birth_info[1])
            else:
                age = now.year - int(birth_info[0])
    except:
        birth_info = []
        age = 'Not found'

    # Get movie title and link and role
    movie_title = []
    movie_link = []
    movie_year = []
    filtered_movie_year = []    # Вспомогательный список для фильтрации
    role_list = []              # Вспомогательный список для фильтрации
    role = []
    count_production = []
    completed_count = 0

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
                    completed_count += 1
        except Exception as e:
            print('Нет статуса in_production')
            print(str(e))
            print(type(e))

        # Индекс от количества фильмов в in_prodution до конца
        production_len = len(count_production) - completed_count
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
        movie_count = len(movie_title)

        # Сформируем словарь данных для фильмов
        movie_list = []
        for i in range(movie_count):
            movie_list.append({
                'title': movie_title[i],
                'year': movie_year[i],
                'link': movie_link[i],
                'role': role[i],
            })
    except:
        movie_count = 0
        last_movie = None
        movie_list = []
        all_movies_count = 0

    #  'name - строка',
    #  'birth_info - список (см.выше)',
    #  'death_info - список (см.выше)',
    #  'age - число',
    #  'img_link - строка',
    #  'bio - строка',
    #  'bio_more - строка (ссылка)',
    #  'movie_count - число',
    #  'movie_list - список словарей',
    #  'completed_count - число',
    #  'last_movie - строка',
    #  'all_movies_count - число',

    return_value = {'name': name,
                    'birth_info': birth_info,
                    'death_info': death_info,
                    'age': age,
                    'img_link': img_link,
                    'bio': bio,
                    'bio_more': bio_more,
                    'movie_count': movie_count,
                    'movie_list': movie_list,
                    'completed_count': completed_count,
                    'last_movie': last_movie,
                    'all_movies_count': all_movies_count}

    # print("count movie = " + str(movie_count))
    # print("title len " + str(len(movie_title)))
    # print("link len " + str(len(movie_link)))
    # print("role len " + str(len(role)))
    # print("year len " + str(len(movie_year)))
    # print(role)
    return return_value
