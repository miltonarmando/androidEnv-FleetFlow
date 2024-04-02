import json
import os
from datetime import datetime
from operator import itemgetter
import requests
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu


global screen
global firebaseConfig
global firebase2 
global lista2
global HORARIOS_SELECIONADOS

cardText = ''
ativosUrl = ''
flowUrl = ''

screen = ScreenManager()

lista2 = []
HORARIOS_SELECIONADOS = []  

class SplashScreen(Screen):
  def on_pre_enter(self, *args):
      if not os.path.exists('cred'):
          os.makedirs('cred')

class LoginScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.usuario.text = ''
        self.ids.senha.text = ''
        self.ids.lblogin.text = ''

    def callbacklogin(self, *args):
        from test import callbacklogin
        callbacklogin(self, *args)

    def getuserx(self, usuario, senha):
      global ativosUrlx
      global flowUrlx
      userName = self.ids.usuario.text
      ativosUrlx = f'https://xavier-67637-default-rtdb.asia-southeast1.firebasedatabase.app/tests/{userName}/ativos'
      flowUrlx = f'https://xavier-67637-default-rtdb.asia-southeast1.firebasedatabase.app/tests/{userName}/flow'
      ativosUrl = ativosUrlx
      flowUrl = flowUrlx
      from test import login
      login(self, usuario, senha)

class DashboardScreen(Screen):
  dialog = None
  def on_pre_enter(self):
    self.ids.lbdashboard.text = cardText
    self.ids.lbchange.text = ''

  def eliminar_ativo(self):
    # Criar e exibir o pop-up de confirmação
    self.dialog = MDDialog(
      text="Tem certeza de que deseja eliminar este ativo?",
      buttons=[
        MDFlatButton(text="Sim", on_release=self.confirmar_eliminar),
        MDFlatButton(text="Não", on_release=self.fechar_dialogo)
      ]
    )
    self.dialog.open()
  
  def fechar_dialogo(self, *args):
    self.dialog.dismiss()

  def confirmar_eliminar(self, matricula):
    from test import eliminarAtivo, go_to_frota
    eliminarAtivo(matricula=cardText, ativosUrl=ativosUrlx, flowUrl=flowUrlx)
    self.dialog.dismiss()
    self.ids.lbchange.text = f'Ativo Eliminado com Sucesso!'
    Clock.schedule_once(go_to_frota, 2)

class FrotaScreen(Screen):
  def on_pre_enter(self):
    self.ids.frota.clear_widgets()  # Limpa os widgets existentes antes de adicionar novos
    self.list_frota()

  def on_pre_enter(self):
    self.ids.lbtitulo.text = "Ativos Disponíveis"
    self.list_frota()

  def list_frota(self):
    from test import consultar_matricula, consultar_fluxo
    try:
      dados = consultar_matricula(ativosUrlx)
      self.ids.frota.clear_widgets()

      for key, value in dados.items():
        try:
          soma_receita = 0
          soma_despesa = 0
          saldo = consultar_fluxo(value['matricula'], flowUrlx)
        
          for key, value2 in saldo.items():
            if value2['Tipo de Entrada']=='Receita':
              soma_receita += int(value2['valor'])
            if value2['Tipo de Entrada']=='Despesa':
              soma_despesa += int(value2['valor'])
            if int(soma_receita) == 0:
              target = str(0)
            else:
              target = str(1-(int(soma_despesa)/int(soma_receita)) if int(soma_despesa) != 0 else 1 if int(soma_receita)!=0 else 1)
            if float(target) > 0.7:
              statusLucro = 'aderente'
            else:
              statusLucro = 'nao_aderente'
        except AttributeError:
          statusLucro = 'nao_aderente'

        self.ids.frota.add_widget(FrotaCard(
          matricula=value['matricula'],          
          icone=value['icone'],
          pagina=value['pagina'],
          status = value['status'],
          farol = statusLucro
          ))
    
    except AttributeError:
      self.ids.lbtitulo.text = 'Ativos Disponíveis'
    
  def getStatus(self):
      global status_ativo
      global status_saldo
      from test import consultar_fluxo, consultar_matricula
      ativo = consultar_matricula(ativosUrlx)
      saldo = consultar_fluxo(cardText,flowUrlx)

class FrotaCard(MDCard):
    matricula = StringProperty()
    icone = StringProperty()
    pagina = StringProperty()
    status = StringProperty()
    farol = StringProperty()
    
    def on_card_click(self):
        global cardText
        cardText = ''
        cardText = self.matricula
        MDApp.get_running_app().root.current = 'dashboard'

