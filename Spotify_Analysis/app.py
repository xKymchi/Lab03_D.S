import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image
import os
import seaborn as sns
 
# skapar en anslutning till en SQLite-databas där datan ska lagras
con = sqlite3.connect("spotify.db")

# läser in all data från 'spotify_data' tabellen i databasen till en Pandas DataFrame
# kör queryn och sparar resultatet i 'merged_data'
merged_data = pd.read_sql("SELECT * FROM spotify_data", con) 
# läser in all data från 'spotify_data_sample' tabellen i databasen till en Pandas DataFrame
# kör queryn och sparar resultatet i 'merged_data_sample'
merged_data_sample = pd.read_sql("SELECT * FROM spotify_data_sample", con)

# läser in CSV-filen för Valmirs och Kymias Spotify-data till en Pandas DataFrame
valmir_spotify = pd.read_csv('/Users/k/Documents/TUC/Data Science/code/kunskapskontroll3-main/Valmir_Spotify.csv')
kymia_spotify = pd.read_csv('/Users/k/Documents/TUC/Data Science/code/kunskapskontroll3-main/Kymia_Spotify.csv')

## Spotify logo
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg" width="150" style="margin-right: 10px;">
        <h1>Data Analysis</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.write('A comparative analysis of Spotify data for two users over the course of a year.')


st.write('### Analysis Question 1.')

# SQL-query som hämtar user, artistName och total lyssningstid (msPlayed) för varje user och artistName
query = """
SELECT user, artistName, SUM(msPlayed) as total_playtime
FROM spotify_data
GROUP BY user, artistName
ORDER BY user, total_playtime DESC
"""

# hämtar resultaten från queryn och spara det i en DataFrame
user_artist_playtime = pd.read_sql(query, con)

# lägger till en ny kolumn 'total_playtime_hours' som omvandlar lyssningstiden från millisekunder till timmar
user_artist_playtime["total_playtime_hours"] = user_artist_playtime["total_playtime"] / (1000 * 60 * 60)

# gruppiera data efter användare och hämta de 3 artister med högst total lyssningstid per användare
top3_artists_user = (
    user_artist_playtime.groupby("user")
    .apply(lambda x: x.nlargest(3, "total_playtime_hours"))  # hämtar de 3 största värdena per användare
    .reset_index(drop=True)  # nollställ index efter gruppering
)

# sätter sökvägen för bilder på artisterna
image_dir = "images"

# hämta unika användarnamn från 'top3_artists_user'
users = top3_artists_user["user"].unique()

# filtrerar ut Valmirs och Kymias top 3 artister
valmir_top_artists = top3_artists_user[top3_artists_user["user"] == "Valmir"]
kymia_top_artists = top3_artists_user[top3_artists_user["user"] == "Kymia"]

# skapar två kolumner i Streamlit för att visa Valmirs och Kymias artister
left_col, right_col = st.columns(2)

# skriver rubriker för Valmir och Kymia kolumner
with left_col:
    st.subheader("Valmir's Top 3 Artists")
    
with right_col:
    st.subheader("Kymia's Top 3 Artists")

# loopar genom varje rad för Valmir och Kymia och visa deras top 3 artister
for (_, valmir_row), (_, kymia_row) in zip(valmir_top_artists.iterrows(), kymia_top_artists.iterrows()):
    # skapar två kolumner för att visa Valmirs och Kymias artistbilder
    left_col, right_col = st.columns(2)
    
    # visar Valmirs artists bilder med lyssningstid
    with left_col:
        if valmir_row["artistName"]:
            listening_hours = valmir_row["total_playtime_hours"]  # hämtar lyssningstiden för Valmir
            image_path = os.path.join(image_dir, f"{valmir_row['artistName']}.jpeg")  # sökväg för artistens bild

            # om bild finns -> visa den, annars skriv ut att bilden saknas
            if os.path.exists(image_path):
                st.image(image_path, caption=f"{valmir_row['artistName']} - {listening_hours:.2f} hours", width=150)
            else:
                st.write(f"Image missing for: {valmir_row['artistName']}")
    
    # visar Kymias artists bilder med lyssningstid
    with right_col:
        if kymia_row["artistName"]:
            listening_hours = kymia_row["total_playtime_hours"]  # hämta lyssningstiden för Kymia
            image_path = os.path.join(image_dir, f"{kymia_row['artistName']}.jpeg")  # sökvägen förr artistens bild
    
            # om bilden finns -> visa den, annars skriv ut att bilden saknas
            if os.path.exists(image_path):
                st.image(image_path, caption=f"{kymia_row['artistName']} - {listening_hours:.2f} hours", width=150)
            else:
                st.write(f"Image missing for: {kymia_row['artistName']}")





