import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div(children=[html.H1("Hello World")])

if __name__ == "__main__":
    app.run_server()