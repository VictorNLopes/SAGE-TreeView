"""

Módulo Table

        Define os principais elementos para a construção da janela de visualização de tabelas

"""


# Bibliotecas
import sys
import os
import pandas as pd
import Options.GraphicOpt as graphics
import PyQt5.uic as uic
from PyQt5 import QtWidgets, QtGui, QtCore


# Caminhos
path = os.path.dirname(os.path.abspath(sys.argv[0]))
icon_path = path + '\\Icon\\'
user_path = os.getenv('userprofile')


# Modelo da tabela
class PandasModel(QtCore.QAbstractTableModel):
    
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data
        
    # Método para salvar a tabela
    def save(self, name: str):
        self._data.to_csv(name, ';', index=False)
        
    def get_data(self):
        return self._data
    
    # Número de linhas
    def rowCount(self, parent=None):
        return self._data.shape[0]
    
    # Número de colunas
    def columnCount(self, parent=None):
        return self._data.shape[1]
    
    # Dados
    def data(self, index, role=QtCore.Qt.DisplayRole):
        
        if index.isValid():
            
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            
            if role == QtCore.Qt.UserRole:
                return str(self._data.columns[index.column()])
            
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignCenter
            
        return None
    
    # Cabeçalho da tabela
    def headerData(self, index: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[index]
        
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[index]
        
        return QtCore.QAbstractTableModel.headerData(self, index, orientation, role)


# Função que permite extrair os itens selecionados pelo o usuário
def get_selection(table_view: QtWidgets.QTableView, model=None):
    
    selection = table_view.selectedIndexes()
    
    if selection:

        table = {}

        if model is None:

            for index in selection:

                value = index.data(QtCore.Qt.DisplayRole)
                label = index.data(QtCore.Qt.UserRole)

                if label not in table.keys():
                    table[label] = []

                table[label].append(value)

            table = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in table.items()]))

            return table

        else:
            data_table = model.get_data()

            for index in selection:

                value = data_table.iloc[index.row(), index.column()]
                label = index.data(QtCore.Qt.UserRole)

                if label not in table.keys():
                    table[label] = []

                table[label].append(value)

            table = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in table.items()]))

            return table

    else:
        return pd.DataFrame()
      

def to_clipboard(table_view: QtWidgets.QTableView):
    
    try:
        df = get_selection(table_view)
        df.to_clipboard(index=False)
    
    except AttributeError:
        pd.DataFrame().to_clipboard(index=False)


# Opções da tabela
def set_table_options(table: QtWidgets.QTableView, model: PandasModel):
    
    # Definindo os dados
    table.setModel(model)
    
    # Visual
    cbutton = table.findChild(QtWidgets.QAbstractButton)
    
    hheader = table.horizontalHeader()
    vheader = table.verticalHeader()
    
    cbutton.setStyleSheet(
            "QAbstractButton{"
            "border: none;"
            "background: white;"
            "}"
    )
    
    hheader.setStyleSheet(
            "QHeaderView::section{"
            "border-top:1px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding:4px;"
            "}"
            "QHeaderView{background-color:white;}")
    
    vheader.setStyleSheet(
            "QHeaderView::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:1px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding:4px;"
            "}"
            "QHeaderView{background-color:white;}")

    class TableEventFilter(QtCore.QObject):
        def __init__(self, parent):
            super().__init__(parent)
    
        # Filtro de eventos
        def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        
            # CTRL+C (copiar)
            if event == QtGui.QKeySequence.Copy:
                to_clipboard(table)
                return True
            
            return super().eventFilter(source, event)
        
    table.installEventFilter(TableEventFilter(table.parent()))


# Classe Principal
class TableWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Janela
        self.ui = uic.loadUi(path + '\\UI\\tabela.ui')
        self.ui.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.ui.setWindowIcon(QtGui.QIcon(icon_path + 'database.png'))
        
        self.ui.table_explorer_button.clicked.connect(self.open_explorer)

        self.ui.table_filename.setText(user_path + '\\consulta.csv')
        
        self.model = None
        self.graph = None
        self.splitter = None

        self.ui.open_graphics.triggered.connect(self.open_graphic_options)
        
        self.ui.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableView.customContextMenuRequested.connect(self.context_menu)
        
    # Define os dados a serem mostrados
    def set_data(self, data=pd.DataFrame()):
        self.model = PandasModel(data)
        set_table_options(self.ui.tableView, self.model)
    
    # Menu de contexto
    def context_menu(self, position):
        menu = QtWidgets.QMenu()
        
        save_table = menu.addAction('Salvar tabela')
        save_table.setIcon(QtGui.QIcon(icon_path + 'save_table.png'))
        
        save_selection = menu.addAction('Salvar seleção')
        save_selection.setIcon(QtGui.QIcon(icon_path + 'selection_icon.png'))
        
        copy = menu.addAction('Copiar')
        copy.setIcon(QtGui.QIcon(icon_path + 'copy_table.png'))
        
        action = menu.exec(self.ui.tableView.mapToGlobal(position))
        
        if action == save_table:
            try:
                self.model.save(self.ui.table_filename.text())
            except AttributeError:
                pd.DataFrame.to_csv(path_or_buf=self.ui.table_filename.text(), sep=';')
        
        elif action == save_selection:
            self.save_selection()
        
        elif action == copy:
            self.copy()
    
    # Abrir Explorer
    def open_explorer(self):
        
        dlg = QtWidgets.QFileDialog(self)
        dlg.setWindowIcon(QtGui.QIcon(icon_path + 'folder.png'))
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(['Any Files (*)', 'CSV (*.csv)'])
        dlg.selectNameFilter('Any Files (*)')
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.ui.table_filename.setText(filenames[0])
    
    # Salvar itens selecionados pelo usuário
    def save_selection(self):
        table = get_selection(self.ui.tableView)
        table.to_csv(self.ui.table_filename.text(), ';', index=False)
    
    # Copiar
    def copy(self):
        to_clipboard(self.ui.tableView)

    def open_graphic_options(self):
        
        table = get_selection(self.ui.tableView, self.model)
        
        if table.empty:
            
            warn = QtWidgets.QMessageBox(self)
            warn.setWindowTitle('Gráfico')
            warn.setText('Dados Vazios!')
            warn.setIcon(warn.Information)
            warn.setInformativeText('Selecione os dados de interesse e depois abra a janela de opções!')
            warn.setStandardButtons(warn.Ok | warn.Cancel)
            warn.show()
            
        else:
        
            self.graph = graphics.Graphics(table)
            self.graph.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.set_plot)
            self.graph.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.set_plot)
            self.graph.ui_show()
            
    def allow_menubar(self, allow: bool):
        self.ui.menu.setEnabled(allow)
        
    def clear_plot(self):
        if self.ui.findChild(QtWidgets.QSplitter) is not None:
            self.splitter.deleteLater()
            self.ui.grid.addWidget(self.ui.table_widget)
        
    def set_plot(self):
        self.graph.set_plot()

        self.clear_plot()
            
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.splitter.addWidget(self.ui.table_widget)
        self.splitter.addWidget(self.graph.plot_widget)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([500, 150])
        self.splitter.setStyleSheet("QSplitter::handle{"
                                    "background-color: white;"
                                    "border: 1px solid #D8D8D8;"
                                    "}")
        
        self.ui.grid.addWidget(self.splitter)
    
    # Mostrar janela principal
    def ui_show(self):
        self.ui.show()
