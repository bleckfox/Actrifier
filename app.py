from imdb_parser import *
from random import randint

from flask import Flask
from flask import render_template
from flask import request

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
        # Run "Feeling lucky" if name field is empty
        if name == '':
            random_actor = randint(0, len(lucky_list))
            search_name = input_name(lucky_list[random_actor])
            actor_id = id_request_json(search_name)
            actor_info = responce_html(actor_id)

        # Run search if name field is not empty
        else:
            if name not in lucky_list:
                lucky_list.append(name)
            search_name = input_name(name)
            actor_id = id_request_json(search_name)
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


if __name__ == '__main__':
    app.run()
