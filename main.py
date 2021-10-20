"""
Aplicativo SAGE TreeView

        Feito para facilitar a consulta de dados  inseridos no sistema SAGE
        
        Instruções de uso:
            
            1.	Introduza as informações de login para acessar o SAGE clicando no botão "Conexão" do menu superior
            2.	Navegue pelos itens e clique no nome do item desejado para receber os dados da base
            3.	As abas na parte direita da janela apresentam as informações de forma categorizada
            4.	Selecione um intervalo de tempo e use o botão "Consultar" para gravar os dados em questão em um arquivo CSV
            
"""

# Bibliotecas
import sys
import json
import os
import psycopg2
import psycopg2.extras
import pandas as pd
import pandas.io.sql as sqlio
import Tree.Tree as Tree
import Table.Table as Table
import PyQt5.uic as uic
from PyQt5 import QtWidgets, QtGui, QtCore
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

# Caminhos
path = os.path.dirname(os.path.abspath(sys.argv[0]))
icon_path = path + '\\Icon\\'
save_path = os.getenv('LOCALAPPDATA') + '\\SAGE TreeView\\config'
os.makedirs(save_path, exist_ok=True)

# Possíveis erros de consulta SQL
errors = (sqlio.DatabaseError, psycopg2.OperationalError, BaseSSHTunnelForwarderError, ValueError, IndexError, EOFError)


