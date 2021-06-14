from flask import Flask
from flask import render_template
from flask import request
import parser

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/card', methods=['POST'])
def card():
    if request.method == "POST":
        name = request.form['name']
        if name == '':
            print("name is empty")
        else:
            search_name = parser.input_name(name)
            actor_id = parser.id_request_json(search_name)
            actor_info = parser.responce_html(actor_id)
            print(actor_info)
        return render_template("card.html",
                               actor_name=actor_info[0],
                               actor_born_month=actor_info[1],
                               actor_born_year=actor_info[2],
                               actor_current_year=actor_info[3],
                               actor_img_link=actor_info[4],
                               actor_bio=actor_info[5],
                               actor_number_movie=actor_info[6],
                               movie_info=actor_info[7])

@app.route('/api/v1/subscription', )

if __name__ == '__main__':
    app.run()