st.write('### Analysis Question 2.')
# Finns det låtar som spelats endast en gång av alla användare och aldrig igen?

# .size() för att räkna antal spelningar varje låt har
# grouby så att alla inspelningar för samma låt hamnar i samma grupp
# .reset_index behövs pga groupby för att göra det enklare att läsa av restulatet, då groupby skapar sina egna grupper
# utan reset_index används låtarna som index
play_counts = merged_data_sample.groupby('trackName').size().reset_index(name='play_count')

# Filtrera föregående så man får ut låtarna som spelats endast en gång bara
played_once = play_counts[play_counts['play_count'] == 1]

# För att vi ska hämta detaljer om låten då vi tappar all info utöver låtnamn pga föregående, såsom artistname och user
# då får vi tillbaka den kopplade infon med pd.merge 
played_once_info = pd.merge(played_once, merged_data_sample, on='trackName')

# Här får vi ut endast de unika låtarna med kopplad info och droppar duplicates ifall det skulle finnas några
unique_songs_played_once = played_once_info[['trackName', 'artistName', 'user']].drop_duplicates()

sns.set(style="darkgrid")
plt.figure(figsize=(6, 8)) # storleken på självaste figuren, bredd x höjd
user_colors = {'Valmir': 'forestgreen', 'Kymia': 'lightgreen'}
colors = unique_songs_played_once['user'].map(user_colors)
unique_songs_played_once['user'].value_counts().plot(kind='bar', color=[user_colors[user] for user in unique_songs_played_once['user'].value_counts().index]) # informationen som man får ut från diagrammet och vilken typ & färg
plt.title("Songs that were played only once", fontsize=14, fontweight='bold',color='white')
plt.ylabel("Number of songs", color='white', fontweight='bold')
plt.xlabel("Users", color='white', fontsize=12, fontweight='bold')
plt.xticks(rotation=0, fontsize=12, color='white') # så att namnen på användare visas rakt utan rotation
# plt.grid(axis='y', linestyle='--') # visas endast på y-axeln och rutnätet ritas som steckande linjer vilket förenklar läsningen av diagrammet
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())
print(unique_songs_played_once)




st.write('### Analysis Question 3.')

# extraherar timmen från kolumnen 'endTime' för att analysera vid vilken tid lyssning sker
merged_data_sample['hour'] = pd.to_datetime(merged_data_sample['endTime']).dt.hour

# klassificerar lyssningsaktivitet i 'Dagtid' (06:00-22:00) och 'Nattid' (22:00-06:00)
merged_data_sample['time_of_day'] = merged_data_sample['hour'].apply(
    lambda x: 'Dagtid' if 6 <= x < 22 else 'Nattid'
)

