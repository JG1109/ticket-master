# imports
from app import app
from forms import ShowSearchForm, BuyerForm, RatingForm, ShopForm, HistoryForm
from flask import flash, render_template, request, redirect
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select, MetaData, Table
import mysql.connector
import sqlalchemy


s = "mysql+mysqlconnector://root:" + "wgzzsql" + "@104.197.213.149/wgzzdb"
engine = sqlalchemy.create_engine(s)

# define and create table
Base = declarative_base()
class Purchases(Base):
    __tablename__ = 'Purchases'

    BuyerName = sqlalchemy.Column(sqlalchemy.String(length=50))
    BuyerSSN = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    ShowName = sqlalchemy.Column(sqlalchemy.String(length=50))

    def __repr__(self):
        return "<Purchases(BuyerName='{1}', BuyerSSN='{0}', ShowName='{1}')>".format(self.BuyerName, self.BuyerSSN, self.ShowName)


Base.metadata.create_all(engine)

# create a session
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()


@app.route('/', methods=['GET', 'POST'])
def index():
    search = ShowSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('index.html', form=search)


"""
@app.route('/')
def test():
    return "Welcome to Ticket Master"
"""


@app.route('/results')
def search_results(search):
    results = None
    search_string = search.data['search']
    select_string = dict(ShowSearchForm.choices).get(search.select.data)
    # print("_____________")
    # print(select_string)
    # results = list()

    if search.data['search'] is not None:
        cnx = mysql.connector.connect(user='root', password='wgzzsql',
                                      host='104.197.213.149',
                                      database='wgzzdb')
        cursor = cnx.cursor()

        getter = "SELECT ShowName FROM Shows WHERE " + select_string + " = " + "'" + search_string + "';"
        cursor.execute(getter)
        replacement = cursor.fetchall()

        if not replacement:
            flash('No results found!')
            return redirect('/')

        # check if there are ratings for the show
        # ORM
        metadata = MetaData(bind=None)
        RatingTable = Table('Rating', metadata, autoload=True, autoload_with=engine)
        checker = select([RatingTable]).where(RatingTable.columns.ShowName == replacement[0][0])
        connection = engine.connect()
        results = connection.execute(checker).fetchall()
        # checker = "SELECT Rating FROM Rating WHERE ShowName" + " = " + "'" + replacement[0][0] + "';"
        # cursor.execute(checker)
        # results = cursor.fetchall()
        if not results:
            query = "SELECT * FROM (SELECT * FROM Shows NATURAL JOIN Location WHERE " \
                + select_string + " = " + "'" + search_string + "') AS a1;"
        else:
            query = "SELECT * FROM (SELECT * FROM Shows NATURAL JOIN Location WHERE " \
                + select_string + " = " + "'" + search_string + "') AS a1 NATURAL JOIN (SELECT ShowName, AVG(Rating) FROM Rating WHERE " \
                + "ShowName" + " = " + "'" + replacement[0][0] + "') AS a2;"
        # query = "SELECT * FROM Shows NATURAL JOIN Location WHERE " + select_string + " = " + "'" + search_string + "';"
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        cnx.close()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)


@app.route('/new_buyer', methods=['GET', 'POST'])
def new_buyer():
    form = BuyerForm(request.form)
    if request.method == 'POST' and form.validate():
        cnx = mysql.connector.connect(user='root', password='wgzzsql',
                                      host='104.197.213.149',
                                      database='wgzzdb')
        cursor = cnx.cursor()
        # check if the show name and venue exist
        checker = "SELECT * FROM Location WHERE ShowName = " + "'" + form.data['show'] + "'" + " AND Venue = " + "'" + \
                  form.data['venue'] + "';"
        cursor.execute(checker)
        results = cursor.fetchall()
        if not results:
            flash('Show name or Venue not found!')
            return redirect('/')

        # check if the buyer exists
        checker = "SELECT * FROM Buyers WHERE BuyerSSN = " + str(int(form.data['ssn'])) + ";"
        cursor.execute(checker)
        results = cursor.fetchall()
        if not results:
            # Add new buyer
            query = "INSERT INTO Buyers (BuyerSSN, BuyerName, BuyerAge, PhoneNumber, Email) VALUES (%s, %s, %s, %s, %s)"
            val = (form.data['ssn'], form.data['name'], form.data['age'], form.data['number'], form.data['email'])
            cursor.execute(query, val)
            cnx.commit()

        # Generate serial number and seat number
        SerialNumber = 111
        seat = 1
        checker = "SELECT SerialNumber, Seat FROM Ticket WHERE  SerialNumber = " + str(
            SerialNumber) + " AND Seat = " + "'" + str(seat) + "';"
        cursor.execute(checker)
        results = cursor.fetchall()
        while results:
            SerialNumber += 1
            seat += 1
            checker = "SELECT SerialNumber, Seat FROM Ticket WHERE SerialNumber = " + str(
                SerialNumber) + " AND Seat = " + "'" + str(seat) + "';"
            cursor.execute(checker)
            results = cursor.fetchall()

        # Add new ticket
        price = dict(BuyerForm.price).get(form.price_choice.data)
        if price == '$20':
            price_int = 20
        elif price == '$35':
            price_int = 35
        elif price == '$50':
            price_int = 50
        else:
            price_int = 90
        query = "INSERT INTO Ticket (SerialNumber, ShowName, Seat, Price, Venue) VALUES (%s, %s, %s, %s, %s)"
        val = (SerialNumber, form.data['show'], seat, price_int, form.data['venue'])
        cursor.execute(query, val)
        cnx.commit()

        # Add a new booking instance
        date = datetime.today()
        query = "INSERT INTO Book (BuyerSSN, SerialNumber, BookingDate) VALUES (%s, %s, %s)"
        val = (form.data['ssn'], SerialNumber, date)
        cursor.execute(query, val)
        cnx.commit()

        cursor.close()
        cnx.close()

        # Add new purchase
        # ORM
        newPurchase = Purchases(BuyerName=form.data['name'], BuyerSSN=form.data['ssn'], ShowName=form.data['show'])
        session.add(newPurchase)
        session.commit()

        flash('Ticket booked successfully!')
        return redirect('/')

    return render_template('new_buyer.html', form=form)


