# 365Scores

Módulo para scrapear datos de [365Scores](https://www.365scores.com/es-mx/football) usando su API interna.

```python
import LanusStats as ls

threesixfivescores = ls.ThreeSixFiveScores()
```

---

## Datos de partidos

La mayoría de los métodos reciben la URL completa del partido. Ejemplo:
`https://www.365scores.com/es-mx/football/match/copa-sudamericana-389/lanus-metropolitanos-fc-869-13830-389#id=4072240`

### `get_match_shotmap()`

Obtiene el mapa de tiros de un partido (si el partido tiene esta información disponible).

```python
df = threesixfivescores.get_match_shotmap(match_url="https://www.365scores.com/...")
```

**Retorna:** `pd.DataFrame`

---

### `get_match_general_stats()`

Obtiene las estadísticas generales de ambos equipos en un partido.

```python
df = threesixfivescores.get_match_general_stats(match_url="https://www.365scores.com/...")
```

**Retorna:** `pd.DataFrame`

---

### `get_match_time_stats()`

Obtiene estadísticas temporales del partido (distribución por minuto).

```python
df = threesixfivescores.get_match_time_stats(match_url="https://www.365scores.com/...")
```

**Retorna:** `pd.DataFrame`

---

### `get_players_info()`

Obtiene información de los jugadores que participaron en el partido.

```python
df = threesixfivescores.get_players_info(match_url="https://www.365scores.com/...")
```

**Retorna:** `pd.DataFrame`

---

### `get_team_data()`

Obtiene nombre, ID y color de ambos equipos del partido.

```python
data = threesixfivescores.get_team_data(match_url="https://www.365scores.com/...")
```

**Retorna:** `dict` con datos de local y visitante.

---

### `get_general_match_stats()`

Obtiene las estadísticas generales del partido (versión alternativa a `get_match_general_stats`).

```python
df = threesixfivescores.get_general_match_stats(match_url="https://www.365scores.com/...")
```

**Retorna:** `pd.DataFrame`

---

### `get_match_data()`

Obtiene todo el JSON de datos del partido.

```python
data = threesixfivescores.get_match_data(match_url="https://www.365scores.com/...")
```

**Retorna:** `dict`

---

## Datos de jugadores

### `get_player_heatmap_match()`

Obtiene la imagen del heatmap de un jugador en un partido.

```python
img = threesixfivescores.get_player_heatmap_match(
    player="Nombre del jugador",
    match_url="https://www.365scores.com/..."
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `player` | `str` | Nombre del jugador |
| `match_url` | `str` | URL completa del partido |

---

## Stats de liga

### `get_league_top_players_stats()`

Obtiene los mejores jugadores en distintas estadísticas de una liga.

```python
df = threesixfivescores.get_league_top_players_stats(league="...")
```

**Retorna:** `pd.DataFrame`
