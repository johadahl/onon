# -*- coding: utf-8 -*-

from flask import render_template, url_for, flash, redirect, request
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from app import app, bcrypt, db, mail
from app.models import User, Responses
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

Questions = [
	'Säkerställa att våra fordon ger ett intryck som ligger i linje med vårt varumärke',
	'Leva upp till våra kunders miljökrav på sina leverantörers fordonspark',
	'Anpassa fordonsparken till vår miljöambition',
	'Bygga förtroende för oss som samhällsbyggare',
	'Säkerställa att medarbetarna är stolta över vilka fordon vi använder',
	'Säkerställa att vår bilpolicy är konkurrenskraftig på arbetsmarknaden'
]

#
#	Detta är route-filen som exekverar olika saker beroende på klientens GET-request
#	T.ex. www.ONONAB.se/kund kommer att rendera kund.html
#

# Renderar bara startsidan
@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html', title='Home')


# Sitan med kundlistan skall öppnas
@app.route("/kund")
@login_required
def kund():
	responses = Responses.query.all()	# Query på ALLA rader i hela databasen. En rad per företag. Definierad så att man får ('ÅF-nummer', 'Företagsnamn', 'organisationsnummer', 'KAM')
	return render_template('kund.html', title='Kunder', responses=responses) # Renderar kund.html och skickar med alla rader från databasen


# Denna sida visar alla svar som en kund har gett
@app.route("/kund/<foretag>")
@login_required
def responses(foretag):
	responses = Responses.query.filter_by(company=foretag).first() # Hämtar alla kolumner kopplat till ett företaget man klickat på
	res = responses.return_responses()	# Funktion i DB-objektet som returnerar en lista med alla svar för att det skall gå att itterera igenom i HTML-dokumentet
	return render_template('responses.html', title=foretag, responses=res, questions=Questions) # Renderar responses.html, res = lista med svar, Questions = hårkodad lista med respektive fråga, form=Responseform som är skapad i Forms.py



# Denna sida är för att kunna skapa ett konto på servern
@app.route("/register", methods=['GET', 'POST']) # Kan hantera både GET och POST requests. POST requests sker när man skickar in inloggningsdetaljer
def register():
	if current_user.is_authenticated:	# current_user är en modul importerad från flask_login som känner av om någon redan är inloggad
		return redirect(url_for('home'))# Om så är fallet, rendera home.html
	form = RegistrationForm()			# Om inte, hämta RegistrationForm från Forms.py, och sedan se Return statement nedan
	if form.validate_on_submit():		# OM SubmitField klickas, kör nedan

		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # form.password.data = det som användaren har skrivit in i PasswordField (se forms.py). Detta hashas med flasks modul bcrypt 
		user = User(email=form.email.data, password=hashed_password)						# Inloggningsdetaljer sparas i ett objekt via clasen User från models.py som sparar parametrarna (ID, email, PW)
		db.session.add(user)	# SQLAlchemy kommando för att adda objektet
		db.session.commit() 	# commitar till databasen

		flash('Konto skapat för {form.email.data}! Du kan nu logga in', 'success')		# Givet att allt ovan fungerar så kommer en grön ('success') banner upp i toppen av sidan och konfirmerar att det gick
		return redirect(url_for('login'))												# För att samtidigt redirecta dig till login-sidan (url_for är en modul importerad från flask)
	return render_template('register.html', title='Register', form=form) # Om ingen är inloggad så renderas register.html tillsammans med RegistrationForm som hanterar registreringstrafiken


@app.route("/login", methods=['GET', 'POST']) # Kan hantera både GET och POST requests. POST requests sker när man skickar in inloggningsdetaljer
def login():
	if current_user.is_authenticated:	# current_user är en modul importerad från flask_login som känner av om någon redan är inloggad
		return redirect(url_for('home'))# Om så är fallet, rendera home.html
	form = LoginForm()					# Om inte, hämta RegistrationForm från Forms.py, och sedan se Return statement nedan
	if form.validate_on_submit():		# OM SubmitField klickas, kör nedan
		# Kod som kontrollerar om användaren finns i databasen
		user = User.query.filter_by(email=form.email.data).first() # Försöker hämta användaren i databasen genom att kolla om det finns ett User-objekt med angiven email
		if user and bcrypt.check_password_hash(user.password, form.password.data):  # Om användarnamnet stämmer samt om lösenordet som användaren skrivit in i formen stämmer med det hashade lösenordet i databasen, kör nedan
			login_user(user, remember=form.remember.data)							# login_user är en importerad modul från flask. remember är en form som finns i Forms.py. En check-box "remember me"
			next_page = request.args.get('next')									# Funktion som tar dig till den sidan du va på innan, om du försökt klicka på kundsida men inte kommit åt den pga att du inte var inloggad, så ska du redirectas till den och inte första-sidan när du lyckats logga in
			flash('Välkommen, du är nu inloggad som ' + user.email, 'success')		# Grön banner som säger att det gick bra
			return redirect(next_page) if next_page else redirect(url_for('home'))	# Redirect till första-sidan om du inte försökt komma in på någonting annat innan
		else:
			flash('Email eller lösenord är felaktigt, försök igen', 'danger')		# Fungerar det inte, så kommer det istället upp en röd ('danger') banner med text 
	return render_template('login.html', title='Login', form=form)					# Renderar login.html och skickar in formen


