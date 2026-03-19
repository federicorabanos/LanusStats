# Funciones Generales

Funciones de utilidad que no pertenecen a ningún módulo en particular. Sirven para explorar qué páginas, ligas y temporadas están disponibles antes de hacer cualquier scraping.

---

## `get_available_pages()`

Devuelve la lista de páginas/fuentes que tienen módulo de scraping disponible.

```python
import LanusStats as ls

ls.get_available_pages()
```

**Retorna:** `list[str]` con los nombres de las páginas disponibles.

---

## `get_available_leagues(page)`

Devuelve las ligas disponibles para una página en particular.

```python
ls.get_available_leagues("FBRef")
ls.get_available_leagues("Fotmob")
ls.get_available_leagues("Sofascore")
ls.get_available_leagues("Transfermarkt")
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | `str` | Nombre de la página (usar los valores de `get_available_pages()`) |

**Retorna:** `list[str]` con los nombres de ligas disponibles.

---

## `get_available_season_for_leagues(page, league)`

Devuelve las temporadas disponibles para una liga específica.

```python
ls.get_available_season_for_leagues("FBRef", "Copa de la Liga")
ls.get_available_season_for_leagues("Fotmob", "Premier League")
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | `str` | Nombre de la página |
| `league` | `str` | Nombre de la liga (usar los valores de `get_available_leagues()`) |

**Retorna:** `list[str]` con las temporadas disponibles.

---

## Flujo recomendado

```python
import LanusStats as ls

# 1. Ver qué páginas hay
ls.get_available_pages()
# ['FBRef', 'Fotmob', 'Sofascore', 'Transfermarkt', ...]

# 2. Ver ligas de FBRef
ls.get_available_leagues("FBRef")
# ['Copa de la Liga', 'Liga Profesional Argentina', 'Premier League', ...]

# 3. Ver temporadas de esa liga
ls.get_available_season_for_leagues("FBRef", "Copa de la Liga")
# ['2024', '2023', '2022', ...]

# 4. Usar el módulo con esos valores
fbref = ls.Fbref()
df = fbref.get_teams_season_stats("gca", "Copa de la Liga", season="2024")
```