# skapar 2-timmars intervall för att gruppera lyssningsaktivitet
merged_data_sample['hour_bin'] = (merged_data_sample['hour'] // 2) * 2  # Rundar ned till närmaste jämna timme

# filtrerar data för varje användare separat
valmir_data = merged_data_sample[merged_data_sample['user'] == 'Valmir']
kymia_data = merged_data_sample[merged_data_sample['user'] == 'Kymia']

# Valmirs lyssningsdata efter 2-timmarsintervall och beräknar total lyssningstid
valmir_activity = (
    valmir_data.groupby('hour_bin')['msPlayed'].sum().reset_index()
)
# omvandlar total lyssningstid från millisekunder till minuter
valmir_activity['listening_time_minutes'] = valmir_activity['msPlayed'] / (1000 * 60)

# Kymias lyssningsdata efter 2-timmarsintervall och beräknar total lyssningstid
kymia_activity = (
    kymia_data.groupby('hour_bin')['msPlayed'].sum().reset_index()
)
# omvandlar total lyssningstid från millisekunder till minuter
kymia_activity['listening_time_minutes'] = kymia_activity['msPlayed'] / (1000 * 60)

# sätter upp stilen för visualiseringen
sns.set(style='darkgrid')
plt.figure(figsize=(12, 6))  # Sätter figurens storlek

# visualisering för Valmirs lyssningsaktivitet över dygnet
plt.plot(
    valmir_activity['hour_bin'], 
    valmir_activity['listening_time_minutes'], 
    label='Valmir', 
    color='forestgreen', 
    marker='o'
)

# visualisering för Kymias lyssningsaktivitet över dygnet
plt.plot(
    kymia_activity['hour_bin'], 
    kymia_activity['listening_time_minutes'], 
    label='Kymia', 
    color='lightgreen', 
    marker='o'
)

# anpassar utseendet på diagrammet
plt.title('Lyssningsaktivitet: Valmir vs Kymia', fontweight='bold', fontsize=18, color='white')
plt.xlabel('Tid på dygnet', fontweight='bold', fontsize=12)
plt.ylabel('Total lyssningstid (minuter)', fontweight='bold', fontsize=12, color='white')

# formaterar x-axelns etiketter för att visa varannan timme
plt.xticks(
    range(0, 24, 2), 
    labels=[f'{hour:02d}:00' for hour in range(0, 24, 2)], 
    rotation=45, 
    fontweight='bold', 
    fontsize=12
)

# lägger till en legend för att skilja på användarna
plt.legend()
# justerar rutnät och axelinställningar
plt.xticks(fontweight='bold', fontsize=12, color='white')
plt.grid(axis='y', linestyle='--', alpha=0.7, color='white')
plt.yticks(fontsize=12, color='white')

# sätter en mörk bakgrundsfärg för att passa temat
plt.gcf().patch.set_facecolor('#2e2e2e')
plt.tight_layout()
plt.show()


st.write('### Analysis Question 4.')
# top 5 mest spelade låtar (i timmar) respektive användare

# Grupperar datan för user och trackname, as_index ser till så dessa två kolumner inte blir till index
# .sum() för att summera den totala speltiden i ms
# Gruppera datan för att analysera data per kategori, i detta fall user o trackname och för att kunna använda funktioner som .sum()
top_songs = (merged_data.groupby(['user', 'trackName'], as_index=False)['msPlayed'].sum())

# Sorterar datan så alla rader för samma användare kommer tillsammans och får låtarna i ordning från mest till minst spelade
top_songs_sorted = top_songs.sort_values(['user', 'msPlayed'], ascending=[True, False])

# Grupperar datan för varje user vilket gör så vi får ut 5 låtar per användare
# Eftersom vi redan från föregående sorterat msPlayed i fallande ordning så får vi direkt ut de 5 mest spelade med .head(5) och inte just de 5 första raderna i csv filen
top_5_songs_per_user = top_songs_sorted.groupby('user').head(5)

plt.figure(figsize=(6, 4))
user_colors = {'Valmir': 'forestgreen', 'Kymia': 'lightgreen'} # för att själv bestämma färgerna då det inte går att göra det på det vanliga sättet med tanke på att det är två olika användare
for user in top_5_songs_per_user['user'].unique(): # Itererar så att vi får en lista med unika users och for user in ser till så vi kan arbeta seperat med varje user
    user_data = top_5_songs_per_user[top_5_songs_per_user['user'] == user] # filtrerar datan från föregående iteration för just en spicifik användare
    plt.bar(user_data['trackName'], # hämtar låtnamn
            user_data['msPlayed'] / (1000 * 60 * 60), # genom att dividera ms med (1000*60*60 = 3,6000,000 = en timme) omvanldas ms till timmar
            label=user, # användarna identifieras i legend
            color=user_colors[user])  
    # plt.bar är inuti loopen pga att det sker en iteration över unika användare och därav behöver vi unika staplar till varje användare
    # tar vi ut plt.bar från loopen så får vi ut ofiltrerad data där man inte kan skilja mellan användarna
sns.set(style="darkgrid")
plt.title('Top 5 most played songs', color='white', fontsize=14, fontweight='bold')
plt.xlabel('Song', color='white', fontsize=12, fontweight='bold')
plt.ylabel('Playtime in hours', color='white', fontweight='bold', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=12, color='white') # ha ser till så texten inte överlappar med andra texter och placeras rätt
plt.legend(title='Users') # den lilla rutan som förklrar färgerna för respektive användare
plt.grid(axis='x', alpha=0.6)
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())


