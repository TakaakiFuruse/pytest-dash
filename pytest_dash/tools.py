import runpy
import threading
import time
import sys

import pytest
import flask
import requests
import percy

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import By


class NoAppFoundError(Exception):
    """No `app` was found in the file."""


@pytest.fixture(scope='package')
def percy_snapshot(selenium):

    loader = percy.ResourceLoader(webdriver=selenium)
    percy_runner = percy.Runner(loader=loader)
    percy_runner.initialize_build()

    def take_snapshot(snapshot_name):
        print('Percy Snapshot {}'.format(sys.version.split(' ')[0]))
        percy_runner.snapshot(name=snapshot_name)

    yield take_snapshot

    percy_runner.finalize_build()


@pytest.fixture
def start_dash(selenium):
    """
    Start a local dash server in a new thread. Stop the server in teardown.

    :param selenium: A selenium fixture.
    :return:
    """

    def create_app(app):

        @app.server.route('/stop')
        def _stop_server():
            stopper = flask.request.environ['werkzeug.server.shutdown']
            stopper()
            return 'stop'

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            app.run_server(debug=False, port=8050, threaded=True)

        t = threading.Thread(target=run)
        t.daemon = True
        t.start()
        time.sleep(3)
        selenium.get('http://localhost:8050')

        # Wait until the react-entry-point is loaded.
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'react-entry-point')))

        return app

    yield create_app

    # Stop the server in teardown
    requests.get('http://localhost:8050/stop')


@pytest.fixture
def dash_from_file():
    """
    Import a dash app from a filepath, the imported file must have a Dash
    instance named `app`
    """

    def import_app(app_file):
        try:
            app_module = runpy.run_path(app_file)
            app = app_module['app']
        except KeyError:
            raise NoAppFoundError(
                'No dash `app` instance was found in {}'.format(app_file)
            )
        except IOError:
            raise
        return app

    yield import_app


@pytest.fixture
def dash_app(dash_from_file, start_dash):
    """
    Import a dash app from a file, then start the process.

    :param dash_from_file:
    :param start_dash:
    :return:
    """

    def _starter(app_file):
        app = dash_from_file(app_file)
        start_dash(app)
        return app

    yield _starter
