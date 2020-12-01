# imports
from wtforms import Form, StringField, SelectField

class ShowSearchForm(Form):
    choices = [('ShowName', 'ShowName'),
               ('ShowType', 'ShowType'),
               ('AgeGroup', 'AgeGroup')]
    select = SelectField('Search for Shows:', choices=choices)
    search = StringField('')

class BuyerForm(Form):
    sex = [('Male', 'Male'), ('Female', 'Female')]
    sex_choice = SelectField('Gender', choices=sex)
    name = StringField('Name')
    age = StringField('Age')
    number = StringField('Phone Number')
    email = StringField('Email')
    ssn = StringField('Social Security Number')
    show = StringField('Show Name')
    venue = StringField('Venue')
    price = [('$20', '$20'), ('$35', '$35'), ('$50', '$50'), ('$90', '$90')]
    price_choice = SelectField('Ticket Tier', choices=price)

class RatingForm(Form):
    name = StringField('Name')
    ssn = StringField('Social Security Number')
    show = StringField('Show Name')
    rate = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    rate_choice = SelectField('Rate the show', choices=rate)

class ShopForm(Form):
    show = StringField('Show Name')