class CreateAssetScreen(Screen):
  def on_pre_enter(self, *args):
    from test import reset_ativo
    reset_ativo(self)

  def cadastroAtivo(self, matricula, marca, meta):
    from test import criar_ativo
    criar_ativo(self, matricula, marca, meta, ativosUrlx)

class ChangeAssetScreen(Screen):
  matricula = StringProperty()
  marca = StringProperty()
  status = StringProperty()
  meta = StringProperty()
  
  ativosUrl = ativosUrl
  def show_dropdown_options(self):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": f"Disponível", "on_release": lambda x=f"Disponível": self.set_status(x)},
            {"viewclass": "OneLineListItem", "text": f"Avariado", "on_release": lambda x=f"Avariado": self.set_status(x)}
        ]
        self.menu = MDDropdownMenu(caller=self.ids.dropdown_status, items=menu_items, width_mult=4)
        self.menu.open()

  def set_status(self, x):
      self.ids.dropdown_status.text = x
      self.menu.dismiss()

  def editaInfo(self, cardText, marca, status, meta):
    from test import modificarAtivo, consultar_matricula, go_to_dashboard
    res = consultar_matricula(ativosUrlx)
    for key, value in res.items():
      if value['matricula'] == self.ids.matricula.text:
        modificarAtivo(ativosUrl=ativosUrlx, matricula=cardText, marca=marca, status=status, meta=meta)
        self.ids.lbchange.text = f'Modificado com sucesso!'
        Clock.schedule_once(go_to_dashboard, 4.5)

  def on_pre_enter(self, *args):
    from test import consultar_matricula
    res = consultar_matricula(ativosUrlx)
    for key, value in res.items():
      if value['matricula'] == cardText:
        self.ids.matricula.text = value['matricula']
        self.ids.meta.text = value['meta']
        self.ids.marca.text = value['marca']
        self.ids.dropdown_status.text = value['status']
        self.ids.lbchange.text = ''

class DespesaScreen(Screen):
  def on_pre_enter(self, *args):
    from test import matricula,reset_despesa
    reset_despesa(self)
    self.ids.lbreceita.text = ''
    self.ids.data.text = "Escolha a data da Despesa"
    matricula(self, dataCard=cardText)

  def cadastrarReceita(self, matricula, data, valor, obs):
    from test import criar_despesa
    criar_despesa(self, matricula, data, valor, obs, flowUrlx)

  def on_save(self, instance, value, data_range):
    from test import on_save
    on_save(self, instance, value, data_range)

  def on_cancel(self, instance, value):
    from test import on_cancel
    on_cancel(self, instance, value)

  def data(self):
    from test import show_data_picker
    show_data_picker(self)          

class ReceitaScreen(Screen):
  def on_pre_enter(self, *args):
    from test import matricula,reset_receita
    reset_receita(self)
    self.ids.lbreceita.text = ''
    self.ids.data.text = "Escolha a data da Receita"
    matricula(self, dataCard=cardText)

  def cadastrarReceita(self, matricula, data, valor, obs):
    from test import criar_receita
    criar_receita(self, matricula, data, valor, obs, flowUrlx)

  def on_save(self, instance, value, data_range):
    from test import on_save
    on_save(self, instance, value, data_range)

  def on_cancel(self, instance, value):
    from test import on_cancel
    on_cancel(self, instance, value)

  def data(self):
    from test import show_data_picker
    show_data_picker(self)          

class FlowChangeScreen(Screen):
  titulo = StringProperty()
  data = StringProperty()
  valor = StringProperty()
  obs = StringProperty()

  def on_pre_enter(self):
    global dataset
    self.ids.data.text = MDApp.get_running_app().AppData
    self.ids.valor.text = MDApp.get_running_app().AppValor
    self.ids.obs.text =  MDApp.get_running_app().AppObs
    self.tipox = MDApp.get_running_app().AppTipo
    self.titulo = f'{self.tipox} de {cardText}'
    dataset = MDApp.get_running_app().AppData
    self.ids.lbchange.text = ''

  def gravar(self, data, valor, obs):
    from test import go_to_tabela
    datax = datetime.strptime(data, "%Y-%m-%d")
    current_month = datax.month
    current_year = datax.year

    mes_ano = f"{current_year}/{current_month:02d}"

    dadosPatch = {
    'data': data,
    'valor': valor,
    'observacao': obs,
    'mes': str(mes_ano),
    }
    chave = MDApp.get_running_app().chave_selecionada
    
    modificar = requests.patch(url=f'{flowUrlx}/{cardText}/{chave}.json', data=json.dumps(dadosPatch))
    self.ids.lbchange.text = f'Operação de {self.tipox} foi modificada!'
    Clock.schedule_once(go_to_tabela, 2)

  def on_save(self, instance, value, data_range):
    from test import on_save
    on_save(self, instance, value, data_range)

  def on_cancel(self, instance, value):
    from test import on_cancel
    on_cancel(self, instance, value)
    self.ids.data.text = MDApp.get_running_app().AppData

  def data(self):
    from test import show_data_picker
    show_data_picker(self)

