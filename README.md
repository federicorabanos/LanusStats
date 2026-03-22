<p align="center">
  <img src="https://raw.githubusercontent.com/federicorabanos/LanusStats/main/lanusstats-logo.png">
</p>

LanusStats es una librería Python de scraping orientada al fútbol y los datos. Su objetivo es abstraer la complejidad de extraer información de múltiples plataformas en funciones simples que devuelven DataFrames de pandas listos para analizar o visualizar.

## Instalación

```bash
pip install LanusStats
```

Para actualizar a la última versión:

```bash
pip install --upgrade LanusStats
```

---

## Fuentes disponibles

- [FBRef](https://fbref.com/en/)
- [FotMob](https://www.fotmob.com/es)
- [SofaScore](https://sofascore.com/)
- [365Scores](https://www.365scores.com/es-mx/football)
- [Transfermarkt](https://transfermarkt.com.ar/)

---

## Cómo se usa

### Funciones generales

Para saber qué páginas tienen módulo disponible:

```python
import LanusStats as ls

ls.get_available_pages()
```

Para ver las ligas disponibles de una página:

```python
ls.get_available_leagues(page)
```

Para ver las temporadas disponibles de una liga:

```python
ls.get_available_season_for_leagues(page, league)
```

---

## FBRef

```python
import LanusStats as ls

fbref = ls.Fbref()
```

### Estadísticas de equipos

Scrapear una estadística específica para todos los equipos de una liga:

```python
fbref.get_teams_season_stats('gca', 'Copa de la Liga', season='2024', save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```

- **`change_columns_names`**: renombra columnas de tipo `Unnamed: X`
- **`add_page_name`**: agrega el nombre de la estadística como prefijo a las columnas (útil al hacer merge entre tablas)
- **`save_csv`**: exporta el resultado a un archivo CSV
- **`stats_vs`**: incluye las estadísticas "en contra" que FBRef provee

Para obtener estadísticas a favor y en contra en un solo paso:

```python
fbref.get_vs_and_teams_season_stats('gca', 'Copa de la Liga', season='2024', save_excel=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```

Devuelve dos DataFrames (a favor y en contra). **`save_excel`** los exporta en un `.xlsx` con dos hojas.

Para scrapear todas las estadísticas disponibles de una liga:

```python
fbref.get_all_teams_season_stats('Copa de la Liga', '2024', save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```

### Estadísticas de jugadores

```python
fbref.get_player_season_stats('gca', 'Copa de la Liga', save_csv=False, add_page_name=False)
```

Para scrapear todas las estadísticas de jugadores en una sola llamada:

```python
fbref.get_all_player_season_stats("Copa de la Liga", "2024", save_csv=False, add_page_name=False)
```

### Estadísticas de un partido

```python
fbref.get_general_match_team_stats("https://fbref.com/en/matches/77d7e2d6/Arsenal-Luton-Town-April-3-2024-Premier-League")
```

### Tabla de posiciones

```python
fbref.get_tournament_table("https://fbref.com/en/comps/9/Premier-League-Stats")
```

---

## FotMob

```python
import LanusStats as ls

fotmob = ls.FotMob()
```

### Tablas de liga

Obtener las tablas de una temporada (posiciones, xG, etc.):

```python
fotmob.get_season_tables("Premier League", "2022/2023", "xg")
```

### Estadísticas de temporada

Estadísticas de jugadores:

```python
fotmob.get_players_stats_season("Premier League", "2023/2024", "expected_assists_per_90")
```

Estadísticas de equipos:

```python
fotmob.get_teams_stats_season("Premier League", "2023/2024", "poss_won_att_3rd_team")
```

### Datos de un partido

El `match_id` es el número al final de la URL. Ejemplo: `https://www.fotmob.com/es/matches/afc-bournemouth-vs-manchester-united/2yrx85#4193851` → `4193851`

Mapa de tiros:

```python
fotmob.get_match_shotmap(4193851)
```

Estadísticas generales de los equipos:

```python
fotmob.get_general_match_stats(4193851)
```

### Datos de un jugador

El `player_id` es el número en la URL del jugador. Ejemplo: `https://www.fotmob.com/es/players/1203665/alejandro-garnacho` → `1203665`

Los parámetros de temporada y competición corresponden a la posición en el dropdown de FotMob, comenzando desde `0`.

Mapa de tiros del jugador:

```python
fotmob.get_player_shotmap("1", "0", 1203665)
```

Percentiles:

```python
fotmob.get_player_percentiles("1", "0", 1203665)
```

Estadísticas de temporada:

```python
fotmob.get_player_season_stats("1", "0", 1203665)
```

Toda la información disponible del jugador:

```python
fotmob.get_player_data(1203665)
```

---

## 365Scores

```python
import LanusStats as ls

threesixfivescores = ls.ThreeSixFiveScores()
```

La URL de un partido tiene la forma: `https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824`

### Estadísticas de liga

Top performers de distintas estadísticas para la temporada actual de una liga:

```python
threesixfivescores.get_league_top_players_stats(league="Argentina Liga Profesional")
```

- **`league`**: liga disponible en `get_available_leagues("365Scores")`

Devuelve un DataFrame con jugadores, posiciones, estadísticas y valores.

### Datos de un partido

Mapa de tiros (si el partido lo tiene):

```python
threesixfivescores.get_match_shotmap("https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824")
```

Devuelve un DataFrame con cada disparo, coordenadas, xG, xGoT y resultado del tiro. Lanza `MatchDoesntHaveInfo` si el partido no tiene mapa de tiros.

Estadísticas generales de los equipos:

```python
threesixfivescores.get_match_general_stats("https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824")
```

Devuelve un DataFrame con las estadísticas del partido por equipo (posesión, tiros, pases, etc.).

Estadísticas de tiempo de juego (tiempo efectivo, tiempo perdido, etc.):

```python
threesixfivescores.get_match_time_stats("https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824")
```

Lanza `MatchDoesntHaveInfo` si el partido no tiene esta información.

### Datos de jugadores en un partido

Información general de los jugadores que participaron:

```python
threesixfivescores.get_players_info("https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824")
```

Mapa de calor de un jugador en un partido:

```python
threesixfivescores.get_player_heatmap_match(player="Lautaro Martinez", match_url="https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824")
```

- **`player`**: nombre del jugador tal como figura en 365Scores

Devuelve una imagen PIL del mapa de calor.

---

## SofaScore

```python
import LanusStats as ls

sofascore = ls.SofaScore()
```

### Datos de un partido

El `match_url` es la URL completa del partido. Ejemplo: `https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532`

Mapa de tiros:

```python
sofascore.get_match_shotmap("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532", save_csv=False)
```

Estadísticas de jugadores (devuelve una lista: `[0]` local, `[1]` visitante):

```python
sofascore.get_players_match_stats("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")
```

Posiciones promedio (devuelve una lista: `[0]` local, `[1]` visitante):

```python
sofascore.get_players_average_positions("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")
```

Lineups:

```python
sofascore.get_lineups("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")
```

Mapa de calor de un jugador en un partido:

```python
sofascore.get_player_heatmap("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532", "Alejandro Garnacho")
```

El nombre del jugador debe ser exactamente como lo muestra SofaScore.

Eventos de un jugador en un partido:

```python
sofascore.get_player_match_events("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532", "Alejandro Garnacho", events=None)
```

- **`events`**: puede ser una lista con uno o más de `['passes', 'ball-carries', 'dribbles', 'defensive']`. Si es `None`, devuelve todos.

### Estadísticas de jugador por temporada

Mapa de calor de un jugador en un torneo:

```python
sofascore.get_player_season_heatmap("Argentina Liga Profesional", "2024", 832213)
```

El tercer parámetro es el ID del jugador, visible en su URL: `https://www.sofascore.com/player/joaquin-pereyra/832213`

Estadísticas de jugadores de un torneo completo:

```python
sofascore.scrape_league_stats(league="Argentina Liga Profesional", season="2024", save_csv=False, accumulation="per90", selected_positions=["Goalkeepers"])
```

- **`league`**: liga disponible en `get_available_leagues("Sofascore")`
- **`season`**: temporada disponible en `get_available_season_for_leagues("Sofascore", league)`
- **`save_csv`**: exporta el resultado a CSV
- **`accumulation`**: forma de pedir las estadísticas. Valores: `total`, `per90`, `perMatch`
- **`selected_positions`**: grupo de jugadores. Valores: `['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']`

---

## Transfermarkt

```python
import LanusStats as ls

transfermarkt = ls.Transfermarkt()
```

### Valoraciones de planteles

```python
transfermarkt.get_league_teams_valuations(league="Primera Division Argentina", season="2024")
```

- **`league`**: liga disponible en `get_available_leagues("Transfermarkt")`
- **`season`**: temporada (por ejemplo: `"2024"` o `"2023/2024"`)

### Plantel de un equipo

```python
transfermarkt.scrape_players_for_teams(team_name="Club Atletico Lanus", team_id="333", season="2024")
```

El `team_name` y `team_id` se sacan de la URL del equipo. Ejemplo: `https://www.transfermarkt.com.ar/club-atletico-lanus/startseite/verein/333`

- **`team_name`**: nombre respetando la URL, sin guiones medios
- **`team_id`**: número al final de la URL

### Datos de un jugador

El `player_id` se saca de la URL del jugador. Ejemplo: `https://www.transfermarkt.com.ar/marcelino-moreno/profil/spieler/456617` → `456617`

Historial de transferencias:

```python
transfermarkt.get_player_transfer_history(player_id="456617")
```

Evolución del valor de mercado:

```python
transfermarkt.get_player_market_value(player_id="456617")
```

Posiciones jugadas:

```python
transfermarkt.get_player_positions_played(player_name="Marcelino Moreno", player_id="456617")
```

Datos de penales para arqueros:

```python
transfermarkt.get_keepers_penalty_data(player_name="Emiliano Martinez", player_id="111873")
```

Partidos jugados:

```python
transfermarkt.get_player_played_data(player_name="Emiliano Martinez", player_id="111873")
```

---

## Visualizaciones

Las visualizaciones combinan el scraping y el ploteo en una sola función, listas para usar o customizar.

Match momentum de un partido de FotMob:

```python
ls.visualizations.fotmob_match_momentum_plot(match_id=4193851, save_fig=False)
```

Hexbin de tiros de un jugador en FotMob:

```python
ls.visualizations.fotmob_hexbin_shotmap('La Liga', '2023/2024', 711231)
```

- **`player_id`**: ID del jugador en FotMob. Ejemplo: `https://www.fotmob.com/es/players/711231/gorka-guruzeta` → `711231`

Mapa de tiros de un partido de 365Scores:

```python
ls.visualizations.threesixfivescores_match_shotmap('https://www.365scores.com/es-mx/football/match/copa-sudamericana-389/lanus-metropolitanos-fc-869-13830-389#id=4072240')
```

Evolución del valor de mercado según Transfermarkt:

```python
ls.visualizations.transfermarkt_player_market_value(player_id='111873')
```

Eventos de un jugador en un partido de SofaScore:

```python
ls.visualizations.sofascore_plot_match_events('https://www.sofascore.com/es/football/match/banfield-racing-club/pobsuob#id:15270114', 'Santiago Sosa', events=None, dashboard=True)
```

- **`dashboard=True`**: agrupa todas las figuras en una sola imagen

---

## Créditos

- [Owen de ScraperFC](https://github.com/oseymour/ScraperFC)
- [Ben Griffis](https://github.com/griffisben/Soccer-Analyses)
- [McKay Johns](https://www.youtube.com/@McKayJohns)

---

## Más contenido

Unite al [Discord](https://discord.gg/3Nk7Pe6mb8) de la comunidad hispanohablante de fútbol y datos.

Para ver todo el contenido de LanusStats: [linktr.ee/lanusstats](https://linktr.ee/lanusstats)
