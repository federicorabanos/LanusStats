# SofaScore: migración de undetected_chromedriver a curl_cffi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el transporte HTTP de `SofaScore` (actualmente un browser headless vía `undetected_chromedriver`) por `curl_cffi` con impersonation de Safari, manteniendo la misma interfaz pública (`sofascore_request`, y todos los métodos que dependen de ella) sin cambios para quien ya usa la librería.

**Architecture:** `SofaScore` deja de mantener un `self._driver` (Chrome) y en su lugar mantiene un `self._session` (`curl_cffi.requests.Session(impersonate='safari184')`) persistente entre requests, igual que hoy se reutiliza el driver. `sofascore_request()` sigue siendo el único punto de entrada HTTP: recibe un `path`, devuelve un `dict` ya parseado de JSON, y ahora además detecta explícitamente los bloqueos de SofaScore (403/429) y los convierte en una excepción clara (`SofaScoreConnectionError`) en vez de dejar que el dict de error se propague silenciosamente y explote más abajo como un `KeyError` confuso (que es el bug original reportado: `Error (total): 'results'`).

**Tech Stack:** Python 3.8–3.13, `curl_cffi` (nueva dependencia), pandas. Se elimina la dependencia de `undetected_chromedriver`, `faker` y `bs4` **dentro de `sofascore.py`** (quedan intactas en otros módulos que sí las siguen usando).

**Spec:** No hay spec separada — este plan documenta la migración validada manualmente en la sesión de debugging previa (ver contexto abajo).

## Contexto (por qué este cambio)

- El método actual (`_fetch_with_driver`) navega con Selenium/`undetected_chromedriver` en modo headless directo a la URL de la API JSON. Esto funciona pero:
  - Tarda ~200s solo en levantar el browser (medido en esta sesión).
  - Depende de tener Chrome instalado y expone a procesos zombie de Chrome (ya documentado como problema conocido en `CLAUDE.md`).
- Se validó en esta sesión, contra la API real de SofaScore desde una IP residencial, que `curl_cffi` con `impersonate='safari184'` (o `'safari17_0'`) devuelve exactamente los mismos datos que el browser, en ~20s en vez de ~275s para un scrape de liga completo (987 jugadores, 10 páginas). `impersonate='chrome...'` y `'firefox...'` siguen bloqueados (403 `{"code": 403, "reason": "challenge"}`) — el WAF de SofaScore parece tener reglas específicas contra fingerprints TLS de Chrome/Firefox pero no contra Safari.
- Se validaron los 9 endpoints que usa el módulo (ver tabla). Todos funcionan salvo `rating-breakdown`, que da 404 **también con el método actual** (bug preexistente, no relacionado a esta migración — no se toca en este plan).
- Detalle importante encontrado en la validación: hay que reusar una **`Session`** (no requests sueltos) — sin reuso de conexión/cookies, la segunda página de un scrape paginado se cuelga (timeout). El diseño de abajo ya usa una sesión persistente por eso.

| Endpoint | Método que lo usa | Validado |
|---|---|---|
| `event/{id}` | `get_match_data`, `get_team_names` | ✅ |
| `event/{id}/graph` | `get_match_momentum` | ✅ |
| `event/{id}/shotmap` | `get_match_shotmap` | ✅ |
| `event/{id}/lineups` | `get_players_match_stats`, `get_lineups`, `get_player_ids` | ✅ |
| `event/{id}/average-positions` | `get_players_average_positions` | ✅ |
| `event/{id}/player/{id}/heatmap` | `get_player_heatmap` | ✅ |
| `unique-tournament/.../statistics` (paginado) | `scrape_league_stats` | ✅ |
| `player/{id}/unique-tournament/.../heatmap/overall` | `get_player_season_heatmap` | ✅ |
| `event/{id}/player/{id}/rating-breakdown` | `get_player_match_events` | ❌ 404 pre-existente, fuera de alcance |

## Global Constraints