'''
#####----------BUSCA NA VERSÃO PROFISSIONAL--------########
class FlowViewScreen(Screen):
  def on_pre_enter(self):
    chave = MDApp.get_running_app().chave_selecionada
    res = requests.get(url=f'{flowUrlx}/{cardText}/{chave}.json')

    data = res.json()
#####----------BUSCA NA VERSÃO PROFISSIONAL--------########
'''

class FlowViewScreen(Screen):
  titulo = StringProperty()
  data = StringProperty()
  valor = StringProperty()
  obs = StringProperty()
    
  def on_pre_enter(self):
    global chave
    chave = MDApp.get_running_app().chave_selecionada
    from test import consultar_fluxo
    res = consultar_fluxo(cardText, flowUrlx)
    for key, value in res.items():
      tipo = value['Tipo de Entrada']
      data = value['data']
      valor = value['valor']
      obs = value['observacao']
      if key == chave:
        self.titulo = f'{tipo} de {cardText}'
        self.data = data[:10]
        self.valor = f'{valor} MZN'
        self.obs = str(obs)
        self.tipo = tipo
  
  def editarClick(self):
    app = MDApp.get_running_app()  # Obtém a instância do aplicativo
    app.AppData = self.data
    app.AppValor = self.valor.replace(' ', '').replace('MZN', '')
    app.AppObs = self.obs.replace('-','')
    app.AppTipo = self.tipo
    self.manager.current = 'changeFlowX'
  
  def eliminarFlow(self):
    self.dialog = MDDialog(
        text="Tem certeza de que deseja eliminar a operação?",
        buttons=[
          MDFlatButton(text="Sim", on_release=self.confirmar_eliminar),
          MDFlatButton(text="Não", on_release=self.fechar_dialogo)
        ]
      )
    self.dialog.open()
  
  def fechar_dialogo(self, *args):
    self.dialog.dismiss()

  def confirmar_eliminar(self, *args):
    from test import go_to_tabela
    requests.delete(f'{flowUrlx}/{cardText}/{chave}.json')
    self.dialog.dismiss()
    self.ids.lbchange.text = f'Eliminado com Sucesso!'
    Clock.schedule_once(go_to_tabela, 2)

