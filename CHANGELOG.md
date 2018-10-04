# Changelog

Versions follow [Semantic Versioning](https://www.semver.org)

## [0.1.0] 2018-10-03
### Added

- Initial fixtures [#1](https://github.com/T4rk1n/pytest-dash/pull/1).
    - `start_dash`, start a dash app instance in a thread.
    - `dash_from_file`, load a py file and return the dash app.
    - `dash_app`, combine `dash_from_file` and `start_dash`.
    - `percy_snapshot`, take percy snapshot (untested)
