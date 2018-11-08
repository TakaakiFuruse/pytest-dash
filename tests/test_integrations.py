import time

from pytest_dash.tools import dash_threaded, dash_from_file, NoAppFoundError, dash_subprocess


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


def test_subprocess(dash_subprocess, selenium):
    dash_subprocess('test_apps.simple_app')

    value_input = selenium.find_element_by_id('value')
    value_input.clear()
    value_input.send_keys('Hello dash subprocess')