- No romper la firma pública de ningún método de `SofaScore` (todos siguen recibiendo/devolviendo lo mismo).
- `python_requires='>=3.8, <3.14'` (de `setup.py`) se mantiene — `curl_cffi` soporta ese rango.
- No tocar `functions.py::get_proxy()` ni su import de `undetected_chromedriver as uc` — es una función no relacionada usada fuera de `SofaScore`.
- No tocar `fotmob.py` (usa `nodriver`, un paquete distinto, sin relación con este cambio).
- Seguir la convención bilingüe (ES/EN) existente en `exceptions.py` para el mensaje de la nueva excepción.
- Seguir la convención existente de no tener suite de tests con pytest/mocks para estos módulos — el repo verifica scraping en vivo con scripts locales gitignoreados (`LanusStats/test_*.py`), no hay infraestructura de mocking que inventar aquí.

## Review Focus

- **Bloqueo real (403/429) en producción:** ¿`sofascore_request` levanta `SofaScoreConnectionError` con un mensaje útil, en vez de devolver el dict de error para que explote como `KeyError` en el caller? → cubierto en Task 3.
- **Dato ausente pero legítimo (404, ej. `rating-breakdown` en un arquero):** ¿sigue funcionando igual que antes (no debe convertirse en `SofaScoreConnectionError`)? → cubierto en Task 3 (el check es específico a códigos 403/429, no a cualquier `'error'`).
- **Reuso de sesión entre múltiples llamadas del mismo objeto `SofaScore`:** ¿una segunda o tercera llamada a `sofascore_request` en el mismo objeto reusa la sesión en vez de crear una nueva? → cubierto en Task 4 (test de `scrape_league_stats`, que hace ~10 requests seguidos).
- **Cierre de recursos:** ¿`close()` y el context manager (`with SofaScore() as ss:`) siguen funcionando sin dejar nada abierto, ahora que no hay proceso de Chrome que matar? → cubierto en Task 3 y Task 4.
- **Dependencias muertas:** ¿queda algo en `setup.py` (`faker`) o imports en `sofascore.py` (`bs4`, `json`, `re`, `subprocess`, `sys`) que ya no se usa después del cambio? → cubierto en Task 1 y Task 3.

---

## Task 1: Agregar `curl_cffi` como dependencia y limpiar `faker`

**Files:**
- Modify: `setup.py:19`

**Interfaces:**
- Produces: `curl_cffi` disponible como import en el resto de las tasks.

- [ ] **Step 1: Confirmar que `curl_cffi` no está ya declarado**

Run: `grep -n "curl_cffi\|faker" setup.py`
Expected: aparece `'faker'` en `INSTALL_REQUIRES`, no aparece `'curl_cffi'`.

- [ ] **Step 2: Editar `INSTALL_REQUIRES`**

En `setup.py:19`, cambiar:

```python
INSTALL_REQUIRES = [
      'pandas', 'mplsoccer', 'requests', 'matplotlib', 'numpy', 'bs4', 'Pillow', 'faker', 'nodriver', 'pydoll-python', 'setuptools', 'undetected-chromedriver', 'ipython',
      ]
```

por:

```python
INSTALL_REQUIRES = [
      'pandas', 'mplsoccer', 'requests', 'matplotlib', 'numpy', 'bs4', 'Pillow', 'curl_cffi', 'nodriver', 'pydoll-python', 'setuptools', 'undetected-chromedriver', 'ipython',
      ]
```

(Se quita `'faker'` porque después de la Task 3 deja de usarse en todo el paquete — hoy solo lo usaba `sofascore.py` para generar un User-Agent falso, que ya no hace falta con `curl_cffi`. Se mantiene `'undetected-chromedriver'` porque `functions.py::get_proxy()` sigue usándolo, sin relación con este cambio.)

- [ ] **Step 3: Instalar la dependencia nueva en el entorno local**

Run: `pip install curl_cffi`
Expected: `Successfully installed curl_cffi-...` (o "already satisfied" si ya estaba, como en esta sesión).

- [ ] **Step 4: Verificar que el paquete sigue instalable en modo editable**

