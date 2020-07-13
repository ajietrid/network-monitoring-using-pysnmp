# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, Email, DataRequired

## login and registration

class LoginForm(FlaskForm):
    username = TextField    ('Username', id='username_login'   , validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login'        , validators=[DataRequired()])

class CreateAccountForm(FlaskForm):
    username = TextField('Username'     , id='username_create' , validators=[DataRequired()])
    email    = TextField('Email'        , id='email_create'    , validators=[DataRequired(), Email()])
    password = PasswordField('Password' , id='pwd_create'      , validators=[DataRequired()])

class AddNewIPphaseone(FlaskForm):
	ip = TextField('IP address', id='ip_add', validators=[DataRequired()])

class AddNewIPphasetwo(FlaskForm):
	ip = TextField('IP address', id='ip_add', validators=[DataRequired()])
	name = TextField('Name', id='name_add', validators=[DataRequired()])
	sysdescr = TextField('System Description', id='sysdescr_add' , validators=[DataRequired()])
	syslocation = TextField('System Location', id='syslocation_add', validators=[DataRequired()])
	snmp_ver= TextField('SNMP version', id='snmpver_add', validators=[DataRequired()])
	community_string = TextField('Community String', id='communitystring_add', validators=[DataRequired()])

class AddNewInterface(FlaskForm):
	interface = TextField('Interface', id='int_add', validators=[DataRequired()])