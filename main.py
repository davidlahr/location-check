from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, InputRequired
import requests
from datetime import datetime, timedelta, timezone
import pytz
from dotenv import load_dotenv
load_dotenv()
import os

############### APPLICATION ########################################
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///address_api.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


################## CONSTANTS #######################################

API_KEY = os.getenv('API_KEY')
POSITIONSTACK_URL = "http://api.positionstack.com/v1/forward"

################### FORMS ########################################

class AddressSearch(FlaskForm):
    address = StringField('Full Address', validators=[DataRequired()])
    submit = SubmitField("Done")

################## FUNCTIONS #######################################

################# API FUNCTION
def get_loc(address):
    parameters = {"access_key": API_KEY,
                  "query": address,
                  "limit": "1",
                  "output": "json",
                  "timezone_module": "1"

                  }
    response = requests.get(url=POSITIONSTACK_URL, params=parameters)
    response.raise_for_status()
    data = response.json()
    return data['data']
    print(data['data'])

def get_time(hours):
    # current Datetime
    unaware = datetime.now()
    # print('Timezone naive:', unaware)
    aware = datetime.now(pytz.utc)
    # print('Timezone Aware:', aware)
    local_time = aware - timedelta(hours=hours)
    return local_time


# get_time(5)

##################### FRAMEWORK ########################################

@app.route('/', methods=["GET", "POST"])
def main_page():
    form = AddressSearch()
    if form.validate_on_submit():
        address_entered = form.address.data
        print(address_entered)
        address_result = get_loc(address_entered)
        print(address_result)
        offset = [x['timezone_module']['offset_string'] for x in address_result]

        offset2 = offset[0]
        offset3 = offset2.split(':')[0]
        offset4 = int(offset3) * -1
        print(offset4)
        local = get_time(offset4).strftime("%X")

        print(local)


        # local_time = get_time()
        print(address_result)
        return render_template("result.html", address_data=address_result, time_data=local)
    return render_template('index.html', form=form)



if __name__ == "__main__":
    app.run(debug=True)