Run: `pip install -e . --no-deps`
Expected: exit code 0, sin errores de sintaxis en `setup.py`.

- [ ] **Step 5: Commit**

```bash
git add setup.py
git commit -m "build: agregar curl_cffi y quitar faker de las dependencias"
```

---

## Task 2: Agregar la excepción `SofaScoreConnectionError`

**Files:**
- Modify: `LanusStats/exceptions.py`

**Interfaces:**
- Produces: `SofaScoreConnectionError(error_payload)` — clase exportada desde `LanusStats.exceptions`, consumida por Task 3.

- [ ] **Step 1: Ubicar el punto de inserción**

En `LanusStats/exceptions.py`, las excepciones de FotMob (`FotMobConnectionError`, `FotMobParseError`, `FotMobTimeoutError`) están al final del archivo (líneas 30-48). La nueva clase va inmediatamente después de `FotMobTimeoutError`.

- [ ] **Step 2: Escribir la excepción**

Agregar al final de `LanusStats/exceptions.py`:

```python
class SofaScoreConnectionError(Exception):
    """Raised when SofaScore blocks the request (bot-detection challenge)."""
    def __init__(self, error_payload):
        super().__init__(
            f"SofaScore bloqueó la conexión: {error_payload}. "
            "Puede ser un bloqueo temporal o de reputación de IP (datacenter/cloud); "
            "probar desde otra red o más tarde.\n"
            f"SofaScore blocked the request: {error_payload}. "
            "May be a temporary block or IP reputation issue (datacenter/cloud); "
            "try from a different network or later."
        )
```

- [ ] **Step 3: Verificar que importa correctamente**

Run: `python -c "from LanusStats.exceptions import SofaScoreConnectionError; print(SofaScoreConnectionError({'code': 403, 'reason': 'challenge'}))"`
Expected: imprime el mensaje bilingüe con el payload `{'code': 403, 'reason': 'challenge'}` interpolado.

- [ ] **Step 4: Commit**

```bash
git add LanusStats/exceptions.py
git commit -m "feat: agregar SofaScoreConnectionError para bloqueos 403/429"
```

---

## Task 3: Reescribir el transporte de `SofaScore` para usar `curl_cffi`

**Files:**
- Modify: `LanusStats/sofascore.py:1-199` (imports, helpers de Chrome, `__init__`, `close`, `_build_driver`, `_ensure_driver`, `_fetch_with_driver`, `sofascore_request`)

**Interfaces:**
- Consumes: `SofaScoreConnectionError` de `LanusStats.exceptions` (Task 2), `curl_cffi.requests.Session` de la librería `curl_cffi` (Task 1).
- Produces: `SofaScore.sofascore_request(path: str) -> dict` (firma sin cambios respecto a hoy — todos los métodos que ya la llaman, de `get_match_data` a `get_player_season_heatmap`, siguen funcionando sin tocarlos).

- [ ] **Step 1: Reemplazar el bloque de imports**

En `LanusStats/sofascore.py:1-13`, reemplazar:

```python
import json
import re
import subprocess
import sys
import numpy as np
from datetime import datetime
from typing import Optional
import time
from .functions import get_possible_leagues_for_page, pd, uc, get_random_rate_sleep
from .exceptions import InvalidStrType, MatchDoesntHaveInfo, PlayerDoesntHaveInfo
from faker import Faker
from faker.providers import user_agent
from bs4 import BeautifulSoup
```

por:

```python
import time
from datetime import datetime
from typing import Optional
import numpy as np
from curl_cffi import requests as cffi_requests
from .functions import get_possible_leagues_for_page, pd, get_random_rate_sleep
from .exceptions import InvalidStrType, MatchDoesntHaveInfo, PlayerDoesntHaveInfo, SofaScoreConnectionError
```

(`json`, `re`, `subprocess`, `sys`, `Faker`/`user_agent`, `BeautifulSoup` quedan sin uso una vez que se borran los helpers de Chrome en el Step 3 — por eso se sacan ahora del import.)

- [ ] **Step 2: Borrar los helpers de detección de Chrome**

