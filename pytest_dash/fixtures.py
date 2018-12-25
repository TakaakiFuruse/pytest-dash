from __future__ import print_function

import pprint
import threading
import time
import sys
import subprocess
import shlex
import uuid

from selenium.common.exceptions import TimeoutException

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

import pytest
import flask
import requests
import percy

from pytest_dash.errors import DashAppLoadingError
from pytest_dash.utils import wait_for_element_by_css_selector


def _stop_server():
    stopper = flask.request.environ['werkzeug.server.shutdown']
    stopper()
    return 'stop'


def _wait_for_client_app_started(driver):
    # Wait until the react-entry-point is loaded.
    try:
        wait_for_element_by_css_selector(driver, '#_dash-app-content')
    except TimeoutException:
        body = wait_for_element_by_css_selector(driver, 'body')
        logs = driver.get_log('browser')
        raise DashAppLoadingError(
            'Dash could not start: \nHTML:\n {}\n\nLOGS: {}'.format(
                body.get_property('innerHTML'),
                pprint.pformat(logs)
            )
        )


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
def dash_threaded(selenium):
    """
    Start a local dash server in a new thread. Stop the server in teardown.

    :param selenium: A selenium fixture.
    :return:
    """

    stop_route = '/_stop-{}'.format(uuid.uuid4().hex)
    ns = dict(
        port=8050,
        url='http://localhost:{}'
    )

    def create_app(app, port=8050):

        app.server.add_url_rule(stop_route, stop_route, _stop_server)
        ns['port'] = port
        ns['url'] = ns['url'].format(port)

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            app.run_server(debug=False, port=port, threaded=True)

        t = threading.Thread(target=run)
        t.daemon = True
        t.start()
        selenium.get(ns['url'])
        _wait_for_client_app_started(selenium)

        return app

    yield create_app

    # Stop the server in teardown
    requests.get('{}{}'.format(ns['url'], stop_route))


@pytest.fixture
def dash_subprocess(selenium):
    namespace = {
        'process': None,
        'queue': Queue()
    }

    def _enqueue(out):
        for line in iter(out.readline, b''):
            namespace['queue'].put(line)
        out.close()

    def _sub(app_module, server_instance='app.server'):
        server_path = '{}:{}'.format(app_module, server_instance)

        status = None
        started = False
        is_windows = sys.platform == 'win32'

        cmd = 'waitress-serve --listen=127.0.0.1:8050 {}'.format(
            server_path
        )
        line = shlex.split(cmd, posix=not is_windows)

        # noinspection PyTypeChecker
        process = namespace['process'] = \
            subprocess.Popen(line,
                             bufsize=1,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        queue_thread = threading.Thread(
            target=_enqueue,
            args=(process.stdout,),
        )
        queue_thread.daemon = True
        queue_thread.start()

        while not started and status is None:
            status = process.poll()
            try:
                out = namespace['queue'].get(timeout=.1)
                out = out.decode()
                if 'Serving on' in out:
                    started = True

            except Empty:
                pass

        if status is not None:
            _, err = process.communicate()
            print(err.decode(), file=sys.stderr)
            raise Exception('Could not start the server.')

        selenium.get('http://localhost:8050/')
        _wait_for_client_app_started(selenium)

    yield _sub

    namespace['process'].kill()
    while not namespace['process'].poll():
        time.sleep(0.01)
