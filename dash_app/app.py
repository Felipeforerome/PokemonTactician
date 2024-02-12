from dash import Dash
import dash_bootstrap_components as dbc
from layouts import layout
import callbacks  # This imports the callbacks to register them with the app

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
