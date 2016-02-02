#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import route, run, template, post, request
import json
from shutil import copyfile
from datetime import *
import codecs

def readJson(path):
#permet de lire un fichier contenant un dictionnaire au format Json, 
#et de retourner celui-ci sous forme de dictionnaire
	#phase lecture
	jsonText=""
	try:
		with codecs.open(path, encoding='utf-8', mode='r') as file:
			lines = file.readlines()
			for line in lines:
				jsonText+=line
	except FileNotFoundError:
		print('le fichier est introuvable')
		return
	except IOError:
		print("erreur d'ouverture")
		return
	#phase traitement
	try:
		jsonDico=json.loads(jsonText)
	except:
		print("erreur de conversion, verifiez que le document contient un texte de type json")
		return
	return jsonDico

	
def writeJson(path, dico):
#permet de sauvegarder un dictionnaire dans un fichier
#sauvegarde les anciennes versions en les numérotant (le numéro le plus
#élevé est la sauvegarde la plus récente, après le fichier ayant
#le nom originel
	duplicate=1
	pathsave=path
	try:
	#on tente d'ouvrir un nouveau fichier du nom spécifié
		file = codecs.open(path, encoding='utf-8', mode='x')
		try:
		#si le fichier n'existe pas déjà, on y écrit le dictionnaire sous format json
			file.write(json.dumps(dico, indent=4))
		except IOError:
			print("Erreur d'écriture")
		finally:
			file.close()
	except FileExistsError:
	#si ce fichier existe, on en fait un backup
		path = pathsave.replace('.',' oldversion('+str(duplicate)+').',1)
		flag = False
		while not flag:
		#on teste la présence d'autres backups, on ne les overwrite pas
			try:
#				fileCopy = codecs.open(path, encoding='utf-8', mode='x')#teste si d'autres backups existent
				flag = True
#				copyfile(pathsave, path)#backup du fichier existant
				file = codecs.open(pathsave, encoding='utf-8', mode='w')
				try:
				#on overwrite le fichier dont on a fait un backup et on y écrit le 
				#dictionnaire sous format json
					file.write(json.dumps(dico, indent=4))
				except IOError:
					print("Erreur d'écriture")
				finally:
#					fileCopy.close()
					file.close()
			except FileExistsError:
			#si des backups existent, on cherche un nom de fichier non utilisé
				duplicate+=1
				path = pathsave.replace('.',' oldversion('+str(duplicate)+').',1)
	except IOError:
		print("Erreur d'ouverture du fichier")
	return

	
def readFile(path):
#permet de lire un fichier et de le convertir en un string python
	HTMLtext=""
	try:
		with codecs.open(path, encoding='utf-8', mode='r') as file:
			lines = file.readlines()
			for line in lines:
				HTMLtext+=line
	except FileNotFoundError:
		print('le fichier est introuvable')
		return
	except IOError:
		print("erreur d'ouverture")
		return
	return HTMLtext
	

def currentUser(nickname):
#permet d'obtenir la reference vers l'utilisateur connecte
	for user in database["users"]:
		if(user["nickname"]==nickname):
			return user
	return database["users"][0]
	
	
#page d'identification => login.html
@route('/')
@route('/login')
def loginPage(message=''):
	return template(readFile('login.html'), message=message)
@post('/loginPost')
def login():
	username=request.forms.get('username')
	password=request.forms.get('password')
	for member in database["users"]:
		if (member["username"]==username and member["password"]==password):
			session=member["nickname"]
			return journalPage(session, session)
	return loginPage("Insert valid id's")
@post('/logout')
def logout():
	return loginPage()
	
#page d'inscription => registration.html
@post('/register')
def registrationPage(message=''):
	return template(readFile('registration.html'), message=message)
@post('/registerPost')
def registration():
	nickname=request.forms.get('nickname')
	username=request.forms.get('username')
	password=request.forms.get('password')
	for member in database["users"]:
		if(member["username"]==username):
			return registrationPage('Username already in use')
		if(member["nickname"]==nickname):
			return registrationPage('Nickname already in use')
	if(nickname=="" or username=="" or password==""):
		return registrationPage('You cannot let any blank field')
	thisUser={}
	thisUser["nickname"]=nickname
	thisUser["username"]=username
	thisUser["password"]=password
	thisUser["pictures"]=[]
	thisUser["comments"]=[]
	thisUser["videos"]=[]
	database['users'].append(thisUser)
	writeJson('database/database.JSON', database)
	return loginPage('your account has been successfully registered')
	
	
