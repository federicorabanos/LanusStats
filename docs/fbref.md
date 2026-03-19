# FBRef

Módulo para scrapear datos de [FBRef](https://fbref.com/en/). Usa `requests` + `BeautifulSoup` + `pandas.read_html()` sobre el HTML estático del sitio.

```python
import LanusStats as ls

fbref = ls.Fbref()
```

---

## Stats de equipos

### `get_teams_season_stats()`

Scrapea la tabla de estadísticas de equipos para una liga y temporada.

```python
df = fbref.get_teams_season_stats(
    stat="gca",
    league="Copa de la Liga",
    season="2024",
    save_csv=False,
    stats_vs=False,
    change_columns_names=False,
    add_page_name=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `stat` | `str` | — | Estadística a scrapear (ver lista abajo) |
| `league` | `str` | — | Liga disponible en `get_available_leagues("FBRef")` |
| `season` | `str` | `None` | Temporada. Si es `None`, trae la más reciente |
| `save_csv` | `bool` | `False` | Exporta el DataFrame a `.csv` |
| `stats_vs` | `bool` | `False` | Trae la tabla "vs" (estadísticas en contra) en lugar de la normal |
| `change_columns_names` | `bool` | `False` | Renombra columnas del tipo `Unnamed: X` |
| `add_page_name` | `bool` | `False` | Agrega el nombre del stat como prefijo a las columnas (útil al hacer merge entre tablas) |

**Retorna:** `pd.DataFrame`

---

### `get_vs_and_teams_season_stats()`

Scrapea las tablas de estadísticas a favor **y** en contra en una sola llamada.

```python
df_for, df_vs = fbref.get_vs_and_teams_season_stats(
    stat="gca",
    league="Copa de la Liga",
    season="2024",
    save_excel=False,
    change_columns_names=False,
    add_page_name=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `stat` | `str` | — | Estadística a scrapear |
| `league` | `str` | — | Liga disponible en `get_available_leagues("FBRef")` |
| `season` | `str` | `None` | Temporada |
| `save_excel` | `bool` | `False` | Exporta ambas tablas a un `.xlsx` con dos hojas |
| `change_columns_names` | `bool` | `False` | Renombra columnas `Unnamed: X` |
| `add_page_name` | `bool` | `False` | Agrega prefijo con el nombre del stat |

**Retorna:** `tuple[pd.DataFrame, pd.DataFrame]` — `(df_a_favor, df_en_contra)`

---

### `get_all_teams_season_stats()`

Scrapea **todas** las estadísticas disponibles para equipos en una liga y temporada, y las combina en un solo DataFrame.

```python
df = fbref.get_all_teams_season_stats(
    league="Copa de la Liga",
    season="2024",
    save_csv=False,
    stats_vs=False,
    change_columns_names=False,
    add_page_name=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `league` | `str` | — | Liga disponible en `get_available_leagues("FBRef")` |
| `season` | `str` | — | Temporada |
| `save_csv` | `bool` | `False` | Exporta a `.csv` |
| `stats_vs` | `bool` | `False` | Trae las tablas "vs" |
| `change_columns_names` | `bool` | `False` | Renombra columnas `Unnamed: X` |
| `add_page_name` | `bool` | `False` | Agrega prefijo con el nombre del stat a cada columna |

**Retorna:** `pd.DataFrame`

---

## Stats de jugadores

### `get_player_season_stats()`

Scrapea estadísticas de jugadores para una liga, temporada y stat específico.

```python
df = fbref.get_player_season_stats(
    stat="gca",
    league="Copa de la Liga",
    season="2024",
    save_csv=False,
    add_page_name=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `stat` | `str` | — | Estadística a scrapear |
| `league` | `str` | — | Liga disponible en `get_available_leagues("FBRef")` |
| `season` | `str` | `None` | Temporada. Si es `None`, trae la más reciente |
| `save_csv` | `bool` | `False` | Exporta a `.csv` |
| `add_page_name` | `bool` | `False` | Agrega prefijo con el nombre del stat a las columnas |

**Retorna:** `pd.DataFrame`

---

### `get_all_player_season_stats()`

Scrapea **todas** las estadísticas de jugadores para una liga y temporada.

```python
df = fbref.get_all_player_season_stats(
    league="Copa de la Liga",
    season="2024",
    save_csv=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `league` | `str` | — | Liga disponible en `get_available_leagues("FBRef")` |
| `season` | `str` | — | Temporada |
| `save_csv` | `bool` | `False` | Exporta a `.csv` |

**Retorna:** `pd.DataFrame`

---

### `get_player_percentiles()`

Scrapea los percentiles de un jugador desde su página de perfil en FBRef.

```python
df = fbref.get_player_percentiles(
    path="https://fbref.com/en/players/bc7dc064/Lionel-Messi"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `path` | `str` | URL completa de la página del jugador en FBRef |

**Retorna:** `pd.DataFrame`

---

### `get_player_similarities()`

Obtiene la tabla de jugadores similares desde la página de un jugador.

```python
df = fbref.get_player_similarities(
    path="https://fbref.com/en/players/bc7dc064/Lionel-Messi"
)
```

**Retorna:** `pd.DataFrame`

---

## Datos de partidos

### `get_match_shots()`

Scrapea el mapa de tiros de un partido.

```python
df = fbref.get_match_shots(
    path="https://fbref.com/en/matches/77d7e2d6/Arsenal-Luton-Town-April-3-2024-Premier-League"
)
```

**Retorna:** `pd.DataFrame`

---

### `get_general_match_team_stats()`

Scrapea las estadísticas generales de los equipos en un partido.

```python
df_local, df_visitante = fbref.get_general_match_team_stats(
    path="https://fbref.com/en/matches/77d7e2d6/Arsenal-Luton-Town-April-3-2024-Premier-League"
)
```

**Retorna:** `tuple[pd.DataFrame, pd.DataFrame]` — `(local, visitante)`

---

## Tabla de posiciones

### `get_tournament_table()`

Scrapea la tabla de posiciones de una liga.

```python
df = fbref.get_tournament_table(
    path="https://fbref.com/en/comps/9/Premier-League-Stats"
)
```

**Retorna:** `pd.DataFrame`

---

## Estadísticas disponibles (`stat`)

Usá `fbref.possible_stats` para ver la lista completa. Algunos valores comunes:

| Valor | Descripción |
|-------|-------------|
| `shooting` | Tiros |
| `passing` | Pases |
| `passing_types` | Tipos de pases |
| `gca` | Goal-creating actions |
| `defense` | Acciones defensivas |
| `possession` | Posesión |
| `misc` | Estadísticas varias |
| `keeper` | Estadísticas de arqueros |

```python
# Ver todos los stats disponibles
print(fbref.possible_stats)
```