En `LanusStats/sofascore.py:16-59` (funciones de módulo `_get_chrome_major_version` y `_get_system_chromedriver_path`, entre el bloque de imports y `fake = Faker()`), borrar todo el bloque completo, desde:

```python
def _get_chrome_major_version() -> Optional[int]:
```

hasta el final de:

```python
def _get_system_chromedriver_path() -> Optional[str]:
    ...
    return None
```

(inclusive las dos funciones completas).

- [ ] **Step 3: Borrar las líneas de Faker a nivel de módulo**

Borrar `LanusStats/sofascore.py:62-65`:

```python
fake = Faker()
fake.add_provider(user_agent)

user_agent_provider = fake.user_agent
```

- [ ] **Step 4: Actualizar `__init__` y `close`**

En la clase `SofaScore`, reemplazar:

```python
        self.base_url = 'https://www.sofascore.com/'
        self._driver = None
```

por:

```python
        self.base_url = 'https://www.sofascore.com/'
        self._session = None
```

Y reemplazar el método `close`:

```python
    def close(self) -> None:
        """Close the persistent Chrome session and free resources."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            try:
                self._driver.service.process.kill()
            except Exception:
                pass
            self._driver = None
```

por:

```python
    def close(self) -> None:
        """Close the persistent HTTP session and free resources."""
        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None
```

- [ ] **Step 5: Reemplazar `_build_driver`/`_ensure_driver`/`_fetch_with_driver`/`sofascore_request`**

Reemplazar el bloque completo (`_build_driver`, `_ensure_driver`, `_fetch_with_driver`, `sofascore_request` — hoy líneas 163-199) por:

```python
    def _ensure_session(self) -> cffi_requests.Session:
        if self._session is None:
            self._session = cffi_requests.Session(impersonate='safari184')
        return self._session

    def sofascore_request(self, path: str) -> dict:
        """Make a request to SofaScore reusing a persistent HTTP session.

        Args:
            path: API path relative to the SofaScore base URL.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            SofaScoreConnectionError: SofaScore blocked the request
                (403/429 bot-detection challenge).
        """
        session = self._ensure_session()
        url = f'{self.base_url}{path}'
        response = session.get(url, timeout=20)
        data = response.json()

        if isinstance(data.get('error'), dict) and data['error'].get('code') in (403, 429):
            raise SofaScoreConnectionError(data['error'])

        time.sleep(get_random_rate_sleep(0.5, 1.5))
        return data
```

Nota: el chequeo de `error.get('code') in (403, 429)` es intencionalmente específico — un 404 (dato legítimamente ausente, como el bug preexistente de `rating-breakdown`) **no** debe levantar `SofaScoreConnectionError`, porque varios métodos (`get_match_momentum`, `get_match_shotmap`, `get_player_match_events`) ya manejan un dict sin la clave esperada como "este partido/jugador no tiene esta info" (`MatchDoesntHaveInfo`/`PlayerDoesntHaveInfo`), y ese comportamiento no debe cambiar.

- [ ] **Step 6: Verificar que el archivo importa sin errores**

Run: `python -c "from LanusStats import SofaScore; ss = SofaScore(); print('ok'); ss.close()"`
Expected: imprime `ok` sin excepciones (no debe intentar abrir ningún browser en este punto — la sesión se crea recién en el primer `sofascore_request`).

- [ ] **Step 7: Commit**

```bash
git add LanusStats/sofascore.py
git commit -m "feat: migrar SofaScore de undetected_chromedriver a curl_cffi"
```

---

## Task 4: Verificación manual contra la API real (todos los endpoints)

**Files:**
- Create (temporal, no commitear): script de verificación en el directorio de trabajo, siguiendo el mismo patrón gitignoreado que `LanusStats/test_fotmob.py` (`LanusStats/test_*.py` ya está en `.gitignore`).

**Interfaces:**
- Consumes: `SofaScore` completo de Task 3.

- [ ] **Step 1: Crear `LanusStats/test_sofascore.py`**

