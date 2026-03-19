# Visualizaciones

Funciones de visualización que combinan scraping y plotting en una sola llamada. Usan `matplotlib` y `mplsoccer` internamente.

```python
import LanusStats as ls
```

Todas las funciones se acceden directamente desde el módulo `ls.visualizations` o desde `ls` directamente.

---

## FotMob

### `fotmob_match_momentum_plot()`

Grafica el momentum del partido minuto a minuto como gráfico de barras.

```python
ls.visualizations.fotmob_match_momentum_plot(
    match_id=4193851,
    save_fig=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `match_id` | `int` | — | ID del partido. Está al final de la URL: `...#4193851` |
| `save_fig` | `bool` | `False` | Guarda la figura como imagen |

---

### `fotmob_hexbin_shotmap()`

Crea un mapa de tiros hexbin de un jugador en una temporada y competición.

```python
ls.visualizations.fotmob_hexbin_shotmap(
    season_index="0",
    competition_index="0",
    player_id=711231,
    credit_extra=" ",
    save_fig=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `season_index` | `str` | — | Posición de la temporada en el dropdown de FotMob (desde `"0"`) |
| `competition_index` | `str` | — | Posición de la competición en esa temporada (desde `"0"`) |
| `player_id` | `int` | — | ID del jugador. Ej: `https://www.fotmob.com/es/players/711231/gorka-guruzeta` |
| `credit_extra` | `str` | `" "` | Texto adicional para los créditos del gráfico |
| `save_fig` | `bool` | `False` | Guarda la figura como imagen |

---

## 365Scores

### `threesixfivescores_match_shotmap()`

Grafica el mapa de tiros de un partido desde 365Scores.

```python
ls.visualizations.threesixfivescores_match_shotmap(
    match_url="https://www.365scores.com/es-mx/football/match/copa-sudamericana-389/lanus-metropolitanos-fc-869-13830-389#id=4072240",
    save_fig=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `match_url` | `str` | — | URL completa del partido en 365Scores |
| `save_fig` | `bool` | `False` | Guarda la figura como imagen |

!!! note
    Solo grafica si el partido tiene datos de shotmap disponibles.

---

## Transfermarkt

### `transfermarkt_player_market_value()`

Grafica la evolución del valor de mercado de un jugador a lo largo de su carrera.

```python
ls.visualizations.transfermarkt_player_market_value(
    transfermarkt_player_id="111873",
    save_fig=False,
    plot_age=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `transfermarkt_player_id` | `str` | — | ID del jugador en Transfermarkt (de la URL) |
| `save_fig` | `bool` | `False` | Guarda la figura como imagen |
| `plot_age` | `bool` | `False` | Usa la edad en el eje X en lugar de la fecha |

---

## SofaScore

### `sofascore_plot_match_events()`

Grafica los eventos de un jugador en un partido sobre una cancha. Permite ver pases, dribbles, acciones defensivas y carries.

```python
ls.visualizations.sofascore_plot_match_events(
    match_url="https://www.sofascore.com/es/football/match/banfield-racing-club/pobsuob#id:15270114",
    player="Santiago Sosa",
    events=None,
    dashboard=True,
    save_fig=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `match_url` | `str` | — | URL completa del partido en SofaScore |
| `player` | `str` | — | Nombre del jugador tal como aparece en SofaScore |
| `events` | `list \| None` | `None` | Tipos de eventos a mostrar: `['passes', 'ball-carries', 'dribbles', 'defensive']`. Si es `None`, muestra todos. |
| `dashboard` | `bool` | `False` | Si es `True`, combina todos los gráficos en una sola figura |
| `save_fig` | `bool` | `False` | Guarda la figura como imagen |
