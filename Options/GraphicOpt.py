import sys
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import PyQt5.uic as uic
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

path = os.path.dirname(os.path.abspath(sys.argv[0]))
icon_path = path + '\\Icon\\'
user_path = os.getenv('userprofile')

mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams["figure.autolayout"] = True


class CheckableComboBox(QtWidgets.QComboBox):
	# Subclass Delegate to increase item height
	class Delegate(QtWidgets.QStyledItemDelegate):
		def sizeHint(self, option, index):
			size = super().sizeHint(option, index)
			size.setHeight(20)
			return size
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Make the combo editable to set a custom text, but readonly
		self.setEditable(True)
		self.lineEdit().setReadOnly(True)
		# Make the lineedit the same color as QPushButton
		palette = self.palette()
		palette.setBrush(QtGui.QPalette.Base, palette.button())
		self.lineEdit().setPalette(palette)
		
		# Use custom delegate
		self.setItemDelegate(CheckableComboBox.Delegate())
		
		# Update the text when an item is toggled
		self.model().dataChanged.connect(self.updateText)
		
		# Hide and show popup when clicking the line edit
		self.lineEdit().installEventFilter(self)
		self.closeOnLineEditClick = False
		
		# Prevent popup from closing when clicking on an item
		self.view().viewport().installEventFilter(self)
	
	def resizeEvent(self, event):
		# Recompute text to elide as needed
		self.updateText()
		super().resizeEvent(event)
	
	def eventFilter(self, object, event):
		
		if object == self.lineEdit():
			if event.type() == QtCore.QEvent.MouseButtonRelease:
				if self.closeOnLineEditClick:
					self.hidePopup()
				else:
					self.showPopup()
				return True
			return False
		
		if object == self.view().viewport():
			if event.type() == QtCore.QEvent.MouseButtonRelease:
				index = self.view().indexAt(event.pos())
				item = self.model().item(index.row())
				
				if item.checkState() == QtCore.Qt.Checked:
					item.setCheckState(QtCore.Qt.Unchecked)
				else:
					item.setCheckState(QtCore.Qt.Checked)
				return True
		return False
	
	def showPopup(self):
		super().showPopup()
		# When the popup is displayed, a click on the lineedit should close it
		self.closeOnLineEditClick = True
	
	def hidePopup(self):
		super().hidePopup()
		# Used to prevent immediate reopening when clicking on the lineEdit
		self.startTimer(100)
		# Refresh the display text when closing
		self.updateText()
	
	def timerEvent(self, event):
		# After timeout, kill timer, and reenable click on line edit
		self.killTimer(event.timerId())
		self.closeOnLineEditClick = False
	
	def updateText(self):
		texts = []
		for i in range(self.model().rowCount()):
			if self.model().item(i).checkState() == QtCore.Qt.Checked:
				texts.append(self.model().item(i).text())
		text = ", ".join(texts)
		
		# Compute elided text (with "...")
		metrics = QtGui.QFontMetrics(self.lineEdit().font())
		elidedText = metrics.elidedText(text, QtCore.Qt.ElideRight, self.lineEdit().width())
		self.lineEdit().setText(elidedText)
	
	def addItem(self, text, data=None):
		item = QtGui.QStandardItem()
		item.setText(text)
		if data is None:
			item.setData(text)
		else:
			item.setData(data)
		item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
		item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
		self.model().appendRow(item)
	
	def addItems(self, texts, datalist=None):
		for i, text in enumerate(texts):
			try:
				data = datalist[i]
			except (TypeError, IndexError):
				data = None
			self.addItem(text, data)
	
	def currentData(self, role: int = ...):
		# Return the list of selected items data
		res = []
		for i in range(self.model().rowCount()):
			if self.model().item(i).checkState() == QtCore.Qt.Checked:
				res.append(self.model().item(i).data())
		return res


class Graphics(QtWidgets.QWidget):
	
	def __init__(self, table: pd.DataFrame):
		super().__init__()
		
		self.table = table
		self.labels = self.table.columns
		
		self.plot_widget = None
		
		self.fig = Figure(figsize=(16, 9), dpi=100, tight_layout=True)
		self.canvas = FigureCanvas(self.fig)
		self.toolbar = NavigationToolbar(self.canvas, None)
		self.ax = None
		
		self.ui = uic.loadUi(path + '\\UI\\graphic_options.ui')
		self.ui.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
		self.ui.setWindowIcon(QtGui.QIcon(icon_path + 'options.png'))
		
		self.ui.xdata.addItems(self.labels)
		
		self.ui.xdata.setCurrentIndex(0)
		
		self.combo = CheckableComboBox()
		
		self.combo.addItems(self.labels)
		
		self.combo.setCurrentIndex(1)
		
		self.ui.options_widget.addRow('Ordenada:', self.combo)
	
	def set_plot(self):
		
		xlabel = self.ui.xdata.currentText()
		ylabel = self.combo.currentText().split(', ')

		xdata = self.table[xlabel]
		
		ydata = []
		
		for item in ylabel:
			ydata.append(self.table[item])
		
		ydata = pd.concat(ydata, axis=1)
		
		self.ax = self.fig.add_subplot(111)
		
		try:
		
			self.ax.plot(xdata, ydata, label=ylabel)
			
			leg = self.ax.legend([f'${k}$' for k in ylabel], fontsize=14, loc='upper left')
			leg.set_draggable(True, use_blit=True)
			
			max_yvalue = ydata.max().max()
			min_yvalue = ydata.min().min()
			
			self.ax.set_xlim(xdata.min(), xdata.max())
			self.ax.set_ylim(min_yvalue, max_yvalue)
			
			self.ax.spines['right'].set_visible(False)
			self.ax.spines['top'].set_visible(False)
			
			def fmt(x, _):
				return fr'${round(x, 3)}$'
			
			self.ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt))
			
			if xlabel == 'tempo':
				
				self.ax.xaxis.set_major_formatter(dates.DateFormatter('${%Y-%m-%d}$' + '\n' + '${%H:%M:%S}$'))
				
				self.ax.xaxis.set_major_locator(dates.AutoDateLocator())
				
			else:
				
				self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt))
			
			self.ax.tick_params(labelsize='large')
			
			self.plot_widget = QtWidgets.QWidget(self)
			layout_mpl = QtWidgets.QGridLayout(self.plot_widget)
			
			layout_mpl.addWidget(self.canvas)
			layout_mpl.addWidget(self.toolbar)
			
		except (ValueError, TypeError):
			warn = QtWidgets.QMessageBox(self)
			warn.setWindowTitle('Gráfico')
			warn.setText('Dados não-numéricos!')
			warn.setInformativeText('Se certifique de que os dados inseridos são númericos e/ou data-hora para o eixo horizontal')
			warn.setIcon(warn.Information)
			warn.setStandardButtons(warn.Ok | warn.Cancel)
			warn.show()
	
	def ui_show(self):
		self.ui.show()
