from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate

# Istanzia le estensioni
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()