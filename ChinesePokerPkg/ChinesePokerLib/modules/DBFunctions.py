import mysql.connector

from ChinesePokerLib.classes.ExceptionClasses import DBWriteError

default_instance="chinesepoker.cgegv43sayeg.eu-west-2.rds.amazonaws.com"
default_username="devUser"
default_password="devPass"
default_db="DevDB"
default_port=3306

def connect_to_db(db_instance=default_instance, port=default_port, user=default_username, password=default_password, db=default_db):
  conn = mysql.connector.connect(host=db_instance, port=port, user=user, password=password, database=db)
  return conn

def select_query(query='SELECT * FROM random_dealt_hands', db_connector=None):
  if db_connector is None:
    db_connector = connect_to_db()
  
  c = db_connector.cursor()
  c.execute(query)
  output = c.fetchall()
  return output, db_connector


def insert_query(query, db_connector=None, no_commit=False, return_lastrowid=False):
  if db_connector is None:
    db_connector = connect_to_db()

  c = db_connector.cursor()
  c.execute(query)

  if no_commit is False:
    db_connector.commit()
  
  if return_lastrowid:
    last_row_id = c.lastrowid
    return db_connector, last_row_id
  else:
    return db_connector


def insert_many_query(base_query, to_insert, db_connector=None, no_commit=False):
  if db_connector is None:
    db_connector = connect_to_db()
  
  c = db_connector.cursor()
  c.executemany(base_query, to_insert)
  
  if no_commit is False:
    try:
      db_connector.commit()
    except:
      db_connector.rollback()
    raise DBWriteError('insert_many_query failed during commit.')
  
  return db_connector

def multiple_insert_queries(query_list, db_connector=None):
  if db_connector is None:
    db_connector = connect_to_db()

  c = db_connector.cursor()
  try:
    for query in query_list:
      if isinstance(query, (tuple, list)) and len(query) == 2:
        c.executemany(query[0], query[1])
      else:
        c.execute(query)
    
    db_connector.commit()
  except:
    db_connector.rollback()
    raise DBWriteError('multiple_insert_queries failed')
  return db_connector

def delete_query(query, db_connector=None, no_commit=False):
  if db_connector is None:
    db_connector = connect_to_db()

  c = db_connector.cursor()
  
  c.execute(query)

  n_rows_deleted = c.rowcount
  if no_commit is False:
    db_connector.commit()
  
  return db_connector, n_rows_deleted

def try_commit(db_connector):
  try:
    db_connector.commit()
  except:
    db_connector.rollback()
    raise DBWriteError('try_commit failed')
  return db_connector