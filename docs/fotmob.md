# FotMob

Módulo para scrapear datos de [FotMob](https://www.fotmob.com/). Usa `nodriver` (browser headless) para bypassear el Cloudflare Turnstile que protege las APIs internas del sitio.

```python
import LanusStats as ls

fotmob = ls.FotMob()
```

!!! info "Primera ejecución"
    Al instanciar `FotMob()`, se abre un browser headless en segundo plano. La primera request puede tardar unos segundos mientras el browser resuelve el challenge de Cloudflare.

!!! warning "Cerrar el browser"
    Al terminar de usar el objeto, llamá `fotmob.close()` para liberar recursos. Especialmente importante en scripts de larga duración.

    ```python
    fotmob = ls.FotMob()
    # ... hacer scraping ...
    fotmob.close()
    ```

---

## Tablas de liga

### `get_season_tables()`

Obtiene las tablas de posiciones de una liga para una temporada. Equivalente a la pestaña "Tabla" en FotMob ([ejemplo](https://www.fotmob.com/es/leagues/47/table/premier-league)).

```python
df = fotmob.get_season_tables(
    league="Premier League",
    season="2023/2024",
    table="all"
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `league` | `str` | — | Liga disponible en `get_available_leagues("Fotmob")` |
| `season` | `str` | — | Temporada en formato `"YYYY/YYYY"` |
| `table` | `str` | `"all"` | Tipo de tabla: `"all"`, `"home"`, `"away"`, `"form"`, `"xg"` |

**Retorna:** `pd.DataFrame`

---

## Estadísticas de temporada

### `get_players_stats_season()`

Obtiene estadísticas de jugadores para una temporada y stat específico. Equivalente a la pestaña "Stats" de jugadores en FotMob ([ejemplo](https://www.fotmob.com/es/leagues/47/stats/premier-league)).

```python
df = fotmob.get_players_stats_season(
    league="Premier League",
    season="2023/2024",
    stat="expected_assists_per_90"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `league` | `str` | Liga disponible en `get_available_leagues("Fotmob")` |
| `season` | `str` | Temporada en formato `"YYYY/YYYY"` |
| `stat` | `str` | Stat a obtener (ver FotMob para los valores disponibles) |

**Retorna:** `pd.DataFrame`

---

### `get_teams_stats_season()`

Obtiene estadísticas de equipos para una temporada y stat específico.

```python
df = fotmob.get_teams_stats_season(
    league="Premier League",
    season="2023/2024",
    stat="poss_won_att_3rd_team"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `league` | `str` | Liga disponible en `get_available_leagues("Fotmob")` |
| `season` | `str` | Temporada en formato `"YYYY/YYYY"` |
| `stat` | `str` | Stat a obtener |

**Retorna:** `pd.DataFrame`

---

## Datos de partidos

El ID del partido está al final de la URL de FotMob:
`https://www.fotmob.com/es/matches/afc-bournemouth-vs-manchester-united/2yrx85#4193851` → ID: `4193851`

### `get_match_shotmap()`

Obtiene el mapa de tiros de un partido.

```python
df = fotmob.get_match_shotmap(match_id=4193851)
```

**Retorna:** `pd.DataFrame`

---

### `get_general_match_stats()`

Obtiene las estadísticas generales de los equipos en un partido (tiros, pases, duelos ganados, etc.).

```python
df = fotmob.get_general_match_stats(match_id=4193851)
```

**Retorna:** `pd.DataFrame`

---

### `get_team_colors()`

Obtiene los colores (hex) de los equipos en un partido.

```python
colores = fotmob.get_team_colors(match_id=4193851)
```

**Retorna:** `dict` con los colores de local y visitante.

---

### `request_match_details()`

Obtiene el JSON completo de detalles de un partido.

```python
data = fotmob.request_match_details(match_id=4193851)
```

**Retorna:** `dict` con toda la info del partido.

---

## Datos de jugadores

El ID del jugador está en la URL de su perfil:
`https://www.fotmob.com/es/players/1203665/alejandro-garnacho` → ID: `1203665`

Para `season_index` y `competition_index`: corresponden a la posición en el dropdown de la página del jugador (empezando desde `0`). `season_index=0` es la temporada más reciente, `competition_index=0` es la primera competición de esa temporada.

### `get_player_season_stats()`

Estadísticas del jugador en una temporada y competición.

```python
df = fotmob.get_player_season_stats(
    season_index="0",
    competition_index="0",
    player_id=1203665
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `season_index` | `str` | Posición de la temporada en el dropdown (desde `"0"`) |
| `competition_index` | `str` | Posición de la competición en la temporada (desde `"0"`) |
| `player_id` | `int` | ID del jugador (de la URL) |

**Retorna:** `pd.DataFrame`

---

### `get_player_shotmap()`

Mapa de tiros del jugador en una temporada y competición.

```python
df = fotmob.get_player_shotmap(
    season_index="0",
    competition_index="0",
    player_id=1203665
)
```

**Retorna:** `pd.DataFrame`

---

### `get_player_percentiles()`

Percentiles del jugador en una temporada y competición.

```python
df = fotmob.get_player_percentiles(
    season_index="0",
    competition_index="0",
    player_id=1203665
)
```

**Retorna:** `pd.DataFrame`

---

### `get_player_data()`

Toda la información disponible de un jugador en FotMob.

```python
data = fotmob.get_player_data(player_id=1203665)
```

**Retorna:** `dict` con toda la info del jugador.
