from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    privkey = PasswordField('Private key', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=25)])
    phone = StringField('phone', validators=[DataRequired(), Length(min=3, max=25)])
    address = StringField('address', validators=[DataRequired(), Length(min=3, max=200)])


class SignForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(min=3, max=200)])
    text = StringField('text', validators=[DataRequired(), Length(min=3, max=20000)])


class VerifyForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(min=3, max=200)])
    text = StringField('text', validators=[DataRequired(), Length(min=3, max=20000)])
    signature = StringField('signature', validators=[DataRequired(), Length(min=3, max=20000)])
    pubkey = StringField('pubkey', validators=[DataRequired(), Length(min=3, max=20000)])
