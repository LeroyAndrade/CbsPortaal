# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from app import create_app
#
# db = SQLAlchemy()
# migrate = Migrate()
#
# app = create_app()

# main.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)