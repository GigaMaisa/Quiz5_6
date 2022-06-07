from flask import Flask, redirect, url_for, render_template, request, session, flash
import requests
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Stragedy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

user_db = SQLAlchemy(app)


class User(user_db.Model):
    id = user_db.Column(user_db.INTEGER, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = user_db.Column(user_db.String(50), nullable=False, unique=True)
    password = user_db.Column(user_db.String(50), nullable=False)
    year = user_db.Column(user_db.INTEGER, nullable=False)


user_db.create_all()


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        y = request.form['year']

        if u == '' or p == '' or y == '':
            flash('Fill up every field')
        elif not 2014 <= int(y) <= 2022:
            flash('Please, enter year from 2014')
        else:
            session['username'] = u
            session['year'] = y

            user1 = User(username=u, password=p, year=int(y))
            user_db.session.add(user1)
            user_db.session.commit()
            return redirect(url_for('user'))
    return render_template('signup.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        u = request.form['username']
        y = request.form['year']
        password = request.form['password']

        user = User.query.filter_by(username=u).first()

        if user is not None:
            if password == user.password:
                session['username'] = u
                if y:
                    session['year'] = y
                    user.year = y
                    user_db.session.commit()
                else:
                    session['year'] = user.year
                return redirect(url_for('user'))
        elif len(y) == 0:
                flash('There is an error! Please enter correct info')
        elif not 2014 <= int(y) <= 2022:
            flash('Please enter correct year. From 2014')
        else:
            flash("Error")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('index.html')


@app.route('/user')
def user():
    if 'year' in session:
        year = session['year']
        resp = requests.get(f'http://ergast.com/api/f1/{year}/drivers.json')
        print(resp.status_code)

        result = resp.json()
        structured_res = json.dumps(result, indent=4)
        print(structured_res)
        with open("data.json", 'w') as data_file:
            json.dump(result, data_file, indent=4)

        with open('data.json') as data_file:
            res = json.load(data_file)

        drivers = res['MRData']['DriverTable']['Drivers']

        drivers_list = []

        for driver in drivers:
            drivers_list.append(tuple(driver.values()))


    return render_template('user.html', drivers_list=drivers_list)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)