from urllib.request import urlopen
import json
import bs4
import requests
import unicodedata

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

a = request_js()
print(a)
'''
    
запрос ролей

в выводе pre-production - исправить

нужно отслеживать complete

выводить список фильмов не из credits, а считать его, как длину списка

проверить если актер умер

вывести подсказку на имя актера (ввели только имя, 
    показываем всех актеров с таким именем)

'''