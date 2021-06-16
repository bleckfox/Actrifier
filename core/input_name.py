from urllib.request import urlopen
import json
import bs4
import requests
import unicodedata
import datetime

def input_name():
    name = input("Type name: ").lower()  # переводим в нижний регистр
    first_symbol = name[0]
    name_for_request = name.replace(' ', '_')
    return_value = [first_symbol, name_for_request]
    # split_name = name.split()            # разделяем по пробелам
    # first_letter = name[0]               # получаем первую букву
    # name_for_requst = split_name[0] + '_' + split_name[1]
    # return_value = [first_letter, name_for_requst]
    return return_value

def request_json():
    input = input_name()
    first_letter = input[0]
    name = input[1]
    url = "https://v2.sg.media-imdb.com/suggestion/" + first_letter + "/" + name + ".json"
    responce = urlopen(url)
    data_json = json.loads(responce.read())
    first_level = data_json['d'][0]
    actor_id = first_level['id']
    return actor_id

# get poster and cast
def get_movie_info(link):
    res = requests.get(link)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features='html.parser')
    movie_cast = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item--link', limit=6)#.get('src')
    movie_poster = soup.select_one('.ipc-media--poster img')
    if movie_poster is not None:
        movie_poster = movie_poster.get('src')
    else:
        movie_poster = ''
    cast_list = []
    filter_cast = []
    for i in movie_cast:
        cast_list.append(i.text)

    return movie_poster

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
    try:
        img_link = body.find('img', {'id': 'name-poster'}).get('src')
    except:
        img_link = body.find('img', {'class': 'no-pic-image'}).get('src')

    # Get actor bio
    bio_body = body.find('div', {'id': 'name-bio-text'}).find('div', {'class': 'inline'})
    bio = bio_body.text.split('\n')[1]
    bio_more = general_url + bio_body.find('span').find('a').get('href')

    # Get actor born info
    try:
        born_request = body.find('div', {'id': 'name-born-info'}).find_all('a')
        born_info = []
        death_info = []
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
        born_month = 'Not found'
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
    movie_request = body.find('div', {'id': 'filmography'})\
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
        print(i)
        try:
            if len(i) > 5:
                role.append(i[5])
            else:
                role.append(i[4])
        except:
            role.append('Unknown role')

    count_movie = len(movie_title)
    print("count movie = " + str(count_movie))
    print("title len " + str(len(movie_title)))
    print("link len " + str(len(movie_link)))
    print("role len " + str(len(role)))
    print("year len " + str(len(movie_year)))
    print('completed count ' + str(len(count_completed)))

    #return bio
'''
+ name
+ born info
+ photo
+ bio
+ count movie
+ movie year
+ movie title
+ movie link
+ role

announced
pre-production
filming
post-production
completed
'''

a = request_json()
b = get_actor_info(a)
print(b)

def responce_html(id):
    actor_id = id
    main_url = 'https://www.imdb.com/name/'
    make_request = main_url + actor_id
    res = requests.get(make_request)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features='html.parser')
    # name_tag_from_html = soup.select_one('td.name-overview-widget__section h1.header span').text
    # born_info = soup.select_one('#name-born-info time').text.split()
    # img_link = soup.select_one('#img_primary img').get('src')
    # actor_bio = soup.select_one('#overview-top .inline').text.split('\n')[1]
    count_movie = soup.select_one('#filmography div').text.split()[3][1:]
    # filmography = soup.select('#filmography .filmo-category-section span.year_column')
    print(int(count_movie))

    # Get year of movie
    # filmography = soup.find_all('span', class_='year_column')
    # f = []
    # for i in filmography:
    #     f.append(unicodedata.normalize("NFKD", i.text))
    # a = []
    # for i in f:
    #     a.append(i.strip())

    # Get movie title and link
    # general_url = 'https://www.imdb.com'
    # movie_request = soup.select('#filmography .filmo-category-section b a')
    # movie_link = []
    # movie_title = []
    # for i in range(int(count_movie)):
    #     index = movie_request.index(movie_request[i])
    #     if a[index] != '':
    #         movie_link.append(general_url + movie_request[i].get('href'))
    #         movie_title.append(movie_request[i].text)

    # for i in movie_request:
    #     index = movie_request.index(i)
    #     if a[index] != '':
    #         movie_link.append(general_url + i.get('href'))
    #         movie_title.append(i.text)

    #a = get_movie_info(movie_link[0])
    # for i in range(5):
    #     print(i)
    #     movie_poster.append(get_movie_info(movie_link[i]))

    # Get actor's role
    role = soup.select('#filmography .filmo-category-section div')
    rol = []
    for i in range(int(count_movie)):
        # получаем много инфы в выводе, берем только роль
        # заменяем точки на пустую строку, убираем пробелы перед ролью
        ro = role[i].text.split('\n')[-2].replace('...', '').strip()
        if ro != '':
            rol.append(ro)
    print(len(rol))
    print(int(count_movie))
    return rol

# a = request_json()
# b = responce_html(a)
# print(b)

def request_js():
    input = input_name()
    first_letter = input[0]
    name = input[1]
    url = "https://v2.sg.media-imdb.com/suggestion/" + first_letter + "/" + name + ".json"
    responce = urlopen(url)
    # Заменяем _ на "пробел", чтобы посчитать количество слов
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
            print(type(data_json))
            for i in range(150):
                level = data_json['d'][i]
                actor_info_from_json.append({
                    'name': level['l'],
                    'id': level['id'],
                    'photo': level['i']['imageUrl'],
                    'description': level['s']
                })
        except:
            print('Two or more words in search field')
            print('OR')
            print('Something fucked up ! ! !')

    return actor_info_from_json

# a = request_js()
# print(len(a))
'''

нужно отслеживать complete

'''