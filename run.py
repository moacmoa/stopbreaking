from classes.DlProtect import DlProtect
from time import sleep

# Toutes les etapes sont appelees ici individuellement pour faciliter le debug
dlp=DlProtect("https://www.dl-protect1.com/435555515406206706756515550375059063385048067605355395654600r3661510l")
dlp.getAndSoup()
dlp.getScript()
dlp.getSteps()
dlp.calculate()
dlp.getParams()

# On print les parametres trouves
print(dlp.params)
p=dlp.params

# On attend un peu pour pas se faire rodav' (le navigateur met plusieurs secondes a calculer)
sleep(3)

# C'est un peu moche mais pour garder la meme session, j'update l'url et je refais le get avec la meme instance de DlProtect
dlp.url="https://www.dl-protect1.com/cdn-cgi/l/chk_jschl"
dlp.getAndSoup(p)

# Je suis cense trouver le code de la success page
print(dlp.html)