# Denna route renderar ingenting specielt, utan den kör flask-kommantod logout_user() och redirectar dig till första-sidan
@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

# Sida för att kunna ändra dina inloggningsuppgifter
@app.route("/account", methods=['GET', 'POST'])
@login_required		# Går bara att accessa om du är inloggad 
def account():
	form = UpdateAccountForm()	# Form från forms.py
	if form.validate_on_submit(): # OM SubmitField klickas, kör nedan
		current_user.email = form.email.data # Skriver över current_user.email med det som användaren skrivit in i UpdateAccountForm()
		db.session.commit()	
		flash('Din email har uppdaterats', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.email.data = current_user.email
	return render_template('account.html', title='Account', form=form)



# Sida du kommer till när du klickat på "Glömt lösenord?"
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()		# Form från forms.py
	if form.validate_on_submit():	# OM SubmitField klickas, kör nedan
		user = User.query.filter_by(email=form.email.data).first() # Kollar i databasen om det finns en användare med angiven email, if so, hämta objektet
		send_reset_email(user)		# Anropa funktionen send_reset_email() (se nedan), och skicka med user-objektet
		flash('Ett mail har skickats med instruktioner för att återställa lösenordet', 'info')	# Gul banner ('info') som säger att att återställningsmail har skickats till angiven email
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)



def send_reset_email(user):
	token = user.get_reset_token() # Skapar en unik "token" mha av User-objektet, googla detta för att få klarthet. Utan parameter så blir default livslängd 30min
	msg = Message('Password Reset Request', # Mail-funktion från flask_mail
		sender='noreply@ONONAB.com', 
		recipients=[user.email])			# Mottagaren av mailet ska vara den mail som är angiven och finns i databasen
	# Nedanstående är själva mailet som mottagaren kommer att få från ONONABtest@gmail.com som det ser ut nu
	msg.body = '''Klicka på följande länk för att ändra lösenord:

{url_for('reset_token', token=token, _external=True)}


'''

	mail.send(msg)	# Skickar meddelandet, se __init__.py för att förstå hur konfigurationerna för detta fungerar, och GOOGLA



# Sida som du kommer till när du har klickat på länken som du får i mailet när du har glömt lösenordet
@app.route("/reset_password/<token>", methods=['GET', 'POST'])	# Tokene'n som skapades mha User-objektet ovan kommer att läggas efter "/" i GET-requesten som kommer att användas för att validera att det är du (tidsbegränsad)
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)	# Metod som verifierar att det är rätt token samt plockar fram rätt objekt
	if user is None:						# Om det inte finns någon user eller om ditt token har "dött" (tar 30min), kör nedan
		flash('Felaktigt eller utgånget token', 'warning')	# Röd banner ('warning') med text om att det inte fungerar
		return redirect(url_for('reset_request'))	# Skickar tillbaks en till sidan för att skapa ett nytt token och få ett nytt mail
	form = ResetPasswordForm()						# Form från forms.py
	if form.validate_on_submit():					# OM SubmitField klickas, kör nedan
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # Hashar det nya lösenordet som anges i PasswordField
		user.password = hashed_password		# Updaterar det aktuella user-objektet
		db.session.commit()					# commitar till databasen (viola det är nu ändrat)
		flash('Lösenordet är nu återstält! Du kan nu logga in igen', 'success')
		return redirect(url_for('login'))	# Redirectar dig till login så att du kan logga in med det nya lösenordet
	return render_template('reset_token.html', title='Reset Password', form=form)	# Renderar reset_token.html 