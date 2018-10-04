# pytest-dash

[Pytest][2] fixtures for [dash][1]

## Install

`$ pip install pytest-dash`

### Fixtures

#### `start_dash`

Start a dash instance in a thread, stop the server in teardown.

```python
import dash

import dash_html_components as html

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


def test_app(start_dash, selenium):
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.Div('My test layout', id='out'),
        html.Button('click me', id='click-me')
    ])
    
    @app.callback(Output('out', 'children'), [Input('click-me', 'n_clicks')])
    def on_click(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return 'Clicked: {}'.format(n_clicks)
    
    start_dash(app)
    
    btn = selenium.find_element_by_id('click-me')
    btn.click()
    
    out = selenium.find_element_by_id('out')
    assert out.text == 'Clicked: 1'
```

#### `dash_from_file`

Load a file with `runpy`, return the app instance.

```python
def test_app(dash_from_file):
    app = dash_from_file('usage.py')
    ...
```

#### `dash_app`

Combine `start_dash` and `dash_from_file`.

```python
def test_app(dash_app, selenium):
    app = dash_app('usage.py')
    # App has already been started, safe to use selenium from there.
    out = selenium.find_element_by('out')
    ...
```

## More resources

- [Dash user guide](https://dash.plot.ly/)
- [Pytest][2]


[1]: https://github.com/plotly/dash
[2]: https://github.com/pytest-dev/pytest
