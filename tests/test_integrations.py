import time

from pytest_dash.tools import start_dash, dash_from_file, NoAppFoundError


def test_run_app(dash_app, selenium):
    dash_app('test_apps/simple_app.py')

    selenium.get('http://localhost:8050')
    time.sleep(1)


def test_no_app_found(dash_from_file):
    error = None

    try:
        app = dash_from_file('test_apps/bad.py')
    except NoAppFoundError as e:
        error = e

    assert isinstance(error, NoAppFoundError)
