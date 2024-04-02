import requests
import json
import os
from datetime import datetime
import requests
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from time import sleep as wait

usuarioUrl = 'https://xavier-67637-default-rtdb.asia-southeast1.firebasedatabase.app/tests'

def callbackregister(self, *args):
  MDApp.get_running_app().root.current = 'login'

def go_to_dashboard(*args):
    MDApp.get_running_app().root.current = 'dashboard'

def go_to_frota(*args):
    MDApp.get_running_app().root.current = 'frota'

def go_to_tabela(*args):
    MDApp.get_running_app().root.current = 'tabela'

# Redireciona para o dashboard
def callbacklogin(self, *args):
  MDApp.get_running_app().root.current = 'frota'

def login(self, usuario, senha):
    try:
        banco = consultar_usuario(usuario)
        try:
            if str(banco['senha']) == str(senha):
                # Imprimir os dados para a chave atual
                self.ids.lblogin.text = 'Autenticado com Sucesso!'
                Clock.schedule_once(self.callbacklogin, 2)
            else:
                self.ids.lblogin.text = 'Credenciais Inválidas, Tente Novamente!'
                return None
        except AttributeError and TypeError:
            self.ids.lblogin.text = 'Credenciais Inválidas, Tente Novamente!'
            return None
    except Exception:
        self.ids.lblogin.text = 'Você está sem Internet'

def consultar_usuario(usuario):
    requisition = requests.get(url=f'{usuarioUrl}/usuarios/.json')
    res = requisition.json()
    try:
        for key, value in res.items():
            if value['usuario'] == usuario:
                dados = {
                    'chave': key,
                    'usuario': value['usuario'],
                    'senha': value['senha']
                }
                return dados
    except UnboundLocalError:
        dados = {
            'chave': 'lstrt87ylkkjuytr',
            'usuario': 'momomo',
            'senha': '32456387fbseodif1d2vey2evd8g3236fdv2u3dnecmodsp,c'
            }
        return dados

def consultar_matricula(ativosUrl):
    requisition = requests.get(url=f'{ativosUrl}/.json')
    res = requisition.json()
    return res

def reset_ativo(self):
    self.ids.matricula.text = ''
    self.ids.marca.text = ''
    self.ids.meta.text = ''
    self.ids.lbregister_pacient.text = ''

def reset_receita(self):
    self.ids.valor.text = ''
    self.ids.data.text = 'Escolha a data da Receita'
    self.ids.obs.text = ''

def reset_despesa(self):
    self.ids.valor.text = ''
    self.ids.data.text = 'Escolha a data da Despesa'
    self.ids.obs.text = ''
    
def criar_ativo(self, matricula, marca, meta, ativosUrl):
    if matricula == '':
        self.ids.lbregister_pacient.text = 'Preencher a Matrícula'
    elif marca == '':
        self.ids.lbregister_pacient.text = 'Preencher a Marca'
    elif meta == '':
        self.ids.lbregister_pacient.text = 'Preencher o Valor da Receita Mínima'
    else:
        res = consultar_matricula(ativosUrl)
        control = []
        dados = {
        'matricula':matricula,
        'marca':marca,
        'meta':meta,
        'icone':'images/sc1.png',
        'pagina':'dashboard',
        'status':'Disponível',
        }
        try:
            for key, value in res.items():
                control.append(value['matricula'])
        except AttributeError:
            pass

        if dados['matricula'] not in control:
            criar = requests.post(url=f'{ativosUrl}/.json', data=json.dumps(dados))
            reset_ativo(self)
            self.ids.lbregister_pacient.text = 'Ativo Cadastrado com Sucesso!'
        else:
            self.ids.lbregister_pacient.text = 'O Ativa existe Cadastrado'

def eliminarAtivo(matricula, ativosUrl, flowUrl):
    res = consultar_matricula(ativosUrl)
    control = []
    try:
        for key, value in res.items():
            control.append(value['matricula'])
            if value['matricula'] == matricula:
                eliminar = requests.delete(f'{ativosUrl}/{key}.json')
                elimDados = requests.delete(f'{flowUrl}/{matricula}.json')
        if matricula not in control:
            pass
    except AttributeError:
        pass

