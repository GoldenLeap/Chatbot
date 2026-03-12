
import psycopg
from psycopg.rows import dict_row 
from datetime import datetime
import click
from flask import current_app, g 
from config import load_config

config = load_config()

def get_db():
    if 'db' not in g:
        try:
            g.db = psycopg.connect(**config)
            g.db.row_factory = dict_row
        except (Exception) as e:
            print(e)
    return g.db 

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read())
       
        
@click.command('init-db')
def init_db_cmd():
    init_db()
    click.echo("DB inicializado")
    
