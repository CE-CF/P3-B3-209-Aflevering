from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from coms.models import User

# Creating a class to handle Registration form i.e. the different registration fields
class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username already exists, try a different one.')

# Creating a class to handle Login form i.e. the different login fields
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

# Creating a form that handles schedules
class UserInputForm(FlaskForm):
	mac = StringField('MAC Address', validators=[DataRequired(), Length(min=17, max=17)])
	work_start = IntegerField('Start of work', validators=[DataRequired(), NumberRange(min=0, max=24)])
	work_end = IntegerField('End of work', validators=[DataRequired(), NumberRange(min=0, max=24)])
	sleep_start = IntegerField('Going to sleep', validators=[DataRequired(), NumberRange(min=0, max=24)])
	sleep_end  = IntegerField('Waking up', validators=[DataRequired(), NumberRange(min=0, max=24)])
	submit = SubmitField(' Input User Data', validators=[DataRequired(),NumberRange(min=0, max=24)])