def modificarAtivo(matricula, ativosUrl, marca, status, meta):
    res = consultar_matricula(ativosUrl)

    dadosPatch = {
    'matricula': matricula,
    'marca':marca,
    'status':status,
    'meta':meta,
    }
    try:
        for key, value in res.items():
            if dadosPatch['matricula'] == value['matricula']:
                modificar = requests.patch(url=f'{ativosUrl}/{key}.json', data=json.dumps(dadosPatch))
            else:
                pass
    except AttributeError:
        pass

# CAIXA

def criar_despesa(self, matricula, data, valor, obs, flowUrl):

    data = datetime.strptime(data, "%Y-%m-%d")
    current_month = data.month
    current_year = data.year

    mes_ano = f"{current_year}/{current_month:02d}"

    if matricula == '':
        self.ids.lbreceita.text = 'Preencher a Matrícula'
    elif data == 'Escolha a data da Despesa' or '':
        self.ids.lbreceita.text = 'Preencher a Data'
    elif valor == '':
        self.ids.lbreceita.text = 'Preencher o Valor'
    else:
        dados = {
            'matricula': matricula,
            'Tipo de Entrada': 'Despesa',
            'ico': 'cash-minus',
            'data':str(data),
            'valor':valor,
            'observacao':obs,
            'mes':mes_ano,
        }
        try:
            criar = requests.post(url=f'{flowUrl}/{matricula}/.json', data=json.dumps(dados))
            reset_receita(self)
            self.ids.lbreceita.text = 'Despesa cadastrado com Sucesso!'
        except Exception as e:
            self.ids.lbreceita.text = 'Você está sem Internet'

def criar_receita(self, matricula, data, valor, obs, flowUrl):

    data = datetime.strptime(data, "%Y-%m-%d")
    current_month = data.month
    current_year = data.year

    mes_ano = f"{current_year}/{current_month:02d}"

    if matricula == '':
        self.ids.lbreceita.text = 'Preencher a Matrícula'
    elif data == 'Escolha a data da Receita' or '':
        self.ids.lbreceita.text = 'Preencher a Data'
    elif valor == '':
        self.ids.lbreceita.text = 'Preencher o Valor'
    else:
        dados = {
            'matricula': matricula,
            'Tipo de Entrada': 'Receita',
            'ico': 'cash-check',
            'data':str(data),
            'valor':valor,
            'observacao':obs,
            'mes':mes_ano,
        }
        try:
            criar = requests.post(url=f'{flowUrl}/{matricula}/.json', data=json.dumps(dados))
            reset_receita(self)
            self.ids.lbreceita.text = 'Receita cadastrado com Sucesso!'
        except Exception as e:
            self.ids.lbreceita.text = 'Você está sem Internet'

def modificarFluxo(matricula, chave, flowUrl, data, valor, obs):
    res = consultar_fluxo(matricula, flowUrl)

    dadosPatch = {
    'data': data,
    'valor':valor,
    'observacao':obs,
    }
    try:
        for key, value in res.items():
            if chave == key:
                modificar = requests.patch(url=f'{flowUrl}/{key}.json', data=json.dumps(dadosPatch))
            else:
                pass
    except AttributeError:
        pass

def consultar_fluxo(matricula, flowUrl):
    res = requests.get(url=f'{flowUrl}/{matricula}/.json')
    dados = res.json()
    return dados

def eliminar_Fluxo(matricula, chave, flowUrl):
    elimDados = requests.delete(f'{flowUrl}/{matricula}/{chave}.json')

def matricula(self, dataCard):
    self.ids.matricula.text = dataCard

# Salva a data escolhida pelo usuário
def on_save(self, instance, value, date_range):
    if value:
        self.ids.data.text = str(value)
    else:
        self.ids.data.text = "Escolha a data da Receita"

# Mostra a mensagem quando o usuário cancela a data
def on_cancel(self, instance, value):
    self.ids.data.text = "Escolha a data da Receita"

# Cria o calendario
def show_data_picker(self):
  year = datetime.now().year
  month = datetime.now().month
  day = datetime.now().day
  date_dialog = MDDatePicker(year, month, day)
  date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
  date_dialog.open()     