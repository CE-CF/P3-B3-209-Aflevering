from flask import Flask
# Defining flask as app
app = Flask(__name__)

# Defining secret app key to encrypt data
app.config['SECRET_KEY'] = 'fb30fdbbb3324bf8ab30f72a848f65ab' # Created using the secrets library in python with the function secrets.token_hex(16)

# Setting up database location
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Defining our database
# db = SQLAlchemy(app)

# Crating a class for the password hashing function Bcrypt
# bcrypt = Bcrypt(app)

# Create a login flask login manager
# login_manager = LoginManager(app)

# To avoid circular import this is placed after database initilazation 
from coms import routes