@post("/<session>/<nickname>/journal")
def journalPage(session, nickname, message=''):
	loggedUser=currentUser(session)
	viewedUser=currentUser(nickname)
	hidden=""
	if(session!=nickname):
		hidden="hidden"
	pictures=u''
	comments=u''
	videos=u''
	try:
		for picture in viewedUser['pictures']:
			pictures+=template(readFile('archPicture.html'), nickname=nickname, session=session, hidden=hidden, url=picture["url"], date=picture["date"], name=picture["name"])
	except KeyError:
		pass
	try:
		for comment in viewedUser['comments']:
			comments+=template(readFile('archComment.html'), nickname=nickname, session=session, hidden=hidden, order=comment["order"], content=comment["content"], author=comment["author"], date=comment["date"])
	except KeyError:
		pass
	try:
		for video in viewedUser['videos']:
			videos+=template(readFile('archVideo.html'), url=video["url"], name=video["name"], session=session, nickname=nickname, hidden=hidden)
	except KeyError:
		pass
	return template(readFile("journal.html"), message=message, pictures=pictures, comments=comments, videos=videos, nickname=nickname, session=session, hidden=hidden)
@post("/<session>/<nickname>/picturePost")
def journalPicture(session, nickname):
	viewedUser=currentUser(nickname)
	url=request.forms.get('urlPicture')
	thisPicture={}
	try:
		thisPicture["name"]=str(int(viewedUser["pictures"][0]["name"])+1)
	except:
		thisPicture["name"]="0"
	thisPicture["date"]=str(datetime.now())
	thisPicture["url"]=url
	viewedUser["pictures"].insert(0,thisPicture)
	writeJson('database/database.JSON', database)
	return journalPage(session, nickname)
@post("/<session>/<nickname>/commentPost")
def journalComment(session, nickname):
	viewedUser=currentUser(nickname)
	loggedUser=currentUser(session)
	message=request.forms.get('comment')
	thisComment={}
	try:
		thisComment["order"]=str(int(viewedUser["comments"][0]["order"])+1)
	except:
		thisComment["order"]="0"
	thisComment["author"]=loggedUser["nickname"]
	thisComment["date"]=str(datetime.now())
	thisComment["content"]=message
	viewedUser["comments"].insert(0,thisComment)
	writeJson('database/database.JSON', database)
	return journalPage(session, nickname)
@post("/<session>/<nickname>/videoPost")
def journalVideo(session, nickname):
	viewedUser=currentUser(nickname)
	url=request.forms.get('urlVideo')
	thisVideo={}
	try:
		thisVideo["name"]=str(int(viewedUser["videos"][0]["name"])+1)
	except:
		thisVideo["name"]="0"
	thisVideo["date"]=str(datetime.now())
	thisVideo["url"]=url
	viewedUser["videos"].insert(0,thisVideo)
	writeJson('database/database.JSON', database)
	return journalPage(session, nickname)
@post("/<session>/<nickname>/deleteVideo/<name>")
def deleteVideo(session, nickname, name):
	loggedUser=currentUser(session)
	for video in loggedUser["videos"]:
		if video["name"]==name:
			loggedUser["videos"].remove(video)
			writeJson('database/database.JSON', database)
			break
	return journalPage(session, nickname)
@post("/<session>/<nickname>/deleteComment/<order>")
def deleteComment(session, nickname, order):
	loggedUser=currentUser(session)
	for	comment in loggedUser["comments"]:
		if comment["order"]==order:
			loggedUser["comments"].remove(comment)
			writeJson('database/database.JSON', database)
			break
	return journalPage(session, nickname)
@post("/<session>/<nickname>/deletePicture/<name>")
def deletePicture(session, nickname, name):
	loggedUser=currentUser(session)
	for picture in loggedUser["pictures"]:
		if picture["name"]==name:
			loggedUser["pictures"].remove(picture)
			writeJson('database/database.JSON', database)
			break
	return journalPage(session, nickname)
@post("/<session>/search")
def searchUser(session):
	nickname=request.forms.get('search')
	viewedUser=currentUser(nickname)
	if(viewedUser["nickname"]=="default"):
		return journalPage(session, session, "cette personne n'est pas enregistree")
	else:
		return journalPage(session, nickname)
	
database=readJson('database/database.JSON')
run(host='localhost', port=8080)