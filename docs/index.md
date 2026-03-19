# LanusStats

<p align="center">
  <img src="https://raw.githubusercontent.com/federicorabanos/LanusStats/main/lanusstats-logo.png" width="400">
</p>

Librería de Python para scrapear datos de fútbol desde múltiples fuentes y visualizarlos con una sola función. Orientada a analistas, periodistas y creadores de contenido del ecosistema hispanohablante de fútbol y datos.

---

## Instalación

```bash
pip install lanusstats
```

Para actualizar a la versión más reciente:

```bash
pip install --upgrade lanusstats
```

---

## Fuentes de datos disponibles

| Módulo | Clase | Qué se puede obtener |
|--------|-------|----------------------|
| [FBRef](fbref.md) | `Fbref` | Stats de equipos y jugadores por temporada, tiros, tabla de posiciones |
| [FotMob](fotmob.md) | `FotMob` | Tablas de liga, stats de temporada, shotmaps, datos de jugadores |
| [SofaScore](sofascore.md) | `SofaScore` | Shotmaps, lineups, posiciones promedio, heatmaps, eventos |
| [Transfermarkt](transfermarkt.md) | `Transfermarkt` | Valuaciones, transferencias, partidos jugados, penales de arqueros |
| [365Scores](threesixfivescores.md) | `ThreeSixFiveScores` | Shotmaps, stats generales, heatmaps por jugador |
| [DataFactory](datafactory.md) | `DataFactory` | Pases, tiros, faltas y otros eventos con coordenadas |

---

## Uso básico

Todos los módulos se importan desde el paquete principal:

```python
import LanusStats as ls

fbref = ls.Fbref()
fotmob = ls.FotMob()
sofascore = ls.SofaScore()
transfermarkt = ls.Transfermarkt()
threesixfivescores = ls.ThreeSixFiveScores()
datafactory = ls.DataFactory()
```

Todos los métodos devuelven **DataFrames de pandas** listos para analizar o exportar.

---

## Funciones generales

Antes de usar cualquier módulo, podés explorar qué páginas, ligas y temporadas están disponibles:

```python
import LanusStats as ls

# Ver páginas disponibles
ls.get_available_pages()

# Ver ligas de una página
ls.get_available_leagues("FBRef")

# Ver temporadas de una liga
ls.get_available_season_for_leagues("FBRef", "Copa de la Liga")
```

Ver documentación completa en [Funciones Generales](general.md).

---

## Comunidad

- [Discord](https://discord.gg/3Nk7Pe6mb8) — comunidad hispanohablante de fútbol y datos
- [Linktree](https://linktr.ee/lanusstats) — todo el contenido de LanusStats

---

## Créditos

- [Owen — ScraperFC](https://github.com/oseymour/ScraperFC)
- [Ben Griffis](https://github.com/griffisben/Soccer-Analyses)
- [McKay Johns](https://www.youtube.com/@McKayJohns)
