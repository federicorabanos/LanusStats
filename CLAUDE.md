# LanusStats — Contexto para Claude Code

## ¿Qué es este proyecto?

LanusStats es una librería Python de scraping orientada al fútbol y los datos. Su objetivo es abstraer la complejidad de extraer datos de múltiples plataformas (FBRef, FotMob, SofaScore, Transfermarkt, 365Scores) en funciones simples que devuelven DataFrames de pandas listos para analizar o visualizar.

El público objetivo son analistas, periodistas y creadores de contenido del ecosistema hispanohablante de fútbol y datos.

---

## Estructura del proyecto

```
LanusStats/
├── LanusStats/
│   ├── __init__.py          # Exporta las clases principales y funciones generales
│   ├── fbref.py             # Módulo FBRef
│   ├── fotmob.py            # Módulo FotMob (nodriver — bypass Cloudflare Turnstile)
│   ├── sofascore.py         # Módulo SofaScore (API interna no documentada)
│   ├── transfermarkt.py     # Módulo Transfermarkt (BeautifulSoup)
│   ├── threesixfivescores.py# Módulo 365Scores
│   ├── visualizations.py    # Visualizaciones que combinan scraping + matplotlib/mplsoccer
│   └── utils.py             # Helpers compartidos (ligas disponibles, temporadas, etc.)
├── setup.py
├── MANIFEST.in
└── README.md
```

---

## Convenciones de código

- Cada fuente de datos es una **clase** (`Fbref`, `FotMob`, `SofaScore`, `Transfermarkt`, `ThreeSixFiveScores`)
- Los métodos siempre devuelven **DataFrames de pandas** o listas de DataFrames
- Los parámetros de liga/temporada se validan contra diccionarios internos de ligas disponibles
- `save_csv=False` / `save_excel=False` son parámetros opcionales comunes para exportar
- Los errores custom se definen por módulo (ej: `MatchDoesntHaveInfo`)
- Las funciones generales `get_available_pages()`, `get_available_leagues(page)`, `get_available_season_for_leagues(page, league)` viven fuera de las clases

---

## Módulos y cómo funcionan internamente

### FBRef (`fbref.py`)
- **Técnica**: `requests` + `BeautifulSoup` + `pandas.read_html()`
- FBRef sirve HTML estático con tablas HTML reales → fácil de parsear con `pd.read_html()`
- Las URLs siguen el patrón: `https://fbref.com/en/comps/{id}/{stat}/{league}-Stats`
- El mayor problema recurrente es que FBRef **cambia los IDs de competición** o la estructura de columnas cuando actualiza temporadas
- Las columnas suelen tener headers multi-nivel (MultiIndex) que hay que aplanar
- `change_columns_names` renombra columnas tipo `Unnamed: X`
- `add_page_name` agrega prefijo con el nombre del stat para evitar colisiones al hacer merge entre tablas

### FotMob (`fotmob.py`)
- **Técnica actual**: `nodriver` — browser headless que bypasea Cloudflare Turnstile automáticamente sin clicks humanos
- **Historia**: FotMob implementó Cloudflare Turnstile en 2024. Se probaron `requests` (falla: 403), Selenium (falla: challenge JS), `curl_cffi` (falla: TLS fingerprint insuficiente). La solución que funcionó es `nodriver`.
- **Cómo funciona**:
  1. Al instanciar `FotMob()`, se crea un **background thread dedicado** con su propio `asyncio` loop (`ProactorEventLoop` en Windows, `SelectorEventLoop` en otros OS). Esto permite usar la clase desde scripts y desde Jupyter notebooks sin conflictos de event loop.
  2. Al primer uso, `_ensure_browser()` llama `_start_browser()`: abre nodriver, visita `https://www.fotmob.com` y espera 5s para que Turnstile resuelva solo.
  3. `_submit(coro)` despacha corrutinas al background loop via `asyncio.run_coroutine_threadsafe()` y bloquea hasta obtener el resultado.
  4. `_async_fetch(url)` navega al endpoint, extrae el JSON del `<pre>` con regex, y reintenta con espera incremental si detecta un challenge. Si el browser se cae, `_restart_browser()` lo resetea y reinicia.
  5. `fotmob_request(path)` envuelve el resultado en `_FotMobResponse` (que tiene `.json()`) para mantener compatibilidad con todos los callers internos sin cambios.
- **APIs internas que usa FotMob**:
  - `https://www.fotmob.com/api/leagues?id={league_id}&ccode3=ARG` → tablas de liga
  - `https://www.fotmob.com/api/leagueseasondeepstats?id={league_id}&...` → stats de temporada
  - `https://www.fotmob.com/api/matchDetails?matchId={match_id}` → detalle de partido
  - `https://www.fotmob.com/api/playerData?id={player_id}` → datos de jugador
  - `https://www.fotmob.com/api/playerStats?playerId={player_id}&seasonId={season_index}-{competition_index}`
- **Errores custom**: `FotMobConnectionError`, `FotMobParseError`, `FotMobTimeoutError` (definidos en `exceptions.py`)
- **Si vuelve a fallar**: Verificar que el `<pre>` siga siendo el elemento que FotMob usa para JSON. Inspeccionar `content[:500]` en `_async_fetch` para ver qué devuelve el browser.
- **Archivo de tests**: `LanusStats/test_fotmob.py` — ejecutar con `python LanusStats/test_fotmob.py` desde la raíz del repo

