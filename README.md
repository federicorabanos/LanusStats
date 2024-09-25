<p align="center">
  <img src="https://raw.githubusercontent.com/federicorabanos/LanusStats/main/lanusstats-logo.png">
</p>

Esto es la líbreria de LanusStats, un lugar en donde se intentará hacerle la vida más facíla toda persona que este interesada en el ámbito del fútbol
y los datos. Se van a tener recursos de todo tipo, desde scrapeo de información de distintas páginas/lugares hasta la posibilidad de hacer visualizaciones
con solo una función.

Para instalarla, solamente tenes que correr esto en algun consola de comando:
```bash
pip install LanusStats
```
En caso de querer actualizarla a la versión más readasdasdciente:
```bash
pip install --upgrade LanusStats
```

La libreria consta de distintos módulos para sacar información de estas páginas:

* [FBRef](https://fbref.com/en/)
* [FotMob](https://www.fotmob.com/es)
* [SofaScore](https://sofascore.com/)
* [365Scores](https://www.365scores.com/es-mx/football)
* [Transfermarkt](https://transfermarkt.com.ar/)

---

# Cómo se usa?

## General

Para saber que páginas contienen un módulo para scrapear, podes hacer:
```bash
get_available_pages()
```
Para saber que ligas tienen las páginas de la función anterior, podes hacer:
```bash
get_available_leagues(page)
```
Para saber que temporadas tienen las ligas de las páginas de la función anterior, podes hacer:
```bash
get_available_season_for_leagues(page, league)
```

## [Fbref](https://github.com/federicorabanos/LanusStats/blob/main/LanusStats/fbref.py)

Importo la clase de esta manera:
```bash
import LanusStats as ls  
fbref = ls.Fbref()
```
Todas las funciones deben tener el fbref. delante de ellas

* Para scrapear información de los equipos se puede usar ```get_teams_season_stats```. Ejemplo:
```bash
get_teams_season_stats('gca', 'Copa de la Liga', season='2024', save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```
**change_columns_names** te permite ponerle el nombre a columnas de tipo Unnamed: 0
**add_page_name** le agrega el nombre de la página a las columnas, hay veces que se repiten los nombres entre páginas  
**save_csv** exporta la tabla a un csv  
**stats_vs** te permite scrapear las tablas de estadísticas vs que en Fbref está la posibilidad  

Si esto lo queres hacer todo junto, podes usar ```get_vs_and_teams_season_stats```. Ejemplo:
```bash
get_vs_and_teams_season_stats('gca', 'Copa de la Liga', season='2024', save_excel=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```
Esto te devuelve dos DataFrames, uno para las estadísticas a favor y otro en contra.
**save_excel** te permite exportarlo a un .xlsx que contiene dos páginas.

Para terminar, con ```get_all_teams_season_stats``` podes scrapear TODAS las estadísticas que esten en la pagina. Ejemplo:
```bash
get_all_teams_season_stats('Copa de la Liga', '2024', save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```

* Para scrapear data de los jugadores se pueden usar:
```bash
get_player_season_stats('gca', 'Copa de la Liga', save_csv=False, add_page_name=False)
```
Y si quiero scrapear todas las estadísticas en una
```bash
get_all_player_season_stats("Copa de la Liga", "2024", save_csv=False, add_page_name=False)
```

* Del perfil de un jugar se puede sacar los percentiles y las similutdes (si las tiene)
```bash
get_player_percentiles("https://fbref.com/en/players/bc7dc64d/Bukayo-Saka")
get_player_similarities("https://fbref.com/en/players/bc7dc64d/Bukayo-Saka")
```

* De un partido en particular se puede sacar los tiros y las estadísticas generales (si las tiene)
```bash
get_match_shots("https://fbref.com/en/matches/77d7e2d6/Arsenal-Luton-Town-April-3-2024-Premier-League")
get_general_match_team_stats("https://fbref.com/en/matches/77d7e2d6/Arsenal-Luton-Town-April-3-2024-Premier-League")
```

* Si queres scrapear la tabla de posiciones de una liga, podes:
```bash
get_tournament_table("https://fbref.com/en/comps/9/Premier-League-Stats")
```

## [FotMob](https://github.com/federicorabanos/LanusStats/blob/main/LanusStats/fotmob.py)
```bash
import LanusStats as ls  
fotmob = ls.FotMob()
```

* Para obtener las distintas tablas que pueden haber en la UI de Fotmob ([ejemplo](https://www.fotmob.com/es/leagues/47/table/premier-league)) pueden usar:

```bash
get_season_tables("Premier League", "2022/2023", "xg")
```

* Para obtener información de estadísticas de una temporada ([ejemplo](https://www.fotmob.com/es/leagues/47/stats/premier-league)):

** De los jugadores puedes usar:

```bash
get_players_stats_season("Premier League", "2023/2024", "expected_assists_per_90")
```

** De los equipos puedes usar:

```bash
get_teams_stats_season("Premier League", "2023/2024", "poss_won_att_3rd_team")
```

* De un partido ([ejemplo](https://www.fotmob.com/es/matches/afc-bournemouth-vs-manchester-united/2yrx85#4193851)) la información que puedes sacar es de:

** Mapa de tiros:
```bash
get_match_shotmap(4193851)
```

** Estadísticas generales de los equipos:
```bash
get_general_match_stats(4193851)
```

Aclaración: El id de parametro es el que se encuentra en la url, ejemplo: https://www.fotmob.com/es/matches/afc-bournemouth-vs-manchester-united/2yrx85#4193851

* También puedes obtener información de un jugador:

** Mapa de tiros ([ejemplo](https://www.fotmob.com/es/players/1203665/alejandro-garnacho)):
```bash
get_player_shotmap("1", "0", 1203665)
```
El 3º parametro es el id que se encuentra en la url, ejemplo: https://www.fotmob.com/es/players/1203665/alejandro-garnacho  
El primer y segundo parametro salen del dropdown de la página de FotMob:
- El primero es la posición de la temporada en el dropdown, arrancando desde el 0. Es decir, si quiero de la primera temporada que aparece en el dropdown, el valor será 0, si es de la 2º, será 1 y así sucesivamente.  
- El segundo es la posición de la competición dentro de una temporada. La que aparezca primera será 0 y asi.

## [365 Scores](https://github.com/federicorabanos/LanusStats/blob/main/LanusStats/threesixfivescores.py)
```bash
import LanusStats as ls  
threesixfivescores = ls.ThreeSixFiveScores()
```

## [SofaScore](https://github.com/federicorabanos/LanusStats/blob/main/LanusStats/sofascore.py)
```bash
import LanusStats as ls  
sofascore = ls.SofaScore()
```

* De un partido ([ejemplo](https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532)) podes sacar los disparos:

```bash
get_match_shotmap("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532", save_csv=True)
```
**match_url** se pone la url entera de la página del partido de Sofascore.  
**save_csv** si guardas el dataframe que te devuelve en un csv

* También de un partido podes sacar las estadísticas de los jugadores:
```bash
get_players_match_stats("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")
```
**match_url** se pone la url entera de la página del partido de Sofascore.  
Aclaración, te devuelve una lista de dataframes, el primero (ó [0]) es del local y el segundo ó [1] es del visitante  

* También de un partido podes sacar las posiciones promedio:
```bash
get_players_average_positions("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")
```
**match_url** se pone la url entera de la página del partido de Sofascore.  
Aclaración, te devuelve una lista de dataframes, el primero (ó [0]) es del local y el segundo ó [1] es del visitante  

* También podes obtener la información de los lineups:
```bash
get_lineups("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")
```

* Por último dentro de un partido podes sacar el mapa de calor de cada uno dentro del partido:
```bash
get_player_heatmap("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532", "Alejandro Garnacho")
```
Aclaración: el nombre del jugador debe ser tal cual lo muestra SofaScore.

* Se puede sacar el mapa de calor de un jugador de cada torneo, si es que lo tiene:
```bash
get_player_season_heatmap("Argentina Liga Profesional", "2024", 832213)
```
La liga y la temporada salen de las funciones generales ya vistas y el tercer parámetro es el id del jugador que se puede ver en la página de jugador: https://www.sofascore.com/player/joaquin-pereyra/832213. Es el número al final del link

* Por último, se pueden scrapear las estadísticas de los jugadores en un [torneo](https://www.sofascore.com/tournament/football/argentina/liga-profesional-de-futbol/155#id:57478):
```bash
scrape_league_stats(league="Argentina Liga Profesional", season="2024", save_csv=False, accumulation="per90", selected_positions= ["Goalkeepers"])
```
**league** Liga habilitada en get_available_leagues("Sofascore")
**season** Temporada habilitada en get_available_season_for_leagues("Sofascore", league)
**save_csv** si guardar el dataframe en un csv o no
**accumulation** como pedir las estadísticas. Valores posibles: total, per90, perMatch
**selected_positions** que grupo de jugadores traer. Valores posibles: ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']

## [Transfermarkt](https://github.com/federicorabanos/LanusStats/blob/main/LanusStats/transfermarkt.py)

```bash
import LanusStats as ls  
transfermarkt = ls.Transfermarkt()
```

* Información de la valuación de los planteles (general):
```bash
get_league_teams_valuations(league="Primera Division Argentina", season="2024")
```
**league (str)**: Liga que este en get_possible_leagues_for_page("Transfermarkt")  
**season(str)**: Cualquier temporada que este en la interfaz de Transfermarkt (por ejemplo: 2024, 2023/2024)  

* Información de los planteles en particular
```bash
scrape_players_for_teams(team_name="Club Atletico Lanus", team_id="333", season="2024")
```
Ejemplo: https://www.transfermarkt.com.ar/club-atletico-lanus/startseite/verein/333  
**team_name (str)** Nombre respetando la URL (Club Atletico Lanus). No poner guiones medios.  
**team_id (str)** ID que está al final de la URL (333)
**season(str)**: Cualquier temporada que este en la interfaz de Transfermarkt (por ejemplo: 2024, 2023/2024)  

* Información de jugadores (ejemplo de URL: https://www.transfermarkt.com.ar/marcelino-moreno/profil/spieler/456617). Transferencias, posiciones jugadas, partidos jugadores, valoraciones, etc.:
```bash
get_player_transfer_history(player_id="456617")
```
**player_id (str)** ID del jugador, se saca de la URL.  

```bash
get_player_market_value(player_id="456617")
```
**player_id (str)** ID del jugador, se saca de la URL.  

```bash
get_player_positions_played(player_name="Marcelino Moreno", player_id="456617")
```
**player_name (str)** Nombre del jugador.  
**player_id (str)** ID del jugador, se saca de la URL.  

```bash
get_keepers_penalty_data(player_name="Emiliano Martinez", player_id="111873")
```
**player_name (str)** Nombre del jugador (arquero).  
**player_id (str)** ID del jugador, se saca de la URL.  


```bash
get_player_played_data(player_name="Emiliano Martinez", player_id="111873")
```
**player_name (str)** Nombre del jugador.  
**player_id (str)** ID del jugador, se saca de la URL.  


## [Visualizaciones](https://github.com/federicorabanos/LanusStats/blob/main/LanusStats/visualizations.py)

Hay visualizaciones seteadas para hacer desde una función que scrapean usando las funciones de la libreria y visualizan la información de cierta manera para que se puede customizar o usar derecho.

* Plotear percentiles de los jugadores de Fbref en un grafico de MPLSoccer

```bash
ls.visualizations.fbref_plot_player_percentiles(path="https://fbref.com/en/players/058c938c/Marcelino-Moreno", image=None, chart_stats = ["shots", "passes", "defense"], save_image=True, name_extra = "- Lanus", credit_extra= "")
```

**path** Link del jugador en Fbref  
**image** path de una imagen que quieras usar, se recomienda pasarla por https://crop-circle.imageonline.co/  
**chart_stats** agregar rectangulos y nombres de las estadísticas al gráfico  
**save_image** si guarda el png de la visualización  
**name_extra** agregarle un string al título  
**credit_extra** agregarle un string a los créditos  

Ejemplo: ![Marcelino Moreno fbref percentile plot](https://github.com/federicorabanos/LanusStats/assets/101477588/d2c41dd6-8271-498f-8849-73ee093529b4)


* Plotear match momentum de FotMob

```bash
ls.visualizations.fotmob_match_momentum_plot(match_id=4193851, save_fig=False)
```

**match_id** es el que se encuentra en la url, ejemplo: https://www.fotmob.com/es/matches/afc-bournemouth-vs-manchester-united/2yrx85#4193851  
**save_fig** si guardo la imagen o no

* Plotear hexbins de tiros de jugadores de FotMob
```bash
ls.visualizations.fotmob_hexbin_shotmap('La Liga', '2023/2024', 711231)
```
**league** Liga habilitada en get_available_leagues("Fotmob")  
**season** Temporada habilitada.  
**player_id** Id del jugador de FotMob. Ejemplo: https://www.fotmob.com/es/players/711231/gorka-guruzeta el número de la url es el id del jugador.

* Plotear un mapa de disparos de un partido de 365Scores
```bash
ls.visualizations.threesixfivescores_match_shotmap('https://www.365scores.com/es-mx/football/match/copa-sudamericana-389/lanus-metropolitanos-fc-869-13830-389#id=4072240')
```
Hay que poner la url del partido entera. Va a devolver info si es que tiene un mapa de tiros el partido.

* Plotear valor de mercado según Transfermarkt a lo largo de la carrera:
```bash
ls.visualizations.transfermarkt_player_market_value(player_id='111873')
```

---

# Créditos

Quiero agradecer a las influencias y ayudas que tuve para armar todo esto:

* [Owen de ScraperFC](https://github.com/oseymour/ScraperFC)
* [Ben Griffis](https://github.com/griffisben/Soccer-Analyses)
* [McKay Johns](https://www.youtube.com/@McKayJohns)

---

# Más contenido

Unite al [Discord](https://discord.gg/3Nk7Pe6mb8) hecho para la comunidad hispano hablante de fútbol y datos (cualquiera está invitado igual)

Para ver todo el contenido de LanusStats, te dejo este [link](https://linktr.ee/lanusstats)
