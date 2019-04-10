# coding=UTF-8

from requests import Session
from bs4 import BeautifulSoup
import re
from fonctions.tools import displayRequestDetails

class AT():

	headers={
		# "Host": "annuaire-telechargement.com", # défini dans le constructeur selon l'url
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
		"Cache-Control" : "no-cache",
		#"Cookie": different chaque coup
		"Connection": "keep-alive",
		# "Host" : a definir selon requete
		"Pragma": "no-cache",
		"TE": "Trailers",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
	}

	def __init__(self, url):
		self.url=url
		self.session=Session()
		self.host=self.url.split("://")[-1].split("/")[0]
		self.headers["Host"]=self.host
	
	def getAndSoup(self, params=None):
		r=self.session.get(self.url, params=params, headers=self.headers, allow_redirects=True)
		print("[INFO] HTTP Response status = {}".format(r.status_code))
		displayRequestDetails(r)
		self.html=r.text.encode("utf-8")
		# with open("ressources/example_05.html", "r") as f:
		# 	self.html=f.read()
		# print(self.html)
		self.soup=BeautifulSoup(self.html, "lxml")

	def getScript(self):
		self.script = self.soup.find("script").text

	def getSteps(self):
		self.steps=[]
		lines=self.script.split("\n")
		lines=[l.strip() for l in lines]
		lines=[l for l in lines if l!=""]

		first=[l for l in lines if l.startswith("var s,t,o,p,b,r,e,a,k,i,n,g,f, ")][0].split()[-1]

		reg=re.compile(r"(\w*)\=\{\"(\w*)\"\:(.*)\}\;")
		res=reg.search(first)
		varname=res.group(1)+"."+res.group(2)

		self.steps.append({"op":None, "calc":res.group(3)})

		sep=";"+varname
		second=[l for l in lines if l.startswith(sep)][0]
		for e in second.split(sep):
			if not e:
				continue
			exp=e.split(";")[0]
			op, calc=exp.split("=")
			self.steps.append({"op":op, "calc":calc})
	
	def calculate(self):
		# Decryptage des calculs
		self.number=0
		for step in self.steps:
			op = step["op"]
			calc = step["calc"].replace("!+[]", "1").replace("!![]", "1").replace("[]", "0")
			
			num,den = calc.split("/")
			num=num[3:-2]
			den=den[3:-2]
			lnum=num.split(")+(")
			lden=den.split(")+(")
			snum="".join([str(eval(e)) for e in lnum])
			sden="".join([str(eval(e)) for e in lden])
			
			result = eval(snum + "./" + sden)
			
			# Gestion de l'opération
			if not op:
				self.number = result
			elif op == "*":
				self.number *= result
			elif op == "-":
				self.number -= result
			elif op == "+":
				self.number += result
			else:
				print("[ERROR] extractNumber: unknown operator - '{}'".format(op))
				sys.exit(0)
	
		# Récupération de la longueur de l'URL
		# length=len(self.headers["Host"]) # longueur de l'url du site (sans https://)
		length=len(self.host)

		self.number+=length
		self.number=round(self.number, 10)

	def getParams(self):
		# Recuperation de certains parametres dans le code HTML
		param_names=["jschl_vc", "pass", "s"]
		self.params={}
		for name in param_names:
			input=self.soup.find("input", {"name": name})
			self.params[name]=str(input["value"])
		
		# Recuperation de l'URL à appeler pour faire le challenge
		self.urlChallenge=self.url+self.soup.find("form", {"id": "challenge-form"})["action"]

		#On recupere la valeur du dernier parametre (le truc chelou à calculer)
		self.params["jschl_answer"]=self.number

		print("Paramètres à envoyer :")
		for key, val in self.params.iteritems():
			print("\t{}:\t{}".format(key, val))

	def makeChallenge(self):
		# Modify max_redirects (default=30)
		# self.session.max_redirects=500
		# print(self.session.max_redirects)

		print("-----------------------------------------------")
		print("MAKING CHALLENGE !")
		print("-----------------------------------------------")

		# On ajoute un champ referer au header de la requete
		self.headers["referer"]=self.url

		# On balance le challenge (avec les paramètres trouvés)
		r=self.session.get(self.urlChallenge, params=self.params, headers=self.headers, allow_redirects=False)
		displayRequestDetails(r, False, False)	# code 302 attendu / 503 si challenge raté
		# print(r.text.encode("utf-8"))

		# On recharge l'url initiale pour récupérer le champ "location" du header de la reponse
		r=self.session.get(self.url, headers=self.headers, allow_redirects=False)
		displayRequestDetails(r, False, False)	# code 301 attendu
		location=r.headers["location"]
		# print(r.text.encode("utf-8"))
		
		# On tente de charger l'url de redirrection recuperée dans le hader de la reponse precedente
		r=self.session.get(location, headers=self.headers, allow_redirects=False)
		displayRequestDetails(r, False, False)	# code 200 attendu
		# print(r.text.encode("utf-8"))