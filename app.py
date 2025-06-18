from flask import Flask,request, render_template
from db_conn import mysql, init_app

app = Flask(__name__)
init_app(app)
mysql.init_app(app)

@app.route('/', methods = ['GET', 'POST'])
def index():
    # if request.method == "POST":
    #     return render_template('index.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run()