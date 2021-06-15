import json
from random import randint

from flask import Flask
from flask import render_template
from flask import request

from imdb_parser import *
from scheduled_cheker import CheckerScheduler

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
                           lucky_list=lucky_list)

@app.route('/card', methods=['POST'])
def card():
    if request.method == "POST":
        name = request.form['name']
        #actor_info = []
        # когда проверяли только имя была ошибка -> используется до объявления

        # Run "Feeling lucky" if name field is empty
        if name == '':
            random_actor = randint(0, len(lucky_list)-1)
            search_name = input_name(lucky_list[random_actor])
            actor_id = request_js(search_name)[0]['id']
            actor_info = get_actor_info(actor_id)
        # Run search if name field is not empty
        else:
            if name not in lucky_list:
                lucky_list.append(name)
            search_name = input_name(name)
            actor_id = request_js(search_name)[0]['id']
            actor_info = get_actor_info(actor_id)

        # Если только имя, выведем все имена, как подсказку
        # для поиска
        #split_name = name.split(' ')
        # if len(split_name) == 1:
        #     search_name = input_name(name)
        #     actor_name = request_js(search_name)
        #     for i in range(0, len(actor_name)):
        #         search_help_list.append(actor_name[i]['name'])

        # Run search if name field is not empty
        # elif len(split_name) >= 2:
        #     if name not in lucky_list:
        #         lucky_list.append(name)
        #     search_name = input_name(name)
        #     actor_id = request_js(search_name)[0]['id']
        #     actor_info = get_actor_info(actor_id)

        return render_template("card.html",
                               #search_help_list=search_help_list,
                               lucky_list=lucky_list,
                               actor_name=actor_info[0],
                               actor_born_info=actor_info[1],
                               actor_death_info=actor_info[2],
                               actor_age=actor_info[3],
                               actor_img_link=actor_info[4],
                               actor_bio=actor_info[5],
                               actor_bio_more=actor_info[6],
                               actor_number_movie=actor_info[7],
                               movie_info=actor_info[8])

# @app.route('/actor', methods = ['POST'])
# def get_post_javascript_data():
#     print("I'm here")
#     name = request.form['javascript_data']
#     split_name = name.split(' ')
#     if len(split_name) == 1:
#         search_name = input_name(name)
#         print(search_name)
#         actor_name = request_js(search_name)
#         print(actor_name)
#         for i in range(0, len(actor_name)):
#             search_help_list.append(actor_name[i]['name'])
# Нужно сформированный список отобразить на сайте
# Js в помощь

if __name__ == '__main__':
    checkerScheduler = CheckerScheduler()
    app.run()
