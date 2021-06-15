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
        # Run "Feeling lucky" if name field is empty
        if name == '':
            random_actor = randint(0, len(lucky_list))
            search_name = input_name(lucky_list[random_actor])
            actor_id = request_js(search_name)[0]['id']
            actor_info = responce_html(actor_id)

        # Run search if name field is not empty
        else:
            if name not in lucky_list:
                lucky_list.append(name)
            search_name = input_name(name)
            actor_id = request_js(search_name)[0]['id']
            actor_info = responce_html(actor_id)

        return render_template("card.html",
                               lucky_list=lucky_list,
                               actor_name=actor_info[0],
                               actor_born_month=actor_info[1],
                               actor_born_year=actor_info[2],
                               actor_current_year=actor_info[3],
                               actor_img_link=actor_info[4],
                               actor_bio=actor_info[5],
                               actor_bio_more=actor_info[6],
                               actor_number_movie=actor_info[7],
                               movie_info=actor_info[8])


@app.route('/api/v1/search', methods=['GET'])
def search():
    name = None
    if 'feelingLucky' in request.args and request.args.get('feelingLucky', type=int) == 1:
        name = choice(lucky_list)
    elif 'name' in request.args:
        name = request.args.get('name', type=str)
    else:
        abort(400)

    actors = request_js([name[0], name.replace(' ', '_')])
    if len(actors) > 0:  # todo: actor found on imdb
        return jsonify({'results': actors, 'feelingLucky': False}), 200
    else:
        return jsonify(), 404


@app.route('/api/v1/actor', methods=['GET'])
def actor():
    if 'id' in request.args and request.args.get('id', type=str).startswith('nm'):
        # TODO: actor details
        return jsonify({'actor': {}}), 200
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
    app.run()