@app.route('/rate_show', methods=['GET', 'POST'])
def rate_show():
    form = RatingForm(request.form)
    if request.method == 'POST' and form.validate():
        # Check if the rater is a buyer
        cnx = mysql.connector.connect(user='root', password='wgzzsql',
                                      host='104.197.213.149',
                                      database='wgzzdb')
        cursor = cnx.cursor()
        checker = "SELECT BuyerSSN FROM Buyers WHERE BuyerSSN = " + str(form.data['ssn']) + ";"
        cursor.execute(checker)
        results = cursor.fetchall()
        if not results:
            flash('Not eligible to rate!')
            return redirect('/')

        # Check if the rater's name and SSN match
        checker = "SELECT BuyerSSN, BuyerName FROM Buyers WHERE BuyerSSN = " + str(
            form.data['ssn']) + " AND BuyerName = " + "'" + form.data['name'] + "';"
        cursor.execute(checker)
        results = cursor.fetchall()
        if not results:
            flash('Name and SSN did not match!')
            return redirect('/')

        # Add a piece of rating info
        date = datetime.today()
        rating = dict(RatingForm.rate).get(form.rate_choice.data)
        query = "INSERT INTO Rating (BuyerSSN, ShowName, Rating, RatingDate) VALUES (%s, %s, %s, %s)"
        val = (form.data['ssn'], form.data['show'], int(rating), date)
        cursor.execute(query, val)

        cnx.commit()

        cursor.close()
        cnx.close()

        flash('Rate successful!')
        return redirect('/')

    return render_template('rate_show.html', form=form)


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    form = ShopForm(request.form)
    if request.method == 'POST' and form.validate():
        # Register metadata
        metadata = MetaData(bind=None)

        # Check if the show is valid
        # ORM
        ShowsTable = Table('Shows', metadata, autoload=True, autoload_with=engine)
        checker = select([ShowsTable]).where(ShowsTable.columns.ShowName == form.data['show'])
        connection = engine.connect()
        results = connection.execute(checker).fetchall()

        if not results:
            flash('Show not found!')
            return redirect('/')

        # Fetch Merchandise data
        # ORM
        MerchandiseTable = Table('Shows', metadata, autoload=True, autoload_with=engine)
        checker = select([MerchandiseTable]).where(MerchandiseTable.columns.ShowName == form.data['show'])
        connection = engine.connect()
        results = connection.execute(checker).fetchall()

        return render_template('shop_results.html', results=results)

    return render_template('shop.html', form=form)


@app.route('/history', methods=['GET', 'POST'])
def history():
    form = HistoryForm(request.form)
    if request.method == 'POST' and form.validate():
        cnx = mysql.connector.connect(user='root', password='wgzzsql',
                                      host='104.197.213.149',
                                      database='wgzzdb')
        cursor = cnx.cursor()
        query = "SELECT BuyerSSN, COUNT(ShowName) AS Shows, SUM(Price) AS TotalCost FROM Buyers NATURAL JOIN Book NATURAL JOIN Ticket GROUP BY BuyerSSN"
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        cnx.close()

        return render_template('history_results.html', results=results)

    return render_template('history.html', form=form)


if __name__ == '__main__':
    app.run()
