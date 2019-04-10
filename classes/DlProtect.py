# coding=UTF-8

from requests import Session
from bs4 import BeautifulSoup
import re

class DlProtect():

	headers={
		"Host": "www.dl-protect1.com",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
		"Accept-Encoding": "gzip, deflate",
		"Referer": "https://www.dl-protect1.com/435555515406206706756515550375059063385048067605355395654600r3661510l",
		#"Cookie": "__cfduid=d11e63fd1ad418e0b79edf012a226db171541604581; PHPSESSID=hsadtroa35vr3apccjg024lob4; cf_clearance=9a30fe23d5b8692c1b7a95f868da846e7aca4a7d-1541619503-1800-150",
		"Connection": "keep-alive",
	}

	def __init__(self, url):
		self.url=url
		self.session=Session()
		print(self.headers)
	
	def getAndSoup(self, params=None):
		r=self.session.get(self.url, params=params, headers=self.headers)
		print("[INFO] HTTP Response status = {}".format(r.status_code))
		#print(r.headers)
		self.html=r.text.encode("utf-8")
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
		length=19 # longueur de l'url du site (sans https://)
		
		self.number+=length
		self.number=round(self.number, 10)

	def getParams(self):
		param_names=["jschl_vc", "pass"]
		self.params={}
		for name in param_names:
			input=self.soup.find("input", {"name": name})
			self.params[name]=str(input["value"])

		#On recupere la valeur du dernier parametre (le truc chelou à calculer)
		self.params["jschl_answer"]=self.number

	def postAndSoup(self, params="None"):
		print(params)
		r=self.session.post(self.url, params=params)
		print("[INFO] HTTP Response status = {}".format(r.status_code))
		self.html=r.text.encode("utf-8")