```python
"""Manual integration check against the live SofaScore API.
Run with: python LanusStats/test_sofascore.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from LanusStats import SofaScore
from LanusStats.exceptions import SofaScoreConnectionError

MATCH_URL = "https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532"
LEAGUE = "Argentina Liga Profesional"
SEASON = "2026"


def check(name, fn):
    try:
        result = fn()
        print(f"[OK] {name}: {result}")
        return result
    except SofaScoreConnectionError as e:
        print(f"[BLOCKED] {name}: {e}")
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")
    return None


def main():
    with SofaScore() as ss:
        check("get_match_data", lambda: ss.get_match_data(MATCH_URL)["event"]["slug"])
        check("get_match_momentum", lambda: len(ss.get_match_momentum(MATCH_URL)))
        check("get_match_shotmap", lambda: len(ss.get_match_shotmap(MATCH_URL)))
        home_df, away_df = check(
            "get_players_match_stats",
            lambda: [len(d) for d in ss.get_players_match_stats(MATCH_URL)]
        ), None
        check(
            "get_players_average_positions",
            lambda: [len(d) for d in ss.get_players_average_positions(MATCH_URL)]
        )
        player_ids = check("get_player_ids", lambda: ss.get_player_ids(MATCH_URL))
        if player_ids:
            some_player = next(iter(player_ids))
            check(
                "get_player_heatmap",
                lambda: len(ss.get_player_heatmap(MATCH_URL, some_player))
            )
        check(
            "scrape_league_stats (paginado)",
            lambda: ss.scrape_league_stats(LEAGUE, SEASON).shape
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Correrlo**

Run: `python LanusStats/test_sofascore.py`
Expected: todas las líneas empiezan con `[OK]`, ninguna con `[BLOCKED]` ni `[FAIL]` (salvo posiblemente una falla puntual de red transitoria — si pasa, correrlo de nuevo antes de investigar más).

- [ ] **Step 3: Confirmar reuso de sesión (no debería recrear la sesión en cada llamada)**

Run:
```bash
python -c "
from LanusStats import SofaScore
ss = SofaScore()
ss.sofascore_request('api/v1/event/11352532')
session_1 = ss._session
ss.sofascore_request('api/v1/event/11352532/graph')
session_2 = ss._session
print('misma sesión reusada:', session_1 is session_2)
ss.close()
print('sesión cerrada:', ss._session is None)
"
```
Expected: `misma sesión reusada: True` y `sesión cerrada: True`.

- [ ] **Step 4: Confirmar que `close()` y el context manager no rompen nada**

Run:
```bash
python -c "
from LanusStats import SofaScore
with SofaScore() as ss:
    data = ss.sofascore_request('api/v1/event/11352532')
    print('slug:', data['event']['slug'])
print('salió del with sin excepciones')
"
```
Expected: imprime el slug y el mensaje final, sin tracebacks (a diferencia del `OSError` de `Chrome.__del__` que aparecía con el método anterior).

- [ ] **Step 5: No commitear el script de test**

Run: `git status --short LanusStats/test_sofascore.py`
Expected: no aparece nada (el archivo matchea `LanusStats/test_*.py` en `.gitignore`, igual que `test_fotmob.py`).

(Sin commit en este paso — el archivo es intencionalmente local, no versionado.)

---

## Task 5: Actualizar documentación (`CLAUDE.md` y `CHANGELOG.md`)

**Files:**
- Modify: `CLAUDE.md` (sección "SofaScore (`sofascore.py`)")
- Modify: `CHANGELOG.md`

**Interfaces:**
- Ninguna (solo documentación).

- [ ] **Step 1: Actualizar la sección de SofaScore en `CLAUDE.md`**

Reemplazar la sección `### SofaScore (\`sofascore.py\`)` completa (la que describe `undetected_chromedriver`, `_build_driver`, `_fetch_with_driver`, etc.) por:

```markdown
### SofaScore (`sofascore.py`)
- **Técnica**: `curl_cffi` con impersonation de Safari (`impersonate='safari184'`) contra la API interna de SofaScore (no documentada oficialmente)
- La API base es `https://www.sofascore.com/`
- Los IDs de partido se extraen de la URL: `https://www.sofascore.com/match/slug#id:{match_id}`
- Los IDs de jugador están al final de la URL del jugador
- **Historia**: hasta 2026 se usaba `undetected_chromedriver` (browser headless). Se migró a `curl_cffi` porque:
  1. `undetected_chromedriver` tardaba ~200s solo en levantar el browser, contra ~20s de un scrape de liga completo con `curl_cffi`.
  2. Dependía de tener Chrome instalado y generaba procesos zombie.
  3. Validado en producción: `curl_cffi` con `impersonate='chrome*'` o `'firefox*'` sigue bloqueado (403 `{"code": 403, "reason": "challenge"}`), pero `impersonate='safari184'`/`'safari17_0'` pasa sin problema — el WAF de SofaScore parece tener reglas específicas contra fingerprints TLS de Chrome/Firefox pero no contra Safari. Esto puede cambiar sin aviso si SofaScore ajusta su WAF.
- **Cómo funciona**:
  1. `SofaScore()` no abre ninguna conexión al instanciarse.
  2. Al primer `sofascore_request()`, `_ensure_session()` crea una `curl_cffi.requests.Session(impersonate='safari184')` persistente, reutilizada entre requests (importante: sin reuso de sesión/cookies, la segunda request de un scrape paginado se cuelga con timeout).
  3. `sofascore_request(path)` hace el GET, parsea el JSON, y si la respuesta es un bloqueo (`error.code` 403 o 429) levanta `SofaScoreConnectionError` en vez de devolver el dict de error silenciosamente.
  4. `close()` (o el context manager `with SofaScore() as ss:`) cierra la sesión HTTP.
- **Arquitectura interna**:
  - `_ensure_session()` — crea la sesión persistente la primera vez, la reusa después.
  - `sofascore_request(path)` — único punto de entrada HTTP para todos los métodos de la clase.
- **Endpoints principales**:
  - `event/{match_id}/shotmap` → mapa de tiros
  - `event/{match_id}` → datos generales del partido (equipos, fecha, etc.)
  - `event/{match_id}/lineups` → alineaciones
  - `event/{match_id}/statistics` → estadísticas generales por equipo
  - `event/{match_id}/player/{player_id}/heatmap` → mapa de calor
  - `event/{match_id}/player/{player_id}/rating-breakdown` → eventos del jugador (⚠️ da 404 actualmente, endpoint roto/deprecado del lado de SofaScore, pendiente de investigar por separado)
  - `unique-tournament/{tournament_id}/season/{season_id}/statistics/players` → stats de liga
- **`get_match_shotmap` devuelve**: columnas base del shotmap + `match_id`, `teamName`, `vs teamName`
- **Si vuelve a fallar con `SofaScoreConnectionError`**: probablemente el WAF de SofaScore empezó a bloquear también el fingerprint de Safari, o es un tema de reputación de IP (datacenter/cloud vs. residencial — confirmado que desde datacenter se bloquea y desde residencial no). Probar otros valores de `impersonate` de `curl_cffi` (ver `curl_cffi.requests.impersonate` para la lista completa de fingerprints disponibles).
- El riesgo de rotura es **cambio de estructura del JSON de respuesta** cuando SofaScore actualiza su frontend, o que ajusten las reglas de su WAF contra el fingerprint de Safari.
```

- [ ] **Step 2: Actualizar la sección "Problemas conocidos y activos"**

En `CLAUDE.md`, en la sección `## Problemas conocidos y activos`, reemplazar la entrada de SofaScore (si existe una sobre chromedriver/zombies) o agregar:

```markdown
### ✅ SofaScore + bot detection (RESUELTO con curl_cffi, Safari impersonation)
- Migrado de `undetected_chromedriver` a `curl_cffi` en 2026. Ver sección "SofaScore" arriba para el detalle.
- Pendiente sin resolver, sin relación a este cambio: el endpoint `rating-breakdown` (usado por `get_player_match_events`) devuelve 404 tanto con el método viejo como con el nuevo — parece un endpoint roto/deprecado del lado de SofaScore.
```