st.write('### Analysis Question 5: Top 5 Most Shared Tracks') 

# SQL-query för att hämta de mest delade låtarna baserat på Kymia och Valmir
query = """
SELECT artistName, trackName,
       COUNT(DISTINCT user) AS shared_count,  -- räknar hur många unika användare som delat låten
       SUM(msPlayed) as total_playtime       -- beräknar total lyssningstid för låten
FROM spotify_data
GROUP BY artistName, trackName              -- grupperar resultaten efter artist och låttitel
HAVING shared_count > 1                      -- filtrerar bort låtar som bara delats av en användare
ORDER BY total_playtime DESC                 -- sorterar efter total lyssningstid i fallande ordning
"""

# hämtar resultatet från query och lagra det i en Pandas DataFrame
shared_data = pd.read_sql(query, con)

# konverterar total lyssningstid från millisekunder till minuter
shared_data['total_playtime_minutes'] = shared_data['total_playtime'] / (1000 * 60)

# väljer ut de 5 mest delade låtarna med högst total lyssningstid
topfive_shared_data = shared_data.head()

# Spotify-URL:er för de 5 mest delade låtarna
spotify_urls = {
    "DOPAMIN": "https://open.spotify.com/track/42Jv5Sboy8OnZMp5WAizL0?si=9181e3723df74e6c",
    "Get Jiggy": "https://open.spotify.com/track/6ydBZr2Iv7UzPG4bogi9i1?si=7c9abdb907434e83",
    "Motorväg": "https://open.spotify.com/track/62MEQ4Jh4IhYwqi6ItXARu?si=5975d2924b2f42aa",
    "DIAMANTER": "https://open.spotify.com/track/75yxwZbg4YmiAdXslkrLiM?si=59bb62b0ca13478f",
    "Who we are": "https://open.spotify.com/track/7B031z9YdKTBBhblIFsLqJ?si=a6c4931945d44351"
}

# lägger till en kolumn i DataFrame där varje låt matchas med sin Spotify-URL
topfive_shared_data['spotify_url'] = topfive_shared_data['trackName'].map(spotify_urls)

# visualisering av de top 5 delade låtarna
fig = px.bar(
    topfive_shared_data, 
    x="total_playtime_minutes",  
    y="trackName",                
    orientation='h',              
    text="total_playtime_minutes",
    color="total_playtime_minutes", 
    color_continuous_scale=["#004d00", "#80e0a7"], 
    labels={'total_playtime_minutes': 'Total Playtime (minutes)', 'trackName': 'Track Name'}, 
    title="Top 5 Most Shared Tracks by Playtime" 
)

