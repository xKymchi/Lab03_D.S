# Lab03_D.S
# Spotify Analys

Jag har skapat en jämförande analys av personliga nedladdad spotify data för två personer. 

I denna respitory finns det mapp för bilder som är inkluderade för projektet samt de personliga csv filerna och även den gemensamma csv filen. 
En databas, en app.py och en .ipynb fil finns med för själva databasen, applikation och analys. 

* I mappen images finns bilderna som vi har kopplat till varje artist med rätt syntax som passar attributen i databasen för artisName.
* I .streamlit mappen finns den en liten kod som hanterar design layouten för streamlit webben.
* I app.py hittar ni all kod för analyserna med deras visualisering.
* I merged_data.ipynb hittar ni hur vi sätter ihop de två personliga csv filerna i en och även en del tester som vi gjort innan vi färdigställt våra analyser.
* I spotify.db ser ni databasen som skapats av den gemensamma csv filen.
* 3st CSV filer finns med, två av dessa är dn personliga spotify streaming historik datan och ena är de två personliga som blivit mergeade till en och samma CSV fil.

För att genomföra detta behövs följande:
* För visualiseringar: Matplotlib.pyplot, Plotly.express, PIL, Seaborn och OS, Streamlit
* För datahantering: Pandas, Sqlite3, Numpy
* Programmeringsspråk: Python
