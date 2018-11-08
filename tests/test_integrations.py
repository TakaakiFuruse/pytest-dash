import time

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

import dash
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_html_components as html

from pytest_dash.tools import dash_threaded, dash_from_file, NoAppFoundError, dash_subprocess


def test_dash_threaded(dash_threaded, selenium):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.Button('click me', id='clicker'),
        html.Div(id='output')
    ])

    call_count = Queue()

    @app.callback(Output('output', 'children'),
                  [Input('clicker', 'n_clicks')])
    def on_click(n_clicks):
        call_count.put(1)
        if n_clicks is None:
            raise PreventUpdate

        return n_clicks

    dash_threaded(app)

    clicker = selenium.find_element_by_id('clicker')

    for i in range(6):
        clicker.click()
        time.sleep(1)

    assert call_count.qsize() == 7


def test_no_app_found(dash_from_file):
    error = None

    try:
        app = dash_from_file('test_apps/bad.py')
    except NoAppFoundError as e:
        error = e

    assert isinstance(error, NoAppFoundError)


def test_subprocess(dash_subprocess, selenium):
    dash_subprocess('test_apps/simple_app')

    value_input = selenium.find_element_by_id('value')
    value_input.clear()
    value_input.send_keys('Hello dash subprocess')
