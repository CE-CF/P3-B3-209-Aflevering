from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from ...submodules.database.database_DONE import Database
from flask_cors import CORS

# Defining flask as app
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Defining secret app key to encrypt data
app.config['SECRET_KEY'] = 'fb30fdbbb3324bf8ab30f72a848f65ab' # Created using the secrets library in python with the function secrets.token_hex(16)

# Setting up database location
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Defining our database
#db = SQLAlchemy(app)
db = Database('DB','localhost','admin','root')

# Crating a class for the password hashing function Bcrypt
bcrypt = Bcrypt(app)

# Create a login flask login manager
login_manager = LoginManager(app)

# To avoid circular import this is placed after database initilazation 
from control_unit.communication.coms import routes