st.plotly_chart(fig)
# dropdown meny i streamlit där låt kan väljas
selected_song = st.selectbox("🎵 Select a song to play:", topfive_shared_data["trackName"])
# hittar Spotify-URL för den valda låten
song_url = topfive_shared_data.loc[topfive_shared_data["trackName"] == selected_song, "spotify_url"].values[0]
st.markdown(f'<iframe src="{song_url}" width="0" height="0" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)




st.write('### Analysis Question 6.')
##Valmir
valmir_spotify['endTime'] = pd.to_datetime(valmir_spotify['endTime'])
my_artist = 'C.Gambino'
df_artist = valmir_spotify[valmir_spotify['artistName'] == my_artist]
df_artist['YearMonth'] = df_artist['endTime'].dt.to_period('M')
monthly_data = df_artist.groupby('YearMonth')['msPlayed'].sum()
monthly_data_in_minutes = monthly_data / 60000
monthly_data_in_minutes = pd.to_numeric(monthly_data_in_minutes, errors='coerce')
 
plt.figure(figsize=(12, 6))
monthly_data_in_minutes.plot(kind='bar', color='forestgreen')
plt.title('Monthly Listening Time for C.Gambino', fontsize=20, color='white', fontweight='bold')
plt.xlabel('Month', color='white', fontweight='bold', fontsize=12)
plt.ylabel('Total play time in minutes', color='white', fontweight='bold', fontsize=12)
plt.xticks(
    ticks=range(len(monthly_data_in_minutes)),
    labels=[str(period) for period in monthly_data_in_minutes.index],
    rotation=45,
    color='white')
plt.gca().text(1, 1.05, "User: Valmir", transform=plt.gca().transAxes, fontsize=18, color='white')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())


##Kymia
kymia_spotify['endTime'] = pd.to_datetime(kymia_spotify['endTime'])
my_artist = 'Makar'
df_artist = kymia_spotify[kymia_spotify['artistName'] == my_artist]
df_artist['YearMonth'] = df_artist['endTime'].dt.to_period('M')
monthly_data = df_artist.groupby('YearMonth')['msPlayed'].sum()
monthly_data_in_minutes = monthly_data / 60000
monthly_data_in_minutes = pd.to_numeric(monthly_data_in_minutes, errors='coerce')
 
plt.figure(figsize=(12, 6))
monthly_data_in_minutes.plot(kind='bar', color='lightgreen')
plt.title('Monthly Listening Time for Makar', fontsize=20, color='white', fontweight='bold')
plt.xlabel('Month', color='white', fontweight='bold', fontsize=12)
plt.ylabel('Total play time in minutes', color='white', fontweight='bold', fontsize=12)
plt.xticks(
    ticks=range(len(monthly_data_in_minutes)),
    labels=[str(period) for period in monthly_data_in_minutes.index],
    rotation=45,
    color='white')
plt.gca().text(1, 1.05, "User: Kymia", transform=plt.gca().transAxes, fontsize=18, color='white')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())



st.write('### Analysis Question 7.')
merged_data['endTime'] = pd.to_datetime(merged_data['endTime'])
merged_data['month'] = merged_data['endTime'].dt.to_period('M')
merged_data = merged_data[merged_data['endTime'] >= '2024-01-01']
valmir_data = merged_data[merged_data['user'] == 'Valmir'].sample(n=21650, random_state=42)
valmir_monthly = valmir_data.groupby('month').size()
kymia_monthly = merged_data[merged_data['user'] == 'Kymia'].groupby('month').size()

plt.figure(figsize=(12, 6))
plt.plot(valmir_monthly.index.astype(str), valmir_monthly, label='Valmir', marker='o', color='forestgreen')
plt.plot(kymia_monthly.index.astype(str), kymia_monthly, label='Kymia', marker='o', color='lightgreen')
plt.title('Play counts per month over a year', fontsize=20, color='white', fontweight='bold')
plt.xlabel('Month', color='white', fontweight='bold', fontsize=12)
plt.ylabel('Play count', color='white', fontweight='bold', fontsize=12)
plt.xticks(rotation=45, color='white')
plt.legend(title='Users')
plt.grid(axis='y', linestyle='--')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())



st.write('### Analysis Question 8.')
### Valmir
# slå ihop lyssningstiden för varje artist
artist_time = valmir_spotify.groupby('artistName')['msPlayed'].sum().sort_values(ascending=False)
# för att kunna identifiera topartisten och lyssningstiden för just denna artist
top_artist = artist_time.idxmax()
top_artist_time = artist_time.max()
# total lyssningstid
total_time = artist_time.sum()
# Topartistens andel av all speltid
top_artist_listening_time = (top_artist_time / total_time) * 100

