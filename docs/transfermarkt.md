# Transfermarkt

Módulo para scrapear datos de [Transfermarkt](https://www.transfermarkt.com.ar/) usando `requests` + `BeautifulSoup`.

```python
import LanusStats as ls

transfermarkt = ls.Transfermarkt()
```

---

## Datos de ligas y equipos

### `get_league_teams_valuations()`

Obtiene las valuaciones de todos los planteles de una liga en una temporada.

```python
df = transfermarkt.get_league_teams_valuations(
    league="Primera Division Argentina",
    season="2024"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `league` | `str` | Liga disponible en `get_available_leagues("Transfermarkt")` |
| `season` | `str` | Temporada (ej: `"2024"`, `"2023/2024"`) |

**Retorna:** `pd.DataFrame`

---

### `scrape_players_for_teams()`

Obtiene el plantel de un equipo en una temporada.

El nombre e ID del equipo se sacan de la URL de Transfermarkt:
`https://www.transfermarkt.com.ar/club-atletico-lanus/startseite/verein/333`
→ `team_name="Club Atletico Lanus"`, `team_id="333"`

```python
df = transfermarkt.scrape_players_for_teams(
    team_name="Club Atletico Lanus",
    team_id="333",
    season="2024"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `team_name` | `str` | Nombre del equipo tal como aparece en la URL (sin guiones medios) |
| `team_id` | `str` | ID del equipo (número al final de la URL) |
| `season` | `str` | Temporada (ej: `"2024"`, `"2023/2024"`) |

**Retorna:** `pd.DataFrame`

---

## Datos de jugadores

El ID del jugador está en la URL de su perfil:
`https://www.transfermarkt.com.ar/marcelino-moreno/profil/spieler/456617` → ID: `"456617"`

### `get_player_transfer_history()`

Obtiene el historial de transferencias de un jugador.

```python
df = transfermarkt.get_player_transfer_history(player_id="456617")
```

**Retorna:** `pd.DataFrame`

---

### `get_player_market_value()`

Obtiene la evolución del valor de mercado de un jugador a lo largo de su carrera.

```python
df = transfermarkt.get_player_market_value(player_id="456617")
```

**Retorna:** `pd.DataFrame` con fechas y valores de mercado.

---

### `get_player_positions_played()`

Obtiene las posiciones en las que jugó un jugador a lo largo de su carrera.

```python
df = transfermarkt.get_player_positions_played(
    player_name="Marcelino Moreno",
    player_id="456617"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `player_name` | `str` | Nombre del jugador |
| `player_id` | `str` | ID del jugador (de la URL) |

**Retorna:** `pd.DataFrame`

---

### `get_player_played_data()`

Obtiene estadísticas de partidos jugados por temporada y competición.

```python
df = transfermarkt.get_player_played_data(
    player_name="Emiliano Martinez",
    player_id="111873"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `player_name` | `str` | Nombre del jugador |
| `player_id` | `str` | ID del jugador (de la URL) |

**Retorna:** `pd.DataFrame`

---

### `get_keepers_penalty_data()`

Obtiene estadísticas de penales para un arquero (atajados y recibidos por temporada).

```python
df = transfermarkt.get_keepers_penalty_data(
    player_name="Emiliano Martinez",
    player_id="111873"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `player_name` | `str` | Nombre del arquero |
| `player_id` | `str` | ID del jugador (de la URL) |

**Retorna:** `pd.DataFrame`

---

### `get_head_coach_historical_data()`

Obtiene el historial de equipos dirigidos por un técnico.

```python
df = transfermarkt.get_head_coach_historical_data(
    name="Marcelo Gallardo",
    headcoach_id="12345"
)
```

**Retorna:** `pd.DataFrame`
