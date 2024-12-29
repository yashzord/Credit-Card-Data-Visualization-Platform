from flask import Flask, render_template, redirect,  request, session
import random, string
from dash_instance import create_dashapp, dash_layout
from pos_instance import create_pos_dashapp, pos_dash_layout
import dash
from dash import html, dcc
import os, signal

server = Flask(__name__, template_folder='templates')

server.secret_key = "dev"

app = dash.Dash(__name__, server = server, url_base_pathname = '/dash/')

pos_app = dash.Dash(__name__, server = server, url_base_pathname = '/pos_dash/')

app.layout = dash_layout

pos_app.layout = pos_dash_layout

clickarr = []


@server.route('/')
def home():
    return render_template('index.html')

@server.route('/dashboard')
def render_dashboard():
    print(session["clickData"])
    create_dashapp(app, session["clickData"])
    return redirect('/dash/')

@server.route('/pos') 
def render_pos_dashboard():
    print(session["clickData"])
    create_pos_dashapp(pos_app, session["clickData"])
    return redirect('/pos_dash/')


@server.route('/update_data', methods=['POST'])
def update_data():
    data = request.get_json()
    session["clickData"] = data
    return data


if __name__ == '__main__':
   server.run(debug = True)