from crypt import methods

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from sqlalchemy import asc
from sqlalchemy import desc

api_key = "e57bb57d8afb967602276222fa8344ab"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress deprecation warnings

# Step 2: Initialize SQLAlchemy
db = SQLAlchemy(app)

# Step 3: Define Models
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    title = db.Column(db.String(80), unique=True)
    year = db.Column(db.Integer )
    description = db.Column(db.String)
    rating = db.Column(db.Float,nullable=True)
    ranking = db.Column(db.Integer,nullable=True)
    review = db.Column(db.String,nullable=True)
    img_url = db.Column(db.String)



with app.app_context():
    db.create_all()

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

class MyForm(FlaskForm):
    rating = StringField('Your rating out of 10', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class Form(FlaskForm):
    Title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Done')


@app.route("/")
def home():
    num = 1
    all_movies = Movie.query.order_by(desc(Movie.rating)).all()
    for movies in all_movies:
        movies.ranking = num
        db.session.commit()
        num += 1



    return render_template("index.html",movies = Movie.query.order_by(asc(Movie.rating)).all())

@app.route("/edit/<int:id_num>",methods=["GET","POST"])
def edit(id_num):
    form = MyForm()
    if form.validate_on_submit():  # Check if the form is submitted and valid
        rating = form.rating.data  # Access form data
        review = form.review.data
        movie = Movie.query.get(id_num)
        movie.rating = float(rating)
        movie.review = review
        db.session.commit()
        return redirect(url_for("home"))  # Handle the form submission

    return render_template("edit.html",form=form)


@app.route("/delete/<int:id_num>",methods=["GET","POST"])
def delete(id_num):
    movie = Movie.query.get(id_num)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add",methods=["GET","POST"])
def add():
    form = Form()
    if form.validate_on_submit():
        return redirect(url_for("select",title = form.Title.data))
    return render_template("add.html",form=form)

@app.route("/select/<title>",methods=["GET","POST"])
def select(title):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": title,
        "page": 1  # Fetch only the first page of results
    }
    response = requests.get(url, params=params)
    results = response.json()["results"]
    return render_template("select.html", data=results)

@app.route("/get/<int:movie_id>",methods=["GET","POST"])
def get(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    # Parameters including the API key
    params = {
        "api_key": api_key,
        "language": "en-US"  # Optional: Specify the language of the response
    }

    # Make the GET request to TMDB API
    response = requests.get(url, params=params).json()
    print(response)
    poster_path = response.get("poster_path")
    new_movie = Movie(
        title=response["original_title"],
        year=response["release_date"].split("-")[0],
        description=response["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500{poster_path}" ,
        rating=response["vote_average"],
        ranking = 0,
        review = ""

    )

    # Add the movie to the session and commit it to the database
    db.session.add(new_movie)
    db.session.commit()
    movie = Movie.query.filter_by(title=response["original_title"]).first()
    return redirect(url_for("edit",id_num=movie.id))





if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=8000)
