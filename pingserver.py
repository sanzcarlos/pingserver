#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from flask import Flask,g,render_template,request,jsonify,flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import ipaddress
import configparser
import ast
from os import path
from lib import Connection
from lib import CustomLogger
from wtforms import Form, TextField, validators, SubmitField

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d54f27d441f27567d441f2b6176a'

apiAuth = HTTPBasicAuth()
webAuth = HTTPBasicAuth()

config = configparser.ConfigParser()
config.read('conf/pingsrv.conf')
apiUser = config.get('Api', 'user')
apiPass = config.get('Api', 'password')
credentials = ast.literal_eval(config.get('Web', 'credentials'))

infoLogger = CustomLogger.getCustomLogger('pingsrvapp', 'pingsrvapp','DEBUG')
errorLogger = CustomLogger.getCustomLogger('error', 'error')

@apiAuth.verify_password
def verify_password(username, password):
    g.usuario = None
    if username == apiUser:
        g.usuario = username
        return check_password_hash(generate_password_hash(apiPass), password)
    return False

@webAuth.verify_password
def verify_password(username, password):
    g.usuario = None
    if username in credentials.keys():
        g.usuario = username
        return check_password_hash(generate_password_hash(credentials[username]), password)
    return False

class IPForm(Form):
    ip = TextField('Dirección IP:', validators=[validators.required()])

@app.route('/', methods = ['GET', 'POST'])
@webAuth.login_required
def index():
    resultado = {}
    form = IPForm(request.form)
    if request.method == 'POST':
        if form.validate():
            respuesta = consulta(request.form['ip'])
            resultado = ast.literal_eval(respuesta.data.decode('utf-8'))
        else:
            resultado['Detail'] = 'No puede ser vacío'
            resultado['Status'] = 'ERROR'
    return render_template('index.html', form=form, resultado=resultado)

@app.route('/api/v1/ping/<ip>', methods = ['GET'])
@apiAuth.login_required
def ping(ip):
    return consulta(ip)

def consulta(ip):
    ipObj = None
    status = 400
    try:
        ipObj = ipaddress.ip_address(ip)
        socketObj = Connection.Connection(ipObj,infoLogger)
        data = socketObj.run()
        status = 200
    except ValueError as valueError:
        data = {'Detail': Connection.ResponseDetail.INVALID_IP.value, 'Status': Connection.ResponseStatus.KO.value}
        errorLogger.error(str(sys.exc_info()))
    except OSError as osError:
        data = {'Detail': 'Socket Error', 'Status': Connection.ResponseStatus.KO.value}
        errorLogger.error(str(sys.exc_info()))
    except:
        data = {'Detail': Connection.ResponseDetail.ERROR.value, 'Status': Connection.ResponseStatus.UNK.value}
        errorLogger.error(str(sys.exc_info()))
    finally:
        response = jsonify(data)
        response.status_code = status
        version = 0 if ipObj == None else ipObj.version
        src_dst = {'src': request.remote_addr, 'dst': ip, 'dst_version': version}
        infoLogger.info('{} | {} | {}'.format(g.usuario, src_dst, data))
        return response
