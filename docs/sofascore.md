# SofaScore

Módulo para scrapear datos de [SofaScore](https://www.sofascore.com/) usando su API interna (no documentada oficialmente).

```python
import LanusStats as ls

sofascore = ls.SofaScore()
```

---

## Datos de partidos

La mayoría de los métodos reciben la URL completa del partido. Ejemplo:
`https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532`

### `get_match_shotmap()`

Obtiene el mapa de tiros de un partido.

```python
df = sofascore.get_match_shotmap(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532",
    save_csv=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `match_url` | `str` | — | URL completa del partido en SofaScore |
| `save_csv` | `bool` | `False` | Exporta el DataFrame a `.csv` |

**Retorna:** `pd.DataFrame`

---

### `get_players_match_stats()`

Obtiene las estadísticas individuales de todos los jugadores en un partido.

```python
df_local, df_visitante = sofascore.get_players_match_stats(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532"
)
```

**Retorna:** `list[pd.DataFrame]` — `[0]` es local, `[1]` es visitante.

---

### `get_players_average_positions()`

Obtiene las posiciones promedio de los jugadores durante el partido.

```python
df_local, df_visitante = sofascore.get_players_average_positions(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532"
)
```

**Retorna:** `list[pd.DataFrame]` — `[0]` es local, `[1]` es visitante.

---

### `get_lineups()`

Obtiene las alineaciones completas del partido.

```python
data = sofascore.get_lineups(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532"
)
```

**Retorna:** `dict` con las alineaciones de ambos equipos.

---

### `get_match_momentum()`

Obtiene los valores del gráfico de momentum del partido.

```python
df = sofascore.get_match_momentum(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532"
)
```

**Retorna:** `pd.DataFrame`

---

### `get_match_data()`

Obtiene toda la información general del partido.

```python
data = sofascore.get_match_data(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532"
)
```

**Retorna:** `dict`

---

## Heatmaps y eventos de jugadores en partidos

Para estos métodos, el nombre del jugador debe escribirse **exactamente como aparece en SofaScore**.

### `get_player_heatmap()`

Obtiene las coordenadas del heatmap de un jugador en un partido.

```python
df = sofascore.get_player_heatmap(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532",
    player="Alejandro Garnacho"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `match_url` | `str` | URL completa del partido |
| `player` | `str` | Nombre del jugador tal como aparece en SofaScore |

**Retorna:** `pd.DataFrame` con coordenadas `x`, `y`

---

### `get_player_match_events()`

Obtiene los eventos de un jugador en un partido (pases, dribbles, acciones defensivas, carries).

```python
df = sofascore.get_player_match_events(
    match_url="https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532",
    player="Alejandro Garnacho",
    events=None
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `match_url` | `str` | — | URL completa del partido |
| `player` | `str` | — | Nombre del jugador en SofaScore |
| `events` | `list \| None` | `None` | Filtrar por tipos de evento. Valores posibles: `['passes', 'ball-carries', 'dribbles', 'defensive']`. Si es `None`, trae todos. |

**Retorna:** `pd.DataFrame`

---

## Stats de temporada

### `get_player_season_heatmap()`

Obtiene el heatmap de un jugador a lo largo de una temporada completa.

El ID del jugador está al final de su URL:
`https://www.sofascore.com/player/joaquin-pereyra/832213` → ID: `832213`

```python
df = sofascore.get_player_season_heatmap(
    league="Argentina Liga Profesional",
    season="2024",
    player_id=832213
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `league` | `str` | Liga disponible en `get_available_leagues("Sofascore")` |
| `season` | `str` | Temporada disponible en `get_available_season_for_leagues("Sofascore", league)` |
| `player_id` | `int` | ID del jugador (de la URL) |

**Retorna:** `pd.DataFrame`

---

### `scrape_league_stats()`

Obtiene las estadísticas de todos los jugadores de una liga y temporada. Equivalente a la sección de estadísticas de jugadores en SofaScore ([ejemplo](https://www.sofascore.com/tournament/football/argentina/liga-profesional-de-futbol/155#id:57478)).

```python
df = sofascore.scrape_league_stats(
    league="Argentina Liga Profesional",
    season="2024",
    save_csv=False,
    accumulation="per90",
    selected_positions=["Goalkeepers"]
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `league` | `str` | — | Liga disponible en `get_available_leagues("Sofascore")` |
| `season` | `str` | — | Temporada disponible en `get_available_season_for_leagues()` |
| `save_csv` | `bool` | `False` | Exporta a `.csv` |
| `accumulation` | `str` | `"total"` | Tipo de acumulación: `"total"`, `"per90"`, `"perMatch"` |
| `selected_positions` | `list[str]` | Todas | Posiciones a incluir: `["Goalkeepers"]`, `["Defenders"]`, `["Midfielders"]`, `["Forwards"]` |

**Retorna:** `pd.DataFrame`
