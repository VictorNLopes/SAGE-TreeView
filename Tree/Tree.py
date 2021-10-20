"""

Módulo Tree

		Define os principais elementos para a construção da treeview

"""

# Bibliotecas
import sys
import os
import pandas as pd
import pandas.io.sql as sqlio
from itertools import islice
from PyQt5 import QtWidgets, QtCore, QtGui
from psycopg2 import OperationalError, InterfaceError
from sshtunnel import BaseSSHTunnelForwarderError

# Possíveis erros de consulta SQL
errors = (sqlio.DatabaseError, OperationalError, BaseSSHTunnelForwarderError, ValueError, IndexError, EOFError)


# Classe que define cada item do treeview
class TreeNode:
	def __init__(self, entity=None, identifier=None, bh_mrid=None, index=None, bh_chave=None, has_expanded='n', connection=None):
		
		self.entity = entity
		self.identifier = identifier
		self.bh_mrid = bh_mrid
		self.index = index
		self.bh_chave = bh_chave
		self.has_expanded = has_expanded
		self.connection = connection
	
	# Retorna os nódulos de um item qualquer
	@property
	def nodes(self):
		
		g = pd.DataFrame([])
		
		try:
		
			if (self.bh_mrid is None) and (self.identifier is not None):
				g = sqlio.read_sql_query("select * from relacionamentos_mrid where pai=filho", self.connection)
			
			else:
				g = sqlio.read_sql_query("select * from relacionamentos_mrid where pai=%(bh_mrid)s", self.connection, params={'bh_mrid': self.bh_mrid})
				
		except errors:
			pass
		
		if g.empty:
			return
		
		for node in g['filho']:
			
			if node == self.bh_mrid:
				pass
			else:
				
				try:
					c = sqlio.read_sql_query("select * from chaves where bh_mrid=%(node)s", self.connection, params={'node': node})
				except errors:
					pass
				
				try:
					yield TreeNode(c['entidade'][0], c['identificador'][0], c['bh_mrid'][0], c['indice'][0], c['bh_chave'][0], connection=self.connection)
				except UnboundLocalError:
					pass
	
	# Anda por todos os itens
	# Não Implementada
	def _traverse(self, tree=None):
		
		if tree is None:
			tree = self
		
		if not tree.has_nodes:
			return
		
		for node in tree.nodes:
			self._traverse(node)
	
	# Função que identifica se há nódulos no item
	@property
	def has_nodes(self):
		
		try:
			next(self.nodes)
		except StopIteration:
			return False
		
		return True
	
	# Função que retorna um nódulo em com índice = index
	def node(self, index=0):
		try:
			return next(islice(self.nodes, index, None))
		except StopIteration:
			return
	
	# Utilitários
	def __str__(self):
		return str(self.identifier)
	
	def __repr__(self):
		return repr(self.identifier)
	
	def __getattr__(self, item):
		return item
	
	def __setattr__(self, key, value):
		super().__setattr__(key, value)


# Função que adiciona um nódulo a um item
def add_node(parent: (QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidget), child: TreeNode):
	node = QtWidgets.QTreeWidgetItem(parent, [str(child)])
	
	text = node.font(0)
	text.setPointSize(11)
	node.setFont(0, text)
	
	node.setData(0, QtCore.Qt.UserRole, child.entity)
	node.setData(0, QtCore.Qt.UserRole + 1, child.identifier)
	node.setData(0, QtCore.Qt.UserRole + 2, child.bh_mrid)
	node.setData(0, QtCore.Qt.UserRole + 3, child.index)
	node.setData(0, QtCore.Qt.UserRole + 4, child.bh_chave)
	
	if child.has_nodes:
		node.setChildIndicatorPolicy(node.ShowIndicator)
		node.setData(0, QtCore.Qt.UserRole + 5, child.has_expanded)
	
	set_tree_icon(node)
	return node


# Função que extrai os dados constituintes de um item
def get_info(item: QtWidgets.QTreeWidgetItem):
	
	entity = item.data(0, QtCore.Qt.UserRole)
	identifier = item.data(0, QtCore.Qt.UserRole + 1)
	bh_mrid = item.data(0, QtCore.Qt.UserRole + 2)
	index = item.data(0, QtCore.Qt.UserRole + 3)
	bh_chave = item.data(0, QtCore.Qt.UserRole + 4)
	has_expanded = item.data(0, QtCore.Qt.UserRole + 5)
	
	data = {'entity': entity, 'identifier': identifier, 'bh_mrid': bh_mrid, 'index': index, 'bh_chave': bh_chave,
					'has_expanded': has_expanded}

	return data


# Função que configura os ícones
def set_tree_icon(item: QtWidgets.QTreeWidgetItem):
	icon = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\Icon\\'
	
	entity = item.data(0, QtCore.Qt.UserRole).strip()
	icon += entity + '.png'

	item.setIcon(0, QtGui.QIcon(icon))


# Função que adiciona todos os nódulos existentes de um item
def add_nodes(item: QtWidgets.QTreeWidgetItem, conn=None):
	data = get_info(item)
	
	item.setData(0, QtCore.Qt.UserRole + 5, 'y')
	
	if data['has_expanded'] == 'n':
		
		try:
			
			tr = TreeNode(data['entity'], data['identifier'], data['bh_mrid'], data['index'], data['bh_chave'], connection=conn)
			
			for node in sorted(tr.nodes, key=lambda x: str(x)):
				add_node(item, node)
				
		except InterfaceError:
			pass
	
	else:
		pass