class RelatorioScreen(Screen):
    somaReceitas = StringProperty()
    somaDespesas = StringProperty()
    statusA = StringProperty()
    target = StringProperty()
    lucro = StringProperty()
    matriculax = StringProperty()
    chave = StringProperty()

    def on_dropdown_select(self, x):
      self.ids.dropdown_item.text = x
      self.menu.dismiss()
      self.consultar_e_atualizar_widgets()
      

    def show_dropdown_options(self):
      menu_items = []

      current_month = datetime.now().month
      current_year = datetime.now().year

      months = [{"viewclass": "OneLineListItem", 
                         "text": f"Global",
                         "on_release": lambda x=f" Global": self.on_dropdown_select(x)}]
      for i in range(-12, 1):
          month = (current_month + i - 1) % 12 + 1
          year = current_year + (current_month + i - 1) // 12
          months.append({"viewclass": "OneLineListItem", 
                         "text": f"{year}/{0 if month<10 else ''}{month}",
                         "on_release": lambda x=f"{year}/{0 if month<10 else ''}{month}": self.on_dropdown_select(x)})
      
      sorted_months = sorted(months, key=itemgetter('text'), reverse=True)  # Ordenar os meses pelo texto (data)
      menu_items.extend(sorted_months)

      self.menu = MDDropdownMenu(caller=self.ids.dropdown_item,
                                  items=menu_items, 
                                  width_mult=4)
      self.menu.open()

    def on_item_click(self, instance):
      chave = instance.custom_data['chave']  # Supondo que a chave seja armazenada em custom_data
      app = MDApp.get_running_app()  # Obtém a instância do aplicativo
      app.chave_selecionada = chave  # Define a chave selecionada como uma variável de classe do aplicativo
      self.manager.current = 'viewFlow'
    
    def consultar_e_atualizar_widgets(self, tipo_filtro=None):
        from test import consultar_fluxo
        # Limpa os widgets existentes na tela
        self.ids.layout.clear_widgets()
        # Consulta a receita
        dadosR = consultar_fluxo(matricula=cardText, flowUrl=flowUrlx)
        somaReceitas = 0
        somaDespesas = 0
        statusA = 0
        target = None
        lucro = 0

        try:
            # Itera sobre os dados
            for key, value in dadosR.items():
              if value['mes'] == self.ids.dropdown_item.text:
                # Verifica se o tipo é igual a 'receita' ou 'despesa'
                if tipo_filtro is None or value['Tipo de Entrada'] == tipo_filtro:
                    data = str(value["data"])
                    valor = str(value["valor"])
                    obs = str(value['observacao'])
                    tipo_entrada = str(value['Tipo de Entrada'])
                    
                    pickcor = (0, 0.5, 0, 0.65) if tipo_entrada == 'Receita' else (1, 0, 0, 0.7)

                    if value['Tipo de Entrada'] == 'Despesa':
                      somaDespesas += int(value["valor"])

                    if value['Tipo de Entrada'] == 'Receita':
                      somaReceitas += int(value["valor"])

                    # Cria um item da lista com o texto e o ícone da data
                    _value = ThreeLineAvatarIconListItem(
                        text=f'{data[:10]}',
                        theme_text_color='Custom',
                        text_color='gray',
                        secondary_text=f'{tipo_entrada}',
                        secondary_theme_text_color='Custom',
                        secondary_text_color=pickcor,
                        tertiary_text=f"{obs if obs != '' else '-'}",
                        tertiary_theme_text_color='Custom',
                        tertiary_text_color='gray',
                        tertiary_font_style='Overline',
                        bg_color=(0.8, 0.8, 0.8, 0.25),
                    )
                    _value.custom_data = {'chave': key}
                    _value.bind(on_release=lambda instance: self.on_item_click(instance))

                    # Adiciona um ícone ao item da list
                    _value.add_widget(IconLeftWidget(icon=value['ico'], theme_text_color="Custom", text_color=pickcor, icon_size="40sp", halign='center', padding=(16, 0.5)))

                    # Criando o MDLabel com o valor da receita/despesa
                    label = MDLabel(
                        text=f'{valor} MZN',
                        halign='center',
                        theme_text_color='Custom',
                        text_color='white',  # Cor do texto
                        font_style='Body2',
                    )

                    label.texture_update()
                    text_width, text_height = label.texture_size

                    # Define o tamanho do MDCard baseado no tamanho do texto
                    card_width = text_width  # Adiciona um espaçamento de 8 dp em cada lado
                    card_height = text_height  # Adiciona um espaçamento de 8 dp em cada lado

                    # Cria o MDCard com o tamanho ajustado automaticamente
                    card = MDCard(padding=8, size_hint=(0.27, 0.4), md_bg_color=pickcor,
                                  size=(card_width, card_height),
                                  pos_hint=({'center_x': 0.8, 'center_y': 0.6}))
                    card.add_widget(label)

                    # Adiciona o MDCard como um widget filho do ThreeLineAvatarIconListItem
                    _value.add_widget(card)

                    # Adiciona o item à tela
                    self.ids.layout.add_widget(_value)

              elif self.ids.dropdown_item.text == ' Global':
                # Verifica se o tipo é igual a 'receita' ou 'despesa'
                if tipo_filtro is None or value['Tipo de Entrada'] == tipo_filtro:
                    data = str(value["data"])
                    valor = str(value["valor"])
                    obs = str(value['observacao'])
                    tipo_entrada = str(value['Tipo de Entrada'])
                    
                    pickcor = (0, 0.5, 0, 0.65) if tipo_entrada == 'Receita' else (1, 0, 0, 0.7)

                    if value['Tipo de Entrada'] == 'Despesa':
                      somaDespesas += int(value["valor"])

                    if value['Tipo de Entrada'] == 'Receita':
                      somaReceitas += int(value["valor"])

                    # Cria um item da lista com o texto e o ícone da data
                    _value = ThreeLineAvatarIconListItem(
                        text=f'{data[:10]}',
                        theme_text_color='Custom',
                        text_color='gray',
                        secondary_text=f'{tipo_entrada}',
                        secondary_theme_text_color='Custom',
                        secondary_text_color=pickcor,
                        tertiary_text=f"{obs if obs != '' else '-'}",
                        tertiary_theme_text_color='Custom',
                        tertiary_text_color='gray',
                        tertiary_font_style='Overline',
                        bg_color=(0.8, 0.8, 0.8, 0.25),
                    )
                    _value.custom_data = {'chave': key}
                    _value.bind(on_release=lambda instance: self.on_item_click(instance))
                    # Adiciona um ícone ao item da list
                    _value.add_widget(IconLeftWidget(icon=value['ico'], theme_text_color="Custom", text_color=pickcor, icon_size="40sp", halign='center', padding=(16, 0.5)))

                    # Criando o MDLabel com o valor da receita/despesa
                    label = MDLabel(
                        text=f'{valor} MZN',
                        halign='center',
                        theme_text_color='Custom',
                        text_color='white',  # Cor do texto
                        font_style='Body2',
                    )

                    label.texture_update()
                    text_width, text_height = label.texture_size

                    # Define o tamanho do MDCard baseado no tamanho do texto
                    card_width = text_width  # Adiciona um espaçamento de 8 dp em cada lado
                    card_height = text_height  # Adiciona um espaçamento de 8 dp em cada lado

                    # Cria o MDCard com o tamanho ajustado automaticamente
                    card = MDCard(padding=8, size_hint=(0.27, 0.4), md_bg_color=pickcor,
                                  size=(card_width, card_height),
                                  pos_hint=({'center_x': 0.8, 'center_y': 0.6}))
                    card.add_widget(label)

                    # Adiciona o MDCard como um widget filho do ThreeLineAvatarIconListItem
                    _value.add_widget(card)

                    # Adiciona o item à tela
                    self.ids.layout.add_widget(_value) 
              
            self.somaDespesas = str(f'{somaDespesas} MZN')
            self.somaReceitas = str(f'{somaReceitas} MZN')
            lucro = somaReceitas-somaDespesas
            self.lucro = str(f'{lucro} MZN')
            if int(somaReceitas) == 0:
              self.target = str(0)
            else:
              self.target = str(1-(int(somaDespesas)/int(somaReceitas)) if int(somaDespesas) != 0 else 1 if int(somaReceitas)!=0 else 1)
            
            if float(self.target) > 0.7:
              self.statusA = 'aderente'
            else:
              self.statusA = 'nao_aderente'
        except AttributeError:
            pass
        
    def on_pre_leave(self):
        self.ids.layout.clear_widgets()
        self.somaDespesas = str(f'0,00 MZN')
        self.somaReceitas = str(f'0,00 MZN')
        self.lucro = str(f'0,00 MZN')
        self.ids.dropdown_item.text = ' Global'


    def on_pre_enter(self):
        self.somaDespesas = str(f'0,00 MZN')
        self.somaReceitas = str(f'0,00 MZN')
        self.lucro = str(f'0,00 MZN')
        self.matriculax = cardText
        self.consultar_e_atualizar_widgets()

    def filtrar_por_tipo(self, tipo):
        self.consultar_e_atualizar_widgets(tipo)

    def filtrar_receitas(self):
        self.consultar_e_atualizar_widgets('Receita')

    def filtrar_despesas(self):
        self.consultar_e_atualizar_widgets('Despesa')

    def filtrar_tudo(self):
        self.consultar_e_atualizar_widgets(None)   
 
screen.add_widget(SplashScreen(name='splash'))
screen.add_widget(LoginScreen(name='login'))
screen.add_widget(DashboardScreen(name='dashboard'))
screen.add_widget(ReceitaScreen(name='checkin'))
screen.add_widget(DespesaScreen(name='checkout'))
screen.add_widget(RelatorioScreen(name='verifymeds'))
screen.add_widget(CreateAssetScreen(name='cadastroativo'))
screen.add_widget(FrotaScreen(name='frota'))
screen.add_widget(FlowChangeScreen(name='changeFlowX'))
screen.add_widget(FlowViewScreen(name='viewFlow'))

class FleetFlowApp(MDApp):

  def build(self):
    kv = Builder.load_file("telas.kv")
    screen = kv
    return screen

if __name__ == "__main__":
    FleetFlowApp().run()
