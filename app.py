from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy

import PlaylistBuilder
from PlaylistBuilder import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class Concert(db.Model):
    """ """

    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(20), nullable=False) 
    show_date = db.Column(db.String(20), nullable=False) 
    show_location = db.Column(db.String(20)) 
    show_info = db.Column(db.String(20))

    def __repr__(self):
        return f'<Concert {self.show_location}, {self.show_date}>'


df_mgr = DataFrameManager()
df = df_mgr.stage_df()

def df_to_table(db):
    """ """

    df.to_sql('concerts', con=db.engine)

def table_to_df(db):
    """ """
    
    pd.read_sql_table('concerts', con=db.engine)


if __name__ == '__main__':
    app.run(debug=True)

# concert1 = Concert(artist='Test', show_date='Test', show_location= 'Test',show_info= 'Test')
# db.session.add(concert1)
# db.commit()

# Concert.query.all()
