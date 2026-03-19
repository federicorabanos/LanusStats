# DataFactory

Módulo para obtener datos de partidos desde DataFactory, incluyendo eventos con coordenadas de cancha (pases, tiros, faltas, etc.).

```python
import LanusStats as ls

datafactory = ls.DataFactory()
```

---

## Pases

### `get_match_passes()`

Obtiene los pases de un partido con sus coordenadas de origen y destino.

```python
df = datafactory.get_match_passes(
    league="Liga Profesional",
    match_id=12345,
    all_passes=False
)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `league` | `str` | — | Liga del partido |
| `match_id` | `int` | — | ID del partido en DataFactory |
| `all_passes` | `bool` | `False` | Si es `True`, incluye todos los pases (completos e incompletos) |

**Retorna:** `pd.DataFrame` con columnas de coordenadas, jugador, equipo y minuto.

---

## Incidencias

### `get_incidence()`

Obtiene cualquier tipo de incidencia de un partido con sus coordenadas.

```python
df = datafactory.get_incidence(
    league="Liga Profesional",
    match_id=12345,
    incidence_type="tiros"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `league` | `str` | Liga del partido |
| `match_id` | `int` | ID del partido |
| `incidence_type` | `str` | Tipo de incidencia (ver lista abajo) |

**Retorna:** `pd.DataFrame`

---

## Tipos de incidencias disponibles

Usá `datafactory.possible_incidences` para ver la lista completa:

```python
print(datafactory.possible_incidences)
```

Algunos valores comunes:

| Valor | Descripción |
|-------|-------------|
| `"tiros"` | Tiros al arco y fuera |
| `"faltas"` | Faltas cometidas |
| `"goles"` | Goles |
| `"tarjetas"` | Tarjetas amarillas y rojas |

---

## Cómo encontrar el `match_id`

El ID del partido se puede obtener desde la URL del partido en la plataforma de DataFactory o desde otras fuentes complementarias. Consultá la documentación de DataFactory para tu liga específica.
