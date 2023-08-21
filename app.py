from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import sqlite3

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
db = SQLAlchemy(app)

####### WEATHER DATABASE MODEL #######
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(30), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    wind = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(3), nullable=False)
    country = db.Column(db.String(3), nullable=False)
    date = db.Column(db.DateTime(timezone=True),
                           default=datetime.now())

    def __repr__(self):
        return f"Weather in {self.name}"

####### ROUTE METHODS #######
@app.route("/", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        weather = get_weather(request.form["city"])
        if len(weather) == 0:
            weathers = Weather.query.order_by(Weather.id).all()
            return render_template("index.html", apiError=True, weathers=weathers)
        else:
            if not db.session.query(Weather.id).filter_by(name=weather[0]).first():
                newCity = Weather(name=weather[0], description=weather[1],
                                            temperature=weather[2], pressure=weather[3],
                                            wind=weather[4], humidity=weather[5],
                                            icon=weather[6], country=weather[7])
                try:
                    db.session.add(newCity)
                    db.session.commit()
                    return redirect("/")
                except:
                    return "Something went wrong while adding city to database"
            else:
                weathers = Weather.query.order_by(Weather.id).all()
                return render_template("index.html", existError = True,
                                       existingCity = weather[0], weathers=weathers)
    else:
        weathers = Weather.query.order_by(Weather.id).all()
        return render_template("index.html", weathers=weathers)
    
@app.route("/delete/<int:id>")
def delete(id):
    city_to_delete = Weather.query.get_or_404(id)

    try:
        db.session.delete(city_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Something went wrong while deleting the city"
    
@app.route("/update/<int:id>")
def update(id):
    city_to_update = Weather.query.get_or_404(id)

    weather = get_weather(city_to_update.name)

    try:
        city_to_update.description = weather[1]
        city_to_update.temperature = weather[2]
        city_to_update.pressure = weather[3]
        city_to_update.wind = weather[4]
        city_to_update.humidity = weather[5]
        city_to_update.icon = weather[6]
        city_to_update.date = datetime.now()
        db.session.commit()
        return redirect("/")
    except:
        return "Something went wrong while updating weather info"

@app.route("/updateAll")
def update_all():
    weathers = Weather.query.all()

    for city in weathers:
        weather = get_weather(city.name)
        try:
            city.description = weather[1]
            city.temperature = weather[2]
            city.pressure = weather[3]
            city.wind = weather[4]
            city.humidity = weather[5]
            city.icon = weather[6]
            city.date = datetime.now()
            db.session.commit()
        except:
            pass

    return redirect("/")

@app.route("/deleteAll")
def delete_all():
    weathers = Weather.query.all()

    for city in weathers:
        try:
            db.session.delete(city)
            db.session.commit()
        except:
            return "Something went wrong while cleaning the database"
        
    return redirect("/")

####### HELPING FUNCTIONS #######
def get_weather(city):
    weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=4075f0cf1418656d2f408d0a3d2fa1b2")
    if weather.status_code == 200:
        weather = weather.json()
        return [weather["name"], weather["weather"][0]["description"],
                 weather["main"]["temp"], weather["main"]["pressure"], 
                 weather["wind"]["speed"], weather["main"]["humidity"],
                 weather["weather"][0]["icon"], weather["sys"]["country"]]
    else:
        return []
    

###### APP RUN CALL #####
if __name__ == "__main__":
    app.run(debug = True)