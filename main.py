# imports
from app import app
from forms import ShowSearchForm
from flask import flash, render_template, request, redirect
import mysql.connector


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

    if search.data['search'] is not None:
        cnx = mysql.connector.connect(user='root', password='wgzzsql',
                                     host='104.197.213.149',
                                     database='wgzzdb')
        cursor = cnx.cursor()
        query = "SELECT * FROM Shows WHERE ShowName = " + "'" + search_string + "';"
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        cnx.close()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display table
        return render_template('results.html', results=results)


if __name__ == '__main__':
    app.run()
