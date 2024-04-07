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
En caso de querer actualizarla a la versión más reciente:
```bash
pip install --upgrade LanusStats
```

La libreria consta de distintos módulos para sacar información de estas páginas:

* [FBRef](https://fbref.com/en/)
* [FotMob](https://www.fotmob.com/es)
* [SofaScore](https://sofascore.com/)
* [365Scores](https://www.365scores.com/es-mx/football)

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
get_all_teams_season_stats('gca', 'Copa de la Liga', save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False)
```

* Para scrapear data de los jugadores se pueden usar:
```bash
get_player_season_stats('gca', 'Copa de la Liga', save_csv=False, add_page_name=False)
```
Y si quiero scrapear todas las estadísticas en una
```bash
get_all_player_season_stats("Copa de la Liga", save_csv=False, add_page_name=False)
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

## FotMob

## SofaScore

## 365 Scores

## Visualizaciones

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
