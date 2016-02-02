# -*- coding: utf-8 -*-

from tkinter import *
import urllib.request
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
			print("Erreur d'ecriture")
		finally:
			file.close()
	except FileExistsError:
	#si ce fichier existe, on en fait un backup
		path = pathsave.replace('.',' oldversion('+str(duplicate)+').',1)
		flag = False
		while not flag:
		#on teste la présence d'autres backups, on ne les overwrite pas
			try:
				fileCopy = codecs.open(path, encoding='utf-8', mode='x')#teste si d'autres backups existent
				flag = True
				copyfile(pathsave, path)#backup du fichier existant
				file = codecs.open(pathsave, encoding='utf-8', mode='w')
				try:
				#on overwrite le fichier dont on a fait un backup et on y écrit le 
				#dictionnaire sous format json
					file.write(json.dumps(dico, indent=4))
				except IOError:
					print("Erreur d'ecriture")
				finally:
					fileCopy.close()
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

class App(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.pack()
		self.loadData()
		return
	def loadData(self):
		self.__listbox = Listbox(self)
		self.__listbox.pack()
		for user in database["users"]:
			self.__listbox.insert(END, user["nickname"])
		self.__f = Frame(self)
		self.__b1=Button(self.__f, text='DeleteUserForever', command=self.deleteUser)
		self.__b1.pack()
		self.__f.pack()
		return
	def deleteUser(self):
		user=self.__listbox.get(ACTIVE)
		thisUser=currentUser(user)
		if(thisUser["nickname"]!="default"):
			database["users"].remove(thisUser)
			writeJson("database/database.JSON", database)
		self.__listbox.destroy()
		self.__b1.destroy()
		self.__f.destroy()
		self.loadData()
		return
database=readJson("database/database.JSON")
window = Tk()
app= App(window)
app.mainloop()