from datetime import datetime
from control_unit.communication.coms import db, login_manager
from flask_login import UserMixin

# Define how to find a user by their id for the login_manager
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# Defining the user login table in our sql database
class User(db.Model, UserMixin):
	
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	# Defining the relationship between users and the users in the schedule
	user_input = db.relationship('UserInput', backref='author', lazy=True)

	def __repr__(self):
	    return 'User("{0}", "{1}")'.format(self.username, self.password)

# Defining the user schedule table in our sql database
class UserInput(db.Model, UserMixin):

	id = db.Column(db.Integer, primary_key=True)
	mac = db.Column(db.String(17), unique=True, nullable=False)
	work_start = db.Column(db.Integer, nullable=False)
	work_end = db.Column(db.Integer, nullable=False)
	sleep_start = db.Column(db.Integer, nullable=False)
	sleep_end  = db.Column(db.Integer, nullable=False)
	# Defining the relationship between users schedule they post
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
	    return 'UserInput("{0}", "{1}", "{2}", "{3}", "{4}", "{5}",)'.format(self.mac, self.work_start, self.work_end, self.sleep_start, self.sleep_end, self.user_id)

class SensorData(db.Model, UserMixin):

	id = db.Column(db.Integer, primary_key=True)
	sensor_id = db.Column(db.String(17), unique=True, nullable=False)
	temperature = db.Column(db.Numeric(3,1), nullable=False)
	humidity = db.Column(db.Numeric(3,1), nullable=False)
	motion = db.Column(db.Boolean, default=False, nullable=False)

	def __repr__(self):
		return 'SensorData("{0}", "{1}", "{2}, "{3}")'.format(self.sensor_id, self.temperature, self.humidity, self.motion)


# Creating this testing database is done by:
# python3
# from main import db
# db.create_all()
# from main import User, UserInput
# user_1 = User(username='CF', password='password')
# db.session.add(user_1)
# db.session.commit()

# For the UserInput table
# user_input_1 = UserInput(mac='00:00:5e:00:53:af', work='07.17', sleep='22.06', user_id=user.id_) 

# To see the content of a table
# table.query.all()

# To see the first entry
# table.query.first()

# Can filter results using the command
# table.query.filter_by(username='CF').all()

# Getting the first of the filtered results by 
# table.query.filter_by(username='CF').first()

# defining a user or user input
# user = User.query.filter_by(username='CF').all()
# userInput = UserInput.query.filter_by(user_i=user.id_).all()

# Finding a user using ther primary key or id in this case which is an integer
# table.query.get(id)

# Looking at a user input for a certain id
# defining a user as user = User.query.filter_by(username='Faur').all() 
# then using the command
# user.user_input

# To remove the database type
# db.drop.all()