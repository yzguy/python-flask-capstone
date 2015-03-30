#Imports for Flask, Flask-WTF, Flask-Login, Flask-SQLAlchemy
from flask import Flask, render_template, url_for, redirect, session, request
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, SubmitField
from wtforms.validators import Required
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy

#Create instance of Flask Class
#Secret Key for Sessions
#Config variable for database URI (Relative Pathname)
app = Flask(__name__)
app.secret_key = 'flask presentation'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pres.db'

#Create LoginManager object
#Initialize it
login_manager = LoginManager()
login_manager.init_app(app)

#Make SQLAlchemy Object
#Initialize it
db = SQLAlchemy()
db.init_app(app)
db.app = app

#user_load callback, used to reload the user object from
#the user ID stored in the session
@login_manager.user_loader
def load_user(userid):
	return db.session.query(User).get(userid)

#Class for LoginForm, Flask-WTF uses classes for forms
class LoginForm(Form):
	username = TextField('username', validators=[Required()])
	password = PasswordField('password', validators=[Required()])
	submit = SubmitField('submit')
	
	#When the user form is created it has function get the user object from the db
	def get_user(self):
		return db.session.query(User).filter_by(username=self.username.data).first()

#Class for RegisterForm
class RegisterForm(Form):
	firstname = TextField('firstname', validators=[Required()])
	lastname = TextField('lastname', validators=[Required()])
	email = TextField('email', validators=[Required()])
	username = TextField('username', validators=[Required()])
	password = PasswordField('password', validators=[Required()])
	submit = SubmitField('submit')

#Class for the User Model
class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	firstname = db.Column(db.String(64))
	lastname = db.Column(db.String(64))
	email = db.Column(db.String(120), unique = True)
	username = db.Column(db.String(64), unique = True)
	password = db.Column(db.String())
	
	def __init__(self, firstname, lastname, email, username, password):
		self.firstname = firstname
		self.lastname = lastname
		self.email = email
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User %r>' % self.username

	#Required method for your User Model when using Flask-Login
	def is_authenticated(self):
		return True

	#Required method for your User Model when using Flask-Login
	def is_active(self):
		return True
	
	#Required method for your User Model when using Flask-Login
	def is_anonymous(self):
		return False

	#Required method for your User Model when using Flask-Login
	def get_id(self):
		return unicode(self.id)

#Declare a route of / and /index, if a user goes to 
#these directories Flask will run the function for that route
@app.route('/')
@app.route('/index')
def index():
	#returns a rendered template back to the user
	return render_template('index.html',
		title = 'Home')

#Another route, this time with GET and POST methods, this is our 
#register form, it posts back to itself. If the form is validate,
#it creates a new User object and adds it to the database and
#redirects the user to the index page
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			newuser = User(form.firstname.data, form.lastname.data,
				form.email.data, form.username.data, form.password.data)
			db.session.add(newuser)
			db.session.commit()
			session['email'] = newuser.email
			return redirect( url_for('index') )
	elif request.method == 'GET':
		return render_template('register.html', 
			title = 'Register', form = form)

#Route for Login, another form. If its valid and the user exists in the 
#database, then the user is logged in with login_user(user) which is
#a part of Flask-Login. If its incorrect it sends them back to login and
#tells them its wrong
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = form.get_user()
			if (user != None):
				login_user(user)
				return redirect( url_for('home') )
			else:
				return render_template('login.html',
					title = 'Login', incorrect = True, form = form )
		else:
			return render_template('login.html',
				title = 'Login', form = form)
	elif request.method == 'GET':
		return render_template('login.html',
			title = 'Login', form = form)

#Route for logout, just calls logout_user() function, which is a part
#of Flask-Login, just gets rid of the session and everything that was
#a part of that user logging in
@app.route('/logout')
def logout():
	logout_user()
	return redirect( url_for('index') )

#Home route, also @login_required. With Flask-WTF you can declare routes
#to only be seen if a user is logged in, this is what the @login_required
#does. Other than that, this page just displays the information for the 
#current logged in user after they log in
@app.route('/home')
@login_required
def home():
	u = current_user
	return render_template('home.html',
		title = 'Home', 
		firstname = u.firstname,
		lastname = u.lastname,
		username = u.username,
		email = u.email)

#Give ability to run as module or standalone
#Run server with debugging on
if __name__ == '__main__':
	app.run(debug = True)






