from classes.AT import AT
from time import sleep
import random, string

# Toutes les etapes sont appelees ici individuellement pour faciliter le debug
dlp=AT("https://annuaire-telechargement.com")
dlp.getAndSoup()
dlp.getScript()
dlp.getSteps()
dlp.calculate()
dlp.getParams()

# On attend un peu pour pas se faire rodav' (le navigateur met plusieurs secondes a calculer)
sleep(3)

# C'est un peu moche mais pour garder la meme session, j'update l'url et je refais le get avec la meme instance de DlProtect
# dlp.url="https://www.annuaire-telechargement.com/cdn-cgi/l/chk_jschl"
dlp.makeChallenge()

# Je suis cense trouver le code de la success page
# print(dlp.html)


