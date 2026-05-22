# Changelog

## [2.1.9] - 2026-05-22

### Changed
- **SofaScore**: el driver de Chrome ahora es persistente entre requests (sesión reutilizable). Reduce drásticamente el uso de RAM en loops — Chrome se abre una sola vez en lugar de una vez por request.
  - Se puede usar como context manager: `with SofaScore() as ss:` para cerrar automáticamente.
  - Método `close()` para cerrar manualmente la sesión.
  - `get_match_shotmap` refactorizado para usar la sesión compartida.
- **SofaScore**: type hints en todos los métodos públicos.

## [2.1.8] - 2026-05-22

### Changed
- `setup.py`: agregado `python_requires='>=3.8, <3.14'` para advertir al instalar en versiones incompatibles.
- `setup.py`: agregadas dependencias faltantes: `undetected-chromedriver`, `ipython`.

## [2.1.7] - 2026-05-21

### Fixed
- **FBRef**: corregido `UnicodeDecodeError` al obtener stats de jugadores de La Liga y ligas con caracteres especiales. La causa era el uso de `.decode("unicode_escape")` sobre HTML que el browser ya devuelve en UTF-8. ([PR #41](https://github.com/federicorabanos/LanusStats/pull/41))

## [2.1.6] - 2025

### Changed
- **FotMob `get_match_shotmap`**: enriquecido con `teamName`, `vs teamName`, `keeperName`, `liga`, `fecha`, `dia_partido`.
- **SofaScore `get_match_shotmap`**: enriquecido con `teamName`, `vs teamName`, `teamId`, `vs teamId`, `tournament`, `year`.

## [2.1.5] - 2025

### Fixed
- **SofaScore**: uso de chromedriver del sistema para evitar mismatch de versiones con `undetected_chromedriver`.

## [2.1.3] - 2025

### Fixed
- Detección de Chrome ampliada a más rutas en Linux/GitHub Actions.
- Restaurados imports relativos en `sofascore.py` y `functions.py`.

## [2.1.0] - 2025

### Changed
- **SofaScore**: migrado a `undetected_chromedriver` con detección automática de versión de Chrome.
- **FotMob**: migrado a `nodriver` para bypass automático de Cloudflare Turnstile.

## [2.0.0] - 2025

### Added
- Módulo `DataFactory`: pases, tiros, faltas, corners y cualquier incidencia de partido desde `datafactory.la`.
- Nuevas visualizaciones: `sofascore_plot_match_events`.
- Soporte para `get_player_match_events` en SofaScore.

## [1.9.0] - 2024

### Added
- Módulo `Transfermarkt`: valor de mercado, transferencias, planteles, valuaciones de liga, historial de DTs.
- Visualización `transfermarkt_player_market_value`.

## [1.8.0] - 2024

### Added
- Soporte para Big 5 European Leagues en FBRef.
- Nuevas ligas en SofaScore y FotMob.

## [1.0.0] - 2024

### Added
- Release inicial con módulos `Fbref`, `FotMob`, `SofaScore`, `ThreeSixFiveScores`.
- Visualizaciones: `fotmob_match_momentum_plot`, `fotmob_hexbin_shotmap`, `threesixfivescores_match_shotmap`.
