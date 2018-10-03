import time

from pytest_dash.tools import start_dash


def test_run_app(dash_app, selenium):
    dash_app('test_apps/simple_app.py')

    selenium.get('http://localhost:8050')
    time.sleep(1)
