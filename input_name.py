from urllib.request import urlopen
import json
import bs4
import requests
import unicodedata

def input_name():
    name = input("Type name: ").lower()  # переводим в нижний регистр
    split_name = name.split()            # разделяем по пробелам
    first_letter = name[0]               # получаем первую букву
    name_for_requst = split_name[0] + '_' + split_name[1]
    return_value = [first_letter, name_for_requst]
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



    # movie_poster_request = soup.select_one('.poster img')
    # movie_poster = ''
    # if movie_poster_request is not None:
    #     movie_poster = movie_poster_request.get('src')
    #movie_cast = soup.select('div.credit_summary_item')
    #movie_info = [#movie_poster]
    # file = open('text.txt', 'a')
    # file.write(str(soup.prettify().encode('utf-8')))
    # file.close()
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
    role = soup.select('#filmography .filmo-category-section div')
    rol = []
    for i in range(int(count_movie)):
        # получаем много инфы в выводе, берем только роль
        # заменяем точки на пустую строку, убираем пробелы перед ролью
        rol.append(role[i].text.split('\n')[-2].replace('...', '').strip())
    print(len(rol))
    filmography = soup.find_all('span', class_='year_column')
    f = []
    for i in filmography:
        f.append(unicodedata.normalize("NFKD", i.text))

    a = []
    for i in f:
        a.append(i.strip())
    general_url = 'https://www.imdb.com'
    movie_request = soup.select('#filmography .filmo-category-section b a')
    movie_link = []
    movie_title = []
    movie_poster = []
    for i in movie_request:
        index = movie_request.index(i)
        if a[index] != '':
            movie_link.append(general_url + i.get('href'))
            movie_title.append(i.text)

    #a = get_movie_info(movie_link[0])
    # for i in range(5):
    #     print(i)
    #     movie_poster.append(get_movie_info(movie_link[i]))

    return rol

a = request_json()
b = responce_html(a)
print(b)

'''

нужная функция для вывода списка актеров
    есть имя, id, фото, описание json [s]
    
запрос ролей

в выводе pre-production - исправить

нужно отслеживать complete

проверить если актер умер

вывести подсказку на имя актера (ввели только имя, 
    показываем всех актеров с таким именем)



'''