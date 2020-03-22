from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
import json, os
from sqlalchemy.dialects import postgresql

# from app import app

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Models
Define the models used in the project
'''

class Strategy(db.Model):
  __tablename__ = 'strategy'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  params = db.Column(postgresql.ARRAY(db.String))
  bots = db.relationship('Bot', backref = 'strategy', lazy = True)

  def format(self):
    listy = [x for x in self.params]
    return {
      'id': self.id,
      'name': self.name,
      'params': listy 
    }

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def update(self):
    db.session.commit()

class Bot(db.Model):
  __tablename__ = 'bot'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(20))
  active = db.Column(db.Boolean)
  timeframe = db.Column(db.String(5))
  param_values = db.Column(postgresql.ARRAY(db.String))
  strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))

  def format(self):
    listy = [x for x in self.param_values]
    return {
      'id': self.id,
      'name': self.name,
      'active': self.active,
      'timeframe': self.timeframe,
      'param_values': listy,
      'strategy_id' : self.strategy_id,
    }

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def update(self):
    db.session.commit()