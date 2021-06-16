from random import randint, choice

from flask import Flask
from flask import render_template
from flask import request, abort, jsonify

from imdb_parser import *
from scheduled_cheker import CheckerScheduler

app = Flask(__name__)
checkerScheduler = CheckerScheduler()


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
                               actor_name=actor_info['name'],
                               actor_born_info=actor_info['born_info'],
                               actor_death_info=actor_info['death_info'],
                               actor_age=actor_info['age'],
                               actor_img_link=actor_info['img_link'],
                               actor_bio=actor_info['bio'],
                               actor_bio_more=actor_info['bio_more'],
                               actor_number_movie=actor_info['count_movie'],
                               movie_info=actor_info['movie_list'])


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


@app.route('/api/v1/search', methods=['GET'])
def search():
    name = None
    if 'feelingLucky' in request.args and request.args.get('feelingLucky', type=int) == 1:
        name = choice(lucky_list)
    elif 'name' in request.args:
        name = request.args.get('name', type=str)
    else:
        abort(400)

    actors = request_js(input_name(name))
    if len(actors) > 0:
        return jsonify({'results': actors, 'feelingLucky': False}), 200
    else:
        return jsonify(), 404


@app.route('/api/v1/actor', methods=['GET'])
def actor():
    if 'id' in request.args and request.args.get('id', type=str).startswith('nm'):
        try:
            info = get_actor_info(request.args.get('id', type=str))
            return jsonify({'actor': {
                'id': request.args.get('id', type=str),
                'name': info[0],
                'birth_info': info[1] if info[1] != ['Not found'] else None,
                'death_info': info[2] if info[2] != [] else None,
                'age': info[3],
                'photo': info[4],
                'bio': info[5],
                'extended_bio_link': info[6],
                'movie_count': info[7],
                'movies': info[8],
            }}), 200
        except NameError:
            abort(404)
    else:
        abort(400)


@app.route('/api/v1/subscription', methods=['PUT'])
def addSubscription():
    if 'id' in request.args and 'firebaseToken' in request.args:
        actorId = request.args.get('id', type=str)
        firebaseToken = request.args.get('firebaseToken', type=str)

        if check_actor_existence(actorId) is not None:
            try:
                checkerScheduler.addSubscription(actorId=actorId, firebaseToken=firebaseToken)
            except ValueError:
                abort(400)
            return jsonify(), 201
        else:
            abort(404)
    else:
        abort(400)


@app.route('/api/v1/subscription', methods=['DELETE'])
def removeSubscription():
    if 'id' in request.args and 'firebaseToken' in request.args:
        actorId = request.args.get('id', type=str)
        firebaseToken = request.args.get('firebaseToken', type=str)

        try:
            checkerScheduler.removeSubscription(actorId=actorId, firebaseToken=firebaseToken)
            return jsonify(), 200
        except ValueError:
            abort(404)
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
