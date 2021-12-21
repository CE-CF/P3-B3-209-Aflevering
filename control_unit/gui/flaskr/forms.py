from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class SettingsForm(FlaskForm):
    mac_addr = StringField('MAC-address', validators=[DataRequired(), Length(min=17, max=17)])
    work_start = IntegerField('Workday Start', validators=[DataRequired(), NumberRange(min=0, max=23)])
    work_end = IntegerField('Workday End', validators=[DataRequired(), NumberRange(min=0, max=23)])
    sleep_start = IntegerField('Bedtime', validators=[DataRequired(), NumberRange(min=0, max=23)])
    sleep_end = IntegerField('Wakeup Time', validators=[DataRequired(), NumberRange(min=0, max=23)])
    submit = SubmitField('Submit User Info', validators=[DataRequired()])