lables = [top_artist, 'Others']
sizes = [top_artist_time, total_time - top_artist_time]
colors = ['forestgreen', 'lightgreen']
explode = (0.1, 0)
plt.figure(figsize=(7, 7))
plt.pie(sizes, explode=explode, labels=lables, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'color': 'white'})
plt.title(f"Share of total listening time: {top_artist} vs Others", fontsize=14, fontweight='bold', color='white')
plt.text(1.2, 1.2, "User: Valmir", fontsize=10, color='white')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())



### Kymia
artist_time = kymia_spotify.groupby('artistName')['msPlayed'].sum().sort_values(ascending=False)
top_artist = artist_time.idxmax()
top_artist_time = artist_time.max()
total_time = artist_time.sum()
top_artist_listening_time = (top_artist_time / total_time) * 100

lables = [top_artist, 'Others']
sizes = [top_artist_time, total_time - top_artist_time]
colors = ['lightgreen', 'forestgreen']
explode = (0.1, 0)
plt.figure(figsize=(7, 7))
plt.pie(sizes, explode=explode, labels=lables, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'color': 'white'})
plt.title(f"Share of total listening time: {top_artist} vs Others", fontsize=14, color='white')
plt.text(1.2, 1.2, "User: Kymia", fontsize=10, color='white')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())



st.write('### Analysis Question 9.')

###Valmir
C_Gambino = valmir_spotify[valmir_spotify['artistName'] == 'C.Gambino']
cg_ms = C_Gambino['msPlayed'].sum()
print(cg_ms)
Others = valmir_spotify[valmir_spotify['artistName'] != 'C.Gambino']
others_ms_artsiter = Others['msPlayed'].sum()
print(others_ms_artsiter)
total_ms = 5002514611 
total_others = total_ms / 60000
print(total_others)
total_cg_ms = 460817145 
total_ms_cg = total_cg_ms / 60000
print(total_ms_cg)

total_playtime = [total_ms_cg, total_others]
labels = ['C.Gambino', 'Others']
fig, ax = plt.subplots(figsize=(6, 8))
ax.bar(labels, total_playtime, color=['forestgreen', 'lightgreen'])
plt.xlabel('Artist', color='white', fontweight='bold', fontsize=12)
plt.ylabel('Playtime in minutes', color='white', fontweight='bold', fontsize=12)
plt.title('C.Gambino vs Other Artists', fontweight='bold', fontsize=14, color='white')
for i, value in enumerate(total_playtime):
    plt.text(i, value + 1000, f'{value:.0f} min', ha='center', fontsize=12, color='black')
ax.text(1.2, 1.2, "User: Valmir", fontsize=10, ha='right', transform=ax.transAxes, color='white')
plt.xticks(fontsize=12, color='white')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())



## Kymia
Makar = kymia_spotify[kymia_spotify['artistName'] == 'Makar']
makar_ms = Makar['msPlayed'].sum()
print(makar_ms)
Others = kymia_spotify[kymia_spotify['artistName'] != 'Makar']
others_ms_artsiter = Others['msPlayed'].sum()
print(others_ms_artsiter)
total_ms = 2557108282 
total_others = total_ms / 60000
print(total_others)
total_makar_ms = 189875904 
total_ms_makar = total_makar_ms / 60000
print(total_ms_makar)

total_playtime = [total_ms_makar, total_others]
labels = ['Makar', 'Others']
fig, ax = plt.subplots(figsize=(6, 8))
ax.bar(labels, total_playtime, color=['forestgreen', 'lightgreen'])
plt.xlabel('Artist', color='white', fontweight='bold', fontsize=12)
plt.ylabel('Playtime in minutes', color='white', fontweight='bold', fontsize=12)
plt.title('Makar vs Other Artists', fontsize=14, color='white', fontweight='bold')
for i, value in enumerate(total_playtime):
    plt.text(i, value + 1000, f'{value:.0f} min', ha='center', fontsize=12, color='black')
ax.text(1.2, 1.2,  "User: Kymia", fontsize=10, ha='right', transform=ax.transAxes, color='white')
plt.xticks(fontsize=12, color='white')
plt.yticks(fontsize=12, color='white')
plt.gcf().patch.set_facecolor('#2e2e2e')
st.pyplot(plt.gcf())