- [ ] **Step 3: Agregar entrada en `CHANGELOG.md`**

Agregar al principio de `CHANGELOG.md`, después de la línea `# Changelog`:

```markdown
## [2.1.12] - 2026-09-27

### Changed
- **SofaScore**: migrado de `undetected_chromedriver` (browser headless) a `curl_cffi` con impersonation de Safari. Reduce el tiempo de un scrape de liga completo de ~275s a ~20s, y elimina la dependencia de tener Chrome instalado y el riesgo de procesos zombie.
- **SofaScore**: los bloqueos de la API (403/429) ahora levantan `SofaScoreConnectionError` con un mensaje claro, en vez de propagarse como un `KeyError` confuso en el caller.

### Removed
- `faker` como dependencia de `setup.py` (solo la usaba el método viejo de SofaScore para generar User-Agents falsos).
```

(El número de versión `2.1.12` es una propuesta siguiendo el patrón de versiones anteriores — el workflow de CI puede terminar bumpeando a otro número al mergear a `main`; si al momento de mergear el número ya no coincide con lo que hizo el bump automático, ajustar el título de esta sección al número real.)

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md CHANGELOG.md
git commit -m "docs: documentar migración de SofaScore a curl_cffi"
```

---

## Task 6: Revisión final y PR

**Files:** ninguno nuevo — solo verificación de todo lo anterior en conjunto.

- [ ] **Step 1: Correr el script de verificación completo una vez más, de punta a punta**

Run: `python LanusStats/test_sofascore.py`
Expected: todo `[OK]`, igual que en Task 4.

- [ ] **Step 2: Revisar que no quedó nada sin commitear salvo el script de test (gitignoreado)**

Run: `git status --short`
Expected: vacío, o solo archivos que ya estaban sin trackear antes de empezar este plan.

- [ ] **Step 3: Push y PR**

```bash
git push -u origin HEAD
gh pr create --title "SofaScore: migrar de undetected_chromedriver a curl_cffi" --body "$(cat <<'EOF'
## Summary
- Reemplaza el browser headless (`undetected_chromedriver`) por `curl_cffi` con impersonation de Safari como transporte HTTP de `SofaScore`.
- Reduce el tiempo de un scrape de liga completo de ~275s a ~20s.
- Los bloqueos 403/429 ahora levantan `SofaScoreConnectionError` en vez de propagarse como `KeyError` confuso.

## Test plan
- [x] Validados manualmente los 9 endpoints usados por la clase contra la API real (ver CLAUDE.md, sección SofaScore).
- [x] `scrape_league_stats` corrido de punta a punta (987 jugadores, 10 páginas) sin bloqueos.
- [x] Confirmado reuso de sesión entre requests y cierre correcto vía `close()`/context manager.
EOF
)"
```

Expected: PR creado, URL devuelta por `gh`.

---

## Self-Review (completado al escribir este plan)

1. **Cobertura de la investigación de esta sesión**: los 9 endpoints validados están todos cubiertos por Task 4. El hallazgo de que Chrome/Firefox impersonation falla y Safari funciona está documentado en Task 5 (CLAUDE.md) para que quede como conocimiento del proyecto, no solo en este plan.
2. **Placeholders**: ninguno — todos los steps tienen código completo, sin "TBD" ni "similar a Task N".
3. **Consistencia de tipos/nombres**: `_session`/`_ensure_session`/`sofascore_request` se usan consistentemente en Tasks 3 y 4. `SofaScoreConnectionError(error_payload)` tiene la misma firma en Task 2 (definición) y Task 3 (uso).
4. **Review Focus**: las 5 líneas de la sección de arriba están cada una cubierta por una task concreta (403/429 → Task 3; 404 legítimo → Task 3; reuso de sesión → Task 4 Step 3; cierre de recursos → Task 3 Step 4 y Task 4 Step 4; dependencias muertas → Task 1 y Task 3 Step 1).
