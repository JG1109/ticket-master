# imports
from wtforms import Form, StringField, SelectField

class ShowSearchForm(Form):
    choices = [('Show Name', 'Show Name'),
               ('Show Type', 'Show Type'),
               ('Age Group', 'Age Group')]
    select = SelectField('Search for Shows:', choices=choices)
    search = StringField('')