# Classe principal
class App(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        # Janela principal
        self.ui = uic.loadUi(path+'\\UI\\Janela.ui')
        self.ui.setWindowIcon(QtGui.QIcon(icon_path+'SAGE TreeView.png'))
        
        # Janela de conexão
        self.ui_connection = uic.loadUi(path+'\\UI\\conexao.ui')
        self.ui_connection.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.ui_connection.setWindowIcon(QtGui.QIcon(icon_path+'conexao.png'))
        
        self.table_window = Table.TableWindow()

        # Interação com o treeview
        self.ui.treeWidget.itemClicked.connect(self.tree_selection)
        self.ui.treeWidget.itemExpanded.connect(self.add_nodes)
        
        # Abrir janela de conexão
        self.ui.open_connection.triggered.connect(self.connection_window)
        
        # Botões das abas
        self.ui.consult_button.clicked.connect(self.consult)
        self.ui.alarm_button.clicked.connect(self.alarm)
        self.ui.severity_check.clicked.connect(self.enable_severity_list)
        self.ui.movie_button.clicked.connect(self.movie)
        
        # Botões da janela de conexão
        self.ui_connection.connection_test_button.clicked.connect(self.check_connection)
        self.ui_connection.buttons.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.connection)
        self.ui_connection.buttons.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.connection)
        self.ui_connection.save_button.clicked.connect(self.save_configuration)
        self.ui_connection.load_button.clicked.connect(self.load_configuration)
        
        # Inicialização de variáveis
        self.root = None
        self.conn = None
        self.tunnel = None
        self.att_table = None
        
        # Tamanho dos ícones do treeview
        self.ui.treeWidget.setIconSize(QtCore.QSize(28, 28))
        
        # Inicializando as datas de início e fim na data atual
        date = QtCore.QDate.currentDate()
        self.ui.start_date.setDate(date.addDays(-1))
        self.ui.end_date.setDate(date)
        
        # Ícone da janela de conexão
        self.ui.open_connection.setIcon(QtGui.QIcon(icon_path+'conexao.png'))
    
    # Habilitar ou desabilitar lista de severidades
    def enable_severity_list(self):
        if self.ui.severity_check.isChecked():
            self.ui.severity_list.setEnabled(True)
        else:
            self.ui.severity_list.setEnabled(False)
            self.ui.severity_list.clearSelection()
    
    # Obtem a configuração da janela de conexão
    def connection_configuration(self):
        
        config = {
            'remote_address': self.ui_connection.ssh_remote_address.text(),
            'remote_port': self.ui_connection.ssh_remote_port.text(),
            'local_address': self.ui_connection.ssh_local_address.text(),
            'local_port': self.ui_connection.ssh_local_port.text(),
            'intermediate_port': self.ui_connection.ssh_intermediate_port.text(),
            'user': self.ui_connection.ssh_user.text(),
            'password': self.ui_connection.ssh_password.text(),
            'file': fr'{self.ui_connection.ssh_file.text()}'
        }
        return config
        
    # Salva a configuração em um arquivo JSON
    def save_configuration(self):
        
        config = self.connection_configuration()
        
        with open(save_path+'\\config.json', 'w+') as file:
            json.dump(config, file, indent=4)
    
    # Recupera a configuração a partir do arquivo
    def load_configuration(self):
        
        try:
            with open(save_path+'\\config.json', 'r+') as file:
                config = json.load(file)
                
                self.ui_connection.ssh_remote_address.setText(config['remote_address'])
                self.ui_connection.ssh_remote_port.setText(config['remote_port'])
                self.ui_connection.ssh_local_address.setText(config['local_address'])
                self.ui_connection.ssh_local_port.setText(config['local_port'])
                self.ui_connection.ssh_intermediate_port.setText(config['intermediate_port'])
                self.ui_connection.ssh_user.setText(config['user'])
                self.ui_connection.ssh_password.setText(config['password'])
                self.ui_connection.ssh_file.setText(config['file'])
        
        except FileNotFoundError:
            self.info('Não encontrado', 'Não foi possível localizar o arquivo de configuração')

    # Checagem de conexão
    def check_connection(self):
        
        icon = 'bad'
        status = False
        
        if (self.tunnel is not None) and (self.conn is not None):
            
            if self.tunnel.is_active and (self.conn.closed == 0):
                icon = 'ok'
                status = True
                
        self.ui_connection.connection_test_button.setIcon(QtGui.QIcon(icon_path + icon + '.png'))
    
        return status

    # Estabelece a conexão
    def connection(self):
        
        if self.check_connection():
            
            pass
        
        else:
            
            config = self.connection_configuration()
            try:
                
                self.tunnel = SSHTunnelForwarder(
                        (config['remote_address'], int(config['remote_port'])),
                        ssh_username=config['user'],
                        remote_bind_address=(config['local_address'], int(config['local_port'])),
                        local_bind_address=('localhost', int(config['intermediate_port'])),
                        ssh_pkey=config['file'],
                        ssh_private_key_password=config['password']
                )
                
                self.tunnel.start()
                
                self.conn = psycopg2.connect(
                        dbname='bhdemo_ems_sage',
                        user='sage',
                        password='sage',
                        host='localhost',
                        port=int(config['intermediate_port'])
                )
                
                self.build_tree()
            
            except errors:
                self.info('Falha na conexão', 'Tente se reconectar usando a janela de conexão ou reinicie a aplicação')
    
    # Insere a base do treeview
    def build_tree(self):
        
        self.ui.treeWidget.clear()
        self.root = Tree.TreeNode('sistema', 'Sistema Elétrico', connection=self.conn)
        Tree.add_node(self.ui.treeWidget, self.root)
    
    # Adiciona nódulos aos items da treeview
    def add_nodes(self, item: QtWidgets.QTreeWidgetItem):
        
        try:
            Tree.add_nodes(item, self.conn)
        except errors:
            if not self.check_connection():
                self.tunnel.stop()
                self.connection()
    
    # Função ativada ao selecionar um item qualquer
    def tree_selection(self, item: QtWidgets.QTreeWidgetItem):
        
        if self.check_connection():
            
            data = Tree.get_info(item)
    
            entity = data['entity']
            name = data['identifier']
            bh_chave = data['bh_chave']
    
            self.ui.general_name.setText(name)

            try:
                t = sqlio.read_sql_query("select * from entidade_bh where nome=%(entity)s", self.conn, params={'entity': entity+'_r'})
                template = str(t['descr'][0]).strip()
                self.ui.general_template.setText(template)
            except errors:
                self.ui.general_template.clear()
            
            g = pd.DataFrame()
            
            try:
                
                g = sqlio.read_sql_query(f'select * from atributo_bh where ent in (select nome from entidade_bh where entbd=%(entity)s and esqgrv=\'\')', self.conn, params={'entity': entity})
                h = sqlio.read_sql_query(f'select * from atributo_bh where ent in (select nome from entidade_bh where entbd=%(entity)s and esqgrv<>\'\')', self.conn, params={'entity': entity})
                self.tab_consult(g, h)
            
            except errors:
                pass
            
            try:
                query = f"select * from {entity}_r where bh_chave={bh_chave}"
                m = sqlio.read_sql_query(query, self.conn)
                self.tab_general(g, m)
            except errors:
                self.ui.general_description.setText(name)
        
        else:
            self.connection()
    
    # Consultar: aba Consulta
    def consult(self):
        
        if self.check_connection():
            
            static = self.ui.consult_static_attributes.selectedItems()
            historied = self.ui.consult_historied_attributes.selectedItems()
            
            try:
                item = self.ui.treeWidget.selectedItems()[0]
            except IndexError:
                item = QtWidgets.QTreeWidgetItem()
            
            data = Tree.get_info(item)
            
            entity = data['entity']
            bh_chave = data['bh_chave']

            g = pd.DataFrame()
            
            if len(historied) > 0:
                
                self.table_window.allow_menubar(True)
                self.table_window.clear_plot()
                
                att_hist = 'bh_dthr as tempo'
                
                for att in historied:
                    
                    att = att.text().strip()
                    
                    if att == 'a1_flags':
                        att = 'flag'
                    elif att == 'a2_flags':
                        att = 'flagest'
                    elif att == 'estad':
                        att = 'estado'
                    elif att == 'Isupa':
                        att = 'Isa'
                    
                    att_hist += ',' + att
    
                start = self.ui.start_date.dateTime().toPyDateTime()
                end = self.ui.end_date.dateTime().toPyDateTime()
                
                try:
                    query = f"select {att_hist} from {entity}_h where ((bh_chave={bh_chave}) and (bh_dthr between \'{start}\' and \'{end}\')) order by tempo"
                    g = sqlio.read_sql_query(query, self.conn)
                except errors:
                    pass
            
            try:
    
                att_stat = []
    
                for att in static:
                    att_stat.append(att.text().strip())
            
                h = self.att_table.loc[self.att_table['Nome'].isin(att_stat)]
                h = {i: [j] for i, j in zip(h['Nome'], h['Valor'])}
                h = pd.DataFrame(h)
                
            except AttributeError:
                
                h = pd.DataFrame()
        
            table = pd.concat((g, h), axis=1)
            table.ffill(0, True)
            
            if table.empty:
                self.info('Tabela Vazia', 'A pesquisa retornou dados vazios')

            self.table_window.set_data(table)
            self.table_window.ui_show()
        
        else:
            self.connection()
    
    # Consultar: aba Alarmes
    def alarm(self):
        
        if self.check_connection():
            
            g = pd.DataFrame()
            
            severity_dict = {
                'Advertência': 'K_SEV_ADVER',
                'Fatal': 'K_SEV_FATAL',
                'Normal': 'K_SEV_NORML',
                'Pânico': 'K_SEV_PANIC',
                'Nula': 'K_SEV_SNULA',
                'Urgência': 'K_SEV_URGEN'
            }
            
            sev_check = self.ui.severity_check.isChecked()
            
            alarm_list = self.ui.alarm_list.selectedItems()
            
            start = self.ui.start_date.dateTime().toPyDateTime()
            end = self.ui.end_date.dateTime().toPyDateTime()
            
            try:
                item = self.ui.treeWidget.selectedItems()[0]
            except IndexError:
                item = QtWidgets.QTreeWidgetItem()
            
            data = Tree.get_info(item)
            bh_mrid = data['bh_mrid']
            
            alrm = ''
            
            for item in alarm_list:
                item = item.text().strip()
                alrm += item + ','
            alrm = alrm.rstrip(',')
            
            if sev_check:
                
                severity_list = self.ui.severity_list.selectedItems()
                
                sev = ''
                
                for item in severity_list:
                    item = item.text().strip()
                    item = severity_dict[item]
                    sev += f'severidade=\'{item}\' or '
                sev = sev.rstrip(' or ')
                
                query = f'select {alrm} from eve_h where ((mrid=\'{bh_mrid}\') and (bh_dthr between \'{start}\' and \'{end}\') and ({sev})) order by bh_dthr'
            
            else:
                
                query = f'select {alrm} from eve_h where ((mrid=\'{bh_mrid}\') and (bh_dthr between \'{start}\' and \'{end}\')) order by bh_dthr'
                
            try:
                g = sqlio.read_sql_query(query, self.conn)
            except errors:
                pass
            
            self.table_window.clear_plot()
            self.table_window.set_data(g)
            self.table_window.ui_show()
            
        else:
            self.connection()
    
    # Consultar: aba Filme
    def movie(self):
        
        if self.check_connection():
            
            selected = self.ui.movie_list.selectedItems()

            try:
                item = self.ui.treeWidget.selectedItems()[0]
            except IndexError:
                item = QtWidgets.QTreeWidgetItem()
            
            data = Tree.get_info(item)
            
            entity = data['entity']
            bh_chave = data['bh_chave']
            
            att_hist = []
            
            for att in selected:
                
                att = att.text().strip()
                
                if att == 'a1_flags':
                    att = 'flag'
                elif att == 'a2_flags':
                    att = 'flagest'
                elif att == 'estad':
                    att = 'estado'
                elif att == 'Isupa':
                    att = 'Isa'
                
                att_hist.append(att)

            columns = ','.join([f'avg({k}) as {k}' for k in att_hist])
            
            start = self.ui.start_date.dateTime().toPyDateTime()
            end = self.ui.end_date.dateTime().toPyDateTime()
            
            time_step = self.ui.granularity.text()
            time_scale = self.ui.granularity_scale.currentData(0)
            
            time_scale_dict = {
                'segundo(s)': 'seconds',
                'minuto(s)': 'minutes',
                'hora(s)': 'hours',
                'dia(s)': 'days'
            }
            
            time_scale = time_scale_dict[time_scale]
            
            g = pd.DataFrame()
            
            query = f'select time_bucket_gapfill(\'{time_step} {time_scale}\', bh_dthr) as tempo,{columns} from {entity}_h where ((bh_dthr between \'{start}\' and \'{end}\') and (bh_chave={bh_chave})) group by tempo order by tempo'
            
            try:
                g = sqlio.read_sql_query(query, self.conn)
                g['tempo'] = g['tempo'] - pd.DateOffset(hours=3)
                
            except errors:
                pass

            self.table_window.allow_menubar(True)
            self.table_window.clear_plot()
            self.table_window.set_data(g)
            self.table_window.ui_show()
            
        else:
            self.connection()
    
    # Aba Consulta
    def tab_consult(self, static, historied):

        self.ui.consult_static_attributes.clear()
        self.ui.consult_historied_attributes.clear()
        self.ui.movie_list.clear()
        
        for att in static['atrbd']:
            att = str(att).strip()
            if att == '':
                break
            self.ui.consult_static_attributes.addItem(QtWidgets.QListWidgetItem(att))
        
        for att in historied['atrbd']:
            att = str(att).strip()
            if att == '':
                break
            self.ui.consult_historied_attributes.addItem(QtWidgets.QListWidgetItem(att))
            self.ui.movie_list.addItem(QtWidgets.QListWidgetItem(att))
    
    # Aba Geral
    def tab_general(self, static, reference):
        
        name_ref = []
        name = []
        value = []
        description = []
        
        for att1, att2, att3 in zip(static['nome'], static['atrbd'], static['descr']):
            name_ref.append(str(att1).strip())
            name.append(str(att2).strip())
            description.append(str(att3).strip())
        
        if 'descr' in name_ref:
            self.ui.general_description.setText(reference['descr'][0])
        
        for att in name_ref:
            s = str(reference[att][0]).strip()
            value.append(s)
        
        self.att_table = pd.DataFrame({'Nome': name, 'Valor': value, 'Descrição': description})
        
        Table.set_table_options(self.ui.tableView, Table.PandasModel(self.att_table))
    
    # Informações
    def info(self, text, info_text=''):
        
        warn = QtWidgets.QMessageBox(self)
        warn.setWindowTitle('Aviso')
        warn.setText(text)
        
        if len(info_text) > 0:
            warn.setInformativeText(info_text)
            
        warn.setIcon(warn.Information)
        warn.setStandardButtons(warn.Ok | warn.Cancel)
        warn.show()
    
    # Mostrar janela principal
    def ui_show(self):
        self.ui.show()
        
    # Mostrar janela de conexão
    def connection_window(self):
        self.ui_connection.show()
        self.check_connection()
        
    # DEBUG
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)


app = None


def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    p = App()
    app.setStyle('fusion')
    p.ui_show()
    sys.excepthook = p.except_hook
    app.exec()


if __name__ == '__main__':
    main()