### SofaScore (`sofascore.py`)
- **Técnica**: `requests` contra la API interna de SofaScore (no documentada oficialmente)
- La API base es `https://api.sofascore.com/api/v1/`
- Los IDs de partido se extraen de la URL: `https://www.sofascore.com/match/slug#id:{match_id}`
- Los IDs de jugador están al final de la URL del jugador
- **Endpoints principales**:
  - `event/{match_id}/shotmap` → mapa de tiros
  - `event/{match_id}/lineups` → alineaciones
  - `event/{match_id}/statistics` → estadísticas generales por equipo
  - `event/{match_id}/player/{player_id}/heatmap` → mapa de calor
  - `event/{match_id}/player/{player_id}/highlights` → eventos del jugador
  - `unique-tournament/{tournament_id}/season/{season_id}/statistics/players` → stats de liga
- El riesgo de rotura es **cambio de estructura del JSON de respuesta** cuando SofaScore actualiza su frontend
- Los headers necesarios incluyen `user-agent` y en algunos endpoints `x-requested-with`

### Transfermarkt (`transfermarkt.py`)
- **Técnica**: `requests` + `BeautifulSoup`
- Transfermarkt tiene **protección anti-bot por User-Agent** → se necesitan headers con UA realista
- Las URLs siguen el patrón: `https://www.transfermarkt.com.ar/{team-name}/startseite/verein/{team_id}`
- Para jugadores: `https://www.transfermarkt.com.ar/{player-name}/profil/spieler/{player_id}`
- **Datos que se pueden extraer**: valuaciones históricas, transferencias, partidos jugados, posiciones
- El problema más común es que Transfermarkt cambia el HTML de las tablas o agrega captchas

### 365Scores (`threesixfivescores.py`)
- **Técnica**: API interna / requests
- Menos documentado internamente que el resto
- Usado principalmente para `shotmap` de partidos

---

## Visualizaciones (`visualizations.py`)

- Usa `matplotlib`, `mplsoccer` y las funciones de scraping de los módulos anteriores
- Cada función de visualización es autónoma: scraping + plotting en una sola llamada
- Funciones existentes:
  - `fotmob_match_momentum_plot(match_id)` → gráfico de momentum del partido
  - `fotmob_hexbin_shotmap(league, season, player_id)` → hexbin de tiros del jugador
  - `threesixfivescores_match_shotmap(url)` → shotmap del partido
  - `transfermarkt_player_market_value(player_id)` → evolución de valor de mercado
  - `sofascore_plot_match_events(url, player_name, events, dashboard)` → eventos en cancha

---

## Problemas conocidos y activos

### ✅ FotMob + Cloudflare Turnstile (RESUELTO con nodriver)
- Migrado a `nodriver` en 2025. El browser headless resuelve el Turnstile automáticamente.
- Si vuelve a fallar: ver sección "Si vuelve a fallar" en la descripción del módulo arriba.

### 🟡 Columnas de FBRef con MultiIndex
- FBRef usa tablas con headers de dos filas. `pd.read_html()` las parsea como MultiIndex
- Al hacer merge entre tablas distintas pueden haber colisiones de nombres
- `add_page_name=True` es el workaround actual

### 🟡 IDs de temporada en SofaScore
- Los `tournament_id` y `season_id` de SofaScore no tienen un patrón público predecible
- Están hardcodeados en los diccionarios internos de ligas disponibles
- Cuando empieza una nueva temporada, hay que actualizar estos IDs manualmente

---

## Cómo agregar soporte para una nueva fuente

1. Crear `nueva_fuente.py` en `LanusStats/`
2. Definir la clase con `__init__` que setee headers, base URL y cualquier estado necesario
3. Agregar métodos que devuelvan DataFrames
4. Registrar la nueva fuente en `utils.py` en los diccionarios de `get_available_pages()` y `get_available_leagues()`
5. Exportar la clase en `__init__.py`
6. Documentar en README.md

---

## Cómo explorar una API interna nueva

Cuando una página cambia estructura o querés agregar una nueva fuente, el flujo es:

1. **Abrir DevTools en Chrome** → pestaña Network → filtrar por `Fetch/XHR`
2. Navegar por la página y observar qué requests hace el browser
3. Identificar los endpoints JSON (buscar respuestas con `Content-Type: application/json`)
4. Click derecho en la request → "Copy as cURL" para ver headers exactos
5. Convertir el cURL a Python con `requests` manteniendo los headers necesarios
6. Si hay Cloudflare Turnstile: usar `nodriver` (ver FotMob como referencia de implementación)

---

## Stack técnico

- Python 3.8+
- `requests` — HTTP requests principales
- `beautifulsoup4` — parsing HTML (FBRef, Transfermarkt)
- `pandas` — estructuración de datos, `read_html()`
- `nodriver` — bypass de Cloudflare Turnstile en FotMob (browser headless sin detección)
- `matplotlib` + `mplsoccer` — visualizaciones

---

## Tips para debugging de scraping

- Si una función devuelve DataFrame vacío: primero imprimir `response.status_code` y `response.text[:500]`
- Si hay 403: problema de headers/bot detection. Agregar/actualizar User-Agent y headers del browser
- Si hay 200 pero falla el parsing: la estructura del HTML/JSON cambió. Inspeccionar la respuesta cruda
- Si hay timeout: el sitio puede estar bloqueando la IP temporalmente, probar con delay entre requests
- Para FotMob específicamente: inspeccionar `content[:500]` en `_async_fetch` para ver qué devuelve el browser. Verificar que `nodriver` esté actualizado (`pip install -U nodriver`).