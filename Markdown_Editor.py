import sys, os, re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QSplitter, QWidget, QVBoxLayout, QGridLayout, 
    QToolBar, QAction, QFileDialog, QMessageBox, QComboBox, QDialog, QFormLayout, 
    QLabel, QLineEdit, QPushButton, QDialogButtonBox, QTabWidget,QTreeView, QFileSystemModel
)
import datetime
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QFontMetrics, QTextCharFormat, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown2
from markdown2 import Markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.formatters import HtmlFormatter
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTextCodec


class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_file = None
        
    def initUI(self):
        self.setWindowTitle('Markdown Editor')
        self.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\MEico.png"))
        self.setStyleSheet("""

background:white;

""")
        
        widget = QWidget()
        self.setCentralWidget(widget)
        
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()

        self.copy_path_button = QPushButton(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\copy.png"),"")
        self.copy_path_button.clicked.connect(self.copy_file_path)
        self.copy_path_button.setToolTip("Copy File Path")
        self.copy_path_button.setVisible(False)
        self.copy_path_button.setIconSize(QSize(20, 20))
        self.copy_path_button.setStyleSheet("""
        QPushButton {
        background:#f2f2f2;
        border-radius:9px;
        padding:3px;}
                                         QPushButton:hover {
                                         background:#e5e5e5;
                                         }
        """)

        # Save and close button
        self.close_save_button = QPushButton(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\saveclose.png"),"")
        self.close_save_button.clicked.connect(self.save_and_close)
        self.close_save_button.setToolTip("Save and Close")
        self.close_save_button.setVisible(False)
        self.close_save_button.setIconSize(QSize(20, 20))
        self.close_save_button.setStyleSheet("""
        QPushButton {
        background:#f2f2f2;
        border-radius:9px;
        padding:3px;}
                                         QPushButton:hover {
                                         background:#e5e5e5;
                                         }
        """)

        self.file_label = QLabel("•••")
        self.file_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # Minimum height
        self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                      padding:3px;
font-size:17px;
""")
        l_h = 30
        self.file_label.setMinimumHeight(l_h)

        header_layout.addWidget(self.file_label)

        self.sep_label = QLabel("|")
        self.sep_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        self.sep_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # Minimum height
        self.sep_label.setStyleSheet("""
background:white;
                                     color:#a5a5a5;
                                     font-size:17px;
""")
        self.sep_label.setMinimumWidth(10)
        self.sep_label.setMaximumWidth(10)

        header_layout.addWidget(self.copy_path_button)
        header_layout.addWidget(self.close_save_button)

        header_layout.addWidget(self.sep_label)

        toggle_mode_button = QPushButton(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\togglemode.png"), '', self)
        toggle_mode_button.setToolTip("Toggle live preview between light and dark mode")  # Set tooltip
        toggle_mode_button.setShortcut("Ctrl+D")  # Set shortcut (optional for QPushButton)
        toggle_mode_button.setIconSize(QSize(25, 25))
        toggle_mode_button.setFixedSize(30, 30)
        toggle_mode_button.clicked.connect(self.toggle_mode) 
        header_layout.addWidget(toggle_mode_button)
        toggle_mode_button.setStyleSheet("""
                                         QPushButton {
        background:#f2f2f2;
        border-radius:8px;}
                                         QPushButton:hover {
                                         background:#e5e5e5;
                                         }
""")
        self.is_dark_mode = False

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("""
QSplitter{
                                    }
QSplitter::handle:vertical {
    background-color: #ccc;
                               border-radius:2px;
    height: 2px;
}
QSplitter::handle:horizontal {
    background-color: #ccc;
                               border-radius:2px;
    height: 2px;
}

""")
        self.splitter.setOpaqueResize(True)

        self.file_system_model = QFileSystemModel()
    
        # Set the root path to the user's home directory, which includes Desktop, Documents, etc.
        self.file_system_model.setRootPath(QDir.homePath())

        # Desktop, Home, and Quick View (add specific paths)
        home_dir = QDir.homePath()  # User home directory
        desktop_dir = os.path.join(home_dir, 'Desktop')  # Desktop directory
        documents_dir = os.path.join(home_dir, 'Documents')

        # Create the tree view to show file system
        self.tree_view = QTreeView()
        self.tree_view.setAnimated(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.homePath()))  # Start from user's home directory
        self.tree_view.hide()
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.clicked.connect(self.open_file_from_tree)
        self.tree_view.setStyleSheet("""
QTreeView {
                border-radius: 10px;
            }
            QTreeView::item:selected {
                background-color: #f2f2f2;
                border:1px solid royalblue;
                color: black;
                border-radius:6px;
                font-weight:bold;
            }
            QTreeView::item {
            border-radius:6px;
                                    margin:2px;
                                    padding:2px;
            }
                                    QTreeView::item:hover {
            border-radius:6px;
            background:#e5e5e5;
            border:1px solid royalblue;
                                    margin:2px;
                                    padding:2px;
                                      color:black;
            }
                                     QScrollBar:vertical {
            background: #e3e5e9;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #b0b0b0;
            min-height: 10px;
                                     min-width:10px;
            border-radius: 6px;
        }
        QScrollBar::add-line:vertical {
            background: #e3e5e9;
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
            background: #e3e5e9;
            height: 0px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar:horizontal {
            background: #e3e5e9;
            height: 9px;
        }
        QScrollBar::handle:horizontal {
            background: #b0b0b0;
            min-width: 15px;
            border-radius: 4px;
        }
        QScrollBar::add-line:horizontal {
            background: #e3e5e9;
            width: 0px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:horizontal {
            background: #e3e5e9;
            width: 0px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }
""")

        # Add the tree view to the splitter
        self.splitter.addWidget(self.tree_view)
        
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptDrops(True)
        self.text_edit.setPlaceholderText("Enter your Markdown here...")
        self.text_edit.textChanged.connect(self.update_preview)
        self.text_edit.setUndoRedoEnabled(True)
        self.text_edit.setStyleSheet("""
                                     QTextEdit {
                                     border:2px solid white;
padding:3px;
background:white;
                                     font-size:17px;
                                     }
                                     QTextEdit:focus {
                                                                          border:2px solid;
border-color: qlineargradient(spread:reflect, x1:0.203, y1:0, x2:1, y2:0, stop:0 rgba(241, 140, 208, 255), stop:0.168539 rgba(0, 164, 255, 255), stop:0.573034 rgba(157, 0, 255, 255), stop:1 rgba(0, 3, 255, 255));;}
                                     
""")

        self.text_edit.dragEnterEvent = self.dragEnterEvent
        self.text_edit.dragMoveEvent = self.dragMoveEvent
        self.text_edit.dropEvent = self.dropEvent
        self.text_edit.textChanged.connect(self.update_status_info)
        self.text_edit.cursorPositionChanged.connect(self.update_cursor_position)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
background:#f2f2f2;
                                      height:25px;
""")
        self.word_count_label = QLabel("Word count: 0")
        self.word_count_label.setStyleSheet("""font-size: 12px;
        margin:4px;
        color:#313131;""")
        self.line_count_label = QLabel("Lines: 0")
        self.line_count_label.setStyleSheet("""font-size: 12px;
        margin:4px;
        color:#313131;""")
        self.column_count_label = QLabel("Columns: 0")
        self.column_count_label.setStyleSheet("""font-size: 12px;
        margin:4px;
        color:#313131;""")
        self.space_count_label = QLabel("Spaces: 0")
        self.space_count_label.setStyleSheet("""font-size: 12px;
        margin:4px;
        color:#313131;""")
        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setStyleSheet("""font-size: 12px;
        margin:4px;
        color:#313131;""")

        self.status_bar.addPermanentWidget(self.encoding_label)
        self.status_bar.addPermanentWidget(self.word_count_label)
        self.status_bar.addPermanentWidget(self.line_count_label)
        self.status_bar.addPermanentWidget(self.column_count_label)
        self.status_bar.addPermanentWidget(self.space_count_label)
        self.setStatusBar(self.status_bar)
        
        self.preview_browser = QWebEngineView()
        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.preview_browser)
        self.splitter.setSizes([200, 500, 500])
        
        layout.addLayout(header_layout)
        layout.addWidget(self.splitter)
        widget.setLayout(layout)
        
        self.file_toolbar = QToolBar("File Toolbar")
        self.addToolBar(Qt.LeftToolBarArea ,self.file_toolbar)
        self.file_toolbar.setMovable(False)   
        
        toggle_treeview_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\filedd.png"),"File Tree", self)
        toggle_treeview_action.triggered.connect(self.toggle_tree_view)
        toggle_treeview_action.setToolTip("File tree")
        self.file_toolbar.addAction(toggle_treeview_action)

        open_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\open.png"),"Open", self)
        open_action.triggered.connect(self.open_file)
        open_action.setToolTip("Open a document")  # Set tooltip
        open_action.setShortcut("Ctrl+O")  # Set shortcut
        self.file_toolbar.addAction(open_action)
        
        save_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\save.png"),"Save", self)
        save_action.triggered.connect(self.save_file)
        save_action.setToolTip("Save the current document")  # Set tooltip
        save_action.setShortcut("Ctrl+S")  # Set shortcut
        self.file_toolbar.addAction(save_action)

        save_as_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\saveas.png"),"Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        save_as_action.setToolTip("Save the current document with new name")  # Set tooltip
        save_as_action.setShortcut("Ctrl+Shift+S")  # Set shortcut
        self.file_toolbar.addAction(save_as_action)

        save_pdf_action = QAction("Save Preview As PDF", self)
        save_pdf_action.setIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\prepdf.png"))  # Optional icon
        save_pdf_action.setToolTip("Save the preview as pdf")
        save_pdf_action.triggered.connect(self.save_as_pdf)

        new_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\newwin.png"),"New Window", self)
        new_action.triggered.connect(self.new)
        new_action.setToolTip("New window")
        self.file_toolbar.addAction(new_action)
        self.file_toolbar.addAction(save_pdf_action)

        self.file_toolbar.addSeparator()

        cut_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\cut.png"),'Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.setToolTip("Cut the text from the editor")
        cut_action.triggered.connect(self.text_edit.cut)
        self.file_toolbar.addAction(cut_action)

        copy_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\copy.png"),'Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.setToolTip("Copy the text from the editor")
        copy_action.triggered.connect(self.text_edit.copy)
        self.file_toolbar.addAction(copy_action)

        paste_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\paste.png"),'Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.setToolTip("Paste the text from clipboard") # Set shortcut
        paste_action.triggered.connect(self.text_edit.paste)
        self.file_toolbar.addAction(paste_action)

        selectall_action = QAction(QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\selectall.png"), "Select All", self)
        selectall_action.setShortcut("Ctrl+Y")  # Set shortcut
        selectall_action.setToolTip("Select all text in the editor")
        selectall_action.triggered.connect(self.text_edit.selectAll)
        self.file_toolbar.addAction(selectall_action)

        clear_action = QAction(QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\clear.png"), "Clear", self)
        clear_action.setShortcut("Ctrl+Y")  # Set shortcut
        clear_action.setToolTip("Clear all text from the editor")
        clear_action.triggered.connect(self.text_edit.clear)
        self.file_toolbar.addAction(clear_action)

        undo_action = QAction(QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\undo.png"), "Undo", self)
        undo_action.setShortcut("Ctrl+Z")  # Set shortcut
        undo_action.setToolTip("Undo the last action")
        undo_action.triggered.connect(lambda: self.text_edit.undo())
        self.file_toolbar.addAction(undo_action)
        
        # Add 'Redo' action
        redo_action = QAction(QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\redo.png"), "Redo", self)
        redo_action.setShortcut("Ctrl+Y")  # Set shortcut
        redo_action.setToolTip("Redo the last undone action")
        redo_action.triggered.connect(lambda: self.text_edit.redo())
        self.file_toolbar.addAction(redo_action)

        toggle_mode_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\togglemode.png"),'Toggle Mode', self)
        toggle_mode_action.triggered.connect(self.toggle_mode)
        toggle_mode_action.setToolTip("Toggle live preview between light and dark mode")  # Set tooltip
        toggle_mode_action.setShortcut("Ctrl+D")
        self.is_dark_mode = False

        self.file_toolbar.layout().setSpacing(5)  # Sets spacing between items
        self.file_toolbar.layout().setContentsMargins(5, 5, 5, 5)

        self.file_toolbar.setStyleSheet("""
    QToolBar {
        background-color: #f2f2f2;
                                        border:none;
    }
    
    QToolButton {
        background-color: #f2f2f2;
        border: none;
        padding: 5px;
                                        border-radius:7px;
    }

    QToolButton:hover {
        background-color: #d8d8d8;
    }
""")
        
        self.format_toolbar = QToolBar("Format Toolbar")
        self.addToolBar(Qt.TopToolBarArea, self.format_toolbar)
        self.format_toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.format_toolbar.setMovable(False)
        self.format_toolbar.setIconSize(QSize(22, 22))
        self.format_toolbar.layout().setSpacing(8)  
        self.format_toolbar.layout().setContentsMargins(5, 5, 5, 5)

        self.format_toolbar.setStyleSheet("""
    QToolBar {
        background-color: #f2f2f2;
                                        border:none;
    }
    
    QToolButton {
        background-color: #f2f2f2;
        border: none;
        padding: 2px;
                                        border-radius:9px;
    }

    QToolButton:hover {
        background-color: #d8d8d8;
    }
""")

        bold_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\bold.png"),"Bold", self)
        bold_action.triggered.connect(self.make_bold)
        bold_action.setToolTip("Bold the text")  # Set tooltip
        bold_action.setShortcut("Ctrl+B")  # Set shortcut
        self.format_toolbar.addAction(bold_action)
        
        italic_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\itallic.png"),"Italic", self)
        italic_action.triggered.connect(self.make_italic)
        italic_action.setToolTip("Italic the text")  # Set tooltip
        italic_action.setShortcut("Ctrl+I")  # Set shortcut
        self.format_toolbar.addAction(italic_action)
        
        bold_italic_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\bolditallic.png"),"Bold Italic", self)
        bold_italic_action.triggered.connect(self.make_bold_italic)
        bold_italic_action.setToolTip("Bold and italic the text")  # Set tooltip
        bold_italic_action.setShortcut("Ctrl+Shift+B")  # Set shortcut
        self.format_toolbar.addAction(bold_italic_action)
        
        strikethrough_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\strickout.png"),"Strikethrough", self)
        strikethrough_action.triggered.connect(self.make_strikethrough)
        strikethrough_action.setToolTip("Strickout the text")  # Set tooltip
        strikethrough_action.setShortcut("Ctrl+Alt+S")  # Set shortcut
        self.format_toolbar.addAction(strikethrough_action)

        highlight_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\highlight.png"),"Highlight", self)
        highlight_action.triggered.connect(self.highlight_text)
        highlight_action.setToolTip("Highlight selected text")
        self.format_toolbar.addAction(highlight_action)

        subscript_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\subscript.png"),"Subscript", self)
        subscript_action.triggered.connect(self.make_subscript)
        subscript_action.setToolTip("Subscript selected text")
        self.format_toolbar.addAction(subscript_action)

        superscript_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\superscript.png"),"Superscript", self)
        superscript_action.triggered.connect(self.make_superscript)
        superscript_action.setToolTip("Superscript selected text")
        self.format_toolbar.addAction(superscript_action)

        header_combo = QComboBox()
        header_combo.setFixedHeight(25)
        header_combo.addItems(["Add Header", "Header 1", "Header 2", "Header 3", "Header 4", "Header 5", "Header 6"])
        header_combo.setToolTip("Add header (h1,h2,h3,h4,h5,h6)")
        header_combo.currentIndexChanged.connect(self.apply_header)
        header_combo.setStyleSheet("""
QComboBox {
margin-left: 5px;
margin-right: 5px;
                font-size: 15px;
                background-color: white;
                selection-background-color: #e0e0e0;
                selection-color: black;
                padding: 6px;
                border-radius:7px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                background:#ccc;
                border-top-right-radius:7px;
                border-bottom-right-radius:7px;
                image: url(C:/Users/rishi/OneDrive/Documents/ME_Icons/dda.png);
                background-size: 4px;
                background-repeat: no-repeat;
                background-position: right 10px center;
            }
                                   QComboBox QAbstractItemView {
        background: white;
        selection-background-color: lightgrey;
        selection-color: black;
        border: 1px solid darkgray;
        border-radius: 7px;
    }
    QComboBox QAbstractItemView::item {
    font-size:10px;
        border-radius: 7px;
        color: black;
    }
    QComboBox QAbstractItemView::item:selected {
        background: lightgrey;
        color: black;
    }
            QComboBox:hover {
margin-left: 5px;
margin-right: 5px;
                background-color: #FFFFFF;
                selection-background-color: #820F41;
                selection-color: white;
            }
""")
        self.format_toolbar.addWidget(header_combo)

        checklist_combo = QComboBox()
        checklist_combo.setFixedHeight(25)
        checklist_combo.addItems(["Add Checklist", "Unchecked Checklist", "Checked Checklist"])
        checklist_combo.setToolTip("Add checklist")
        checklist_combo.currentIndexChanged.connect(self.apply_checklist)
        checklist_combo.setStyleSheet("""
QComboBox {
margin-left: 5px;
margin-right: 5px;
                font-size: 15px;
                background-color: white;
                selection-background-color: #e0e0e0;
                selection-color: black;
                padding: 6px;
                border-radius:7px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                background:#ccc;
                border-top-right-radius:7px;
                border-bottom-right-radius:7px;
                image: url(C:/Users/rishi/OneDrive/Documents/ME_Icons/dda.png);
                background-size: 5px;
                background-repeat: no-repeat;
                background-position: right 10px center;
            }
            QComboBox QAbstractItemView {
        background: white;
        selection-background-color: lightgrey;
        selection-color: black;
        border: 1px solid darkgray;
        border-radius: 7px;
    }
    QComboBox QAbstractItemView::item {
    font-size:10px;
        border-radius: 7px;
        color: black;
    }
    QComboBox QAbstractItemView::item:selected {
        background: lightgrey;
        color: black;
    }
            QComboBox:hover {
margin-left: 5px;
margin-right: 5px;
                background-color: #FFFFFF;
                selection-background-color: #820F41;
                selection-color: white;
            }
""")
        self.format_toolbar.addWidget(checklist_combo)
        
        list_combo = QComboBox()
        list_combo.setFixedHeight(25)
        list_combo.addItems(["Add List", "Ordered List", "Unordered List"])
        list_combo.setToolTip("Add list")
        list_combo.currentIndexChanged.connect(self.apply_list)
        list_combo.setStyleSheet("""
QComboBox {
margin-left: 5px;
margin-right: 5px;
                font-size: 15px;
                background-color: white;
                selection-background-color: #e0e0e0;
                selection-color: black;
                padding: 6px;
                border-radius:7px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                background:#ccc;
                border-top-right-radius:7px;
                border-bottom-right-radius:7px;
                image: url(C:/Users/rishi/OneDrive/Documents/ME_Icons/dda.png);
                background-size: 5px;
                background-repeat: no-repeat;
                background-position: right 10px center;
            }
            QComboBox QAbstractItemView {
        background: white;
        selection-background-color: lightgrey;
        selection-color: black;
        border: 1px solid darkgray;
        border-radius: 7px;
    }
    QComboBox QAbstractItemView::item {
    font-size:10px;
        border-radius: 7px;
        color: black;
    }
    QComboBox QAbstractItemView::item:selected {
        background: lightgrey;
        color: black;
    }
            QComboBox:hover {
margin-left: 5px;
margin-right: 5px;
                background-color: #FFFFFF;
                selection-background-color: royalblue;
                selection-color: white;
            }
""")
        self.format_toolbar.addWidget(list_combo)

        self.format_toolbar.addSeparator()

        section_header_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\sectionheader.png"),"Section Header", self)
        section_header_action.triggered.connect(self.show_section_header_dialog)
        section_header_action.setToolTip("Add a section header")
        self.format_toolbar.addAction(section_header_action)
        
        link_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\link.png"),"Add Link", self)
        link_action.triggered.connect(self.show_link_dialog)
        link_action.setToolTip("Add a link")
        self.format_toolbar.addAction(link_action)

        image_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\image.png"),"Insert Image", self)
        image_action.triggered.connect(self.show_image_dialog)
        image_action.setToolTip("Add an image")
        self.format_toolbar.addAction(image_action)

        table_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\table.png"),"Table", self)
        table_action.triggered.connect(self.insert_table_dialog)
        table_action.setToolTip("Insert a table")
        self.format_toolbar.addAction(table_action)

        add_equation_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\equation.png"),"Equations", self)
        add_equation_action.triggered.connect(self.eq_win)
        add_equation_action.setToolTip("Add an equation")  # Set tooltip
        add_equation_action.setShortcut("Ctrl+Shift+E")  # Set shortcut
        self.format_toolbar.addAction(add_equation_action)

        self.format_toolbar.addSeparator()

        comment_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\comment.png"),"Comment", self)
        comment_action.triggered.connect(self.insert_comment)
        comment_action.setToolTip("Comment selected text")
        self.format_toolbar.addAction(comment_action)

        uncomment_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\uncomment.png"),"Uncomment", self)
        uncomment_action.triggered.connect(self.remove_comment)
        uncomment_action.setToolTip("Uncomment selected text")
        self.format_toolbar.addAction(uncomment_action)

        self.addToolBarBreak()

        self.elements_toolbar = QToolBar("Elements Toolbar")
        self.addToolBar(Qt.TopToolBarArea, self.elements_toolbar)
        self.elements_toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.elements_toolbar.setMovable(False)
        self.elements_toolbar.setIconSize(QSize(22, 22))
        self.elements_toolbar.layout().setSpacing(8)  # Sets spacing between items
        self.elements_toolbar.layout().setContentsMargins(5, 5, 5, 5)

        self.elements_toolbar.setStyleSheet("""
    QToolBar {
        background-color: #f2f2f2;
                                        border:none;
    }
    
    QToolButton {
        background-color: #f2f2f2;
        border: none;
        padding: 2px;
                                        border-radius:9px;
    }

    QToolButton:hover {
        background-color: #d8d8d8;
    }
""")
        
        self.admonition_combobox = QComboBox(self)
        self.admonition_combobox.setFixedHeight(25)
        self.admonition_combobox.setToolTip("Add block")
        self.admonition_combobox.setStyleSheet("""
QComboBox {
margin-left: 5px;
margin-right: 5px;
                font-size: 15px;
                background-color: white;
                selection-background-color: #e0e0e0;
                selection-color: black;
                padding: 6px;
                border-radius:7px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                background:#ccc;
                border-top-right-radius:7px;
                border-bottom-right-radius:7px;
                image: url(C:/Users/rishi/OneDrive/Documents/ME_Icons/dda.png);
                background-size: 5px;
                background-repeat: no-repeat;
                background-position: right 10px center;
            }
            QComboBox QAbstractItemView {
        background: white;
        selection-background-color: lightgrey;
        selection-color: black;
        border: 1px solid darkgray;
        border-radius: 7px;
    }
    QComboBox QAbstractItemView::item {
    font-size:10px;
        border-radius: 7px;
        color: black;
    }
    QComboBox QAbstractItemView::item:selected {
        background: lightgrey;
        color: black;
    }
            QComboBox:hover {
margin-left: 5px;
margin-right: 5px;
                background-color: #FFFFFF;
                selection-background-color: royalblue;
                selection-color: white;
            }
""")
        self.admonition_combobox.addItems([
            'Add block', 
            'Quote block', 
            'Inline code block', 
            'Multiline code block',
            'Note block', 
            'Warning block', 
            'Danger block', 
            'Success block', 
            'Info block', 
            'Tip block'
        ])
        
        # Connect the combo box signal
        self.admonition_combobox.currentIndexChanged.connect(self.insert_admonition_from_combobox)

        # Add the combobox to the toolbar
        self.elements_toolbar.addWidget(self.admonition_combobox)

        toc_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\toc.png"), 'Insert Table of Contents', self)
        toc_action.triggered.connect(self.insert_toc)
        toc_action.setToolTip("Insert Table of Contents")
        self.elements_toolbar.addAction(toc_action)

        prog_bar_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\progbar.png"), 'Insert Progressbar', self)
        prog_bar_action.triggered.connect(self.open_progress_bar_dialog)
        prog_bar_action.setToolTip("Insert Progress Bar")
        self.elements_toolbar.addAction(prog_bar_action)

        hr_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\horzline.png"),"Horizontal Line", self)
        hr_action.triggered.connect(self.insert_horizontal_line)
        hr_action.setToolTip("Add a horizontal line")
        self.elements_toolbar.addAction(hr_action)

        footnote_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\footnote.png"),"Footnote", self)
        footnote_action.triggered.connect(self.insert_footnote)
        footnote_action.setToolTip("Add a footnote")
        self.elements_toolbar.addAction(footnote_action)

        toggle_treeview_action.setStatusTip("File tree")
        save_action.setStatusTip("Save the current document")
        save_as_action.setStatusTip("Save the current document with new name")
        save_pdf_action.setStatusTip("Save the preview as pdf")
        open_action.setStatusTip("Open a document")
        cut_action.setStatusTip("Cut the text from the editor")
        copy_action.setStatusTip("Copy the text from the editor")
        paste_action.setStatusTip("Paste the text from clipboard")
        selectall_action.setStatusTip("Select all text in the editor")
        clear_action.setStatusTip("Clear all text from the editor")
        undo_action.setStatusTip("Undo the last action")
        redo_action.setStatusTip("Redo the last undone action")
        toggle_mode_action.setStatusTip("Toggle live preview between light and dark mode")
        bold_action.setStatusTip("Bold the text")
        italic_action.setStatusTip("Italic the text")
        bold_italic_action.setStatusTip("Bold and italic the text")
        strikethrough_action.setStatusTip("Strikethrough the text")
        highlight_action.setStatusTip("Highlight selected text")
        subscript_action.setStatusTip("Subscript selected text")
        superscript_action.setStatusTip("Superscript selected text")
        section_header_action.setStatusTip("Add a section header")
        link_action.setStatusTip("Add a link")
        image_action.setStatusTip("Add an image")
        table_action.setStatusTip("Insert a table")
        add_equation_action.setStatusTip("Add an equation")
        footnote_action.setStatusTip("Add a footnote")
        self.admonition_combobox.setStatusTip("Add block")
        toc_action.setStatusTip("Insert Table of Contents")
        prog_bar_action.setStatusTip("Insert Progress Bar")
        hr_action.setStatusTip("Add a horizontal line")
        comment_action.setStatusTip("Comment selected text")
        uncomment_action.setStatusTip("Uncomment selected text")

        # For QComboBox objects
        header_combo.setStatusTip("Add header (h1,h2,h3,h4,h5,h6)")
        checklist_combo.setStatusTip("Add checklist")
        list_combo.setStatusTip("Add list")

        menubar = self.menuBar()
        menubar.setStyleSheet("""
QMenuBar
{
background-color: royalblue;
width:60px;
padding:4px;
color:white;
font-weight:bold;
}
            QMenuBar::item {
font-size:20px;
alignment: center;
            }
            QMenuBar::item:selected {
            color:white;
                              background:blue  ;
                              border-radius:5px;
                              padding:5px;
            }
            QMenu {
background-color: white;
                              background:white;
                              color:black;
                margin:4px;
                padding:4px;
                        }
            QMenu::item {
                              background:white;
                              color:black;
            }
            QMenu::item:selected {
                background-color: lightgrey;
                color:black;
                border-radius:5px;
            }
            QMenu::separator {
}
""")

        # File Menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction(open_action)
        file_menu.addAction(new_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(save_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(toggle_treeview_action)

        # Edit Menu
        edit_menu = menubar.addMenu('Edit')

        indent_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\indent.png"),"Indent", self)
        dedent_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\dedent.png"),"Dedent", self)

        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(selectall_action)
        edit_menu.addAction(clear_action)
        edit_menu.addSeparator()
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(indent_action)
        edit_menu.addAction(dedent_action)
        edit_menu.addSeparator()
        edit_menu.addAction(comment_action)
        edit_menu.addAction(uncomment_action)

        # Connect actions to their respective slots
        indent_action.triggered.connect(self.indent_text)
        dedent_action.triggered.connect(self.dedent_text)

        selection_menu = QMenu("Selection", self)

        # Actions for the Selection submenu
        jump_to_top_action = QAction("Jump to Top", self)
        jump_to_selection_action = QAction("Jump to Selection", self)
        jump_to_bottom_action = QAction("Jump to Bottom", self)
        jump_to_line_start_action = QAction("Jump to Line Start", self)
        jump_to_line_end_action = QAction("Jump to Line End", self)

        # Add actions to the Selection submenu
        selection_menu.addAction(jump_to_top_action)
        selection_menu.addAction(jump_to_selection_action)
        selection_menu.addAction(jump_to_bottom_action)
        selection_menu.addAction(jump_to_line_start_action)
        selection_menu.addAction(jump_to_line_end_action)

        # Add the Selection submenu to the Edit menu
        edit_menu.addSeparator()
        edit_menu.addMenu(selection_menu)

        # Connect actions to slots
        jump_to_top_action.triggered.connect(self.jump_to_top)
        jump_to_selection_action.triggered.connect(self.jump_to_selection)
        jump_to_bottom_action.triggered.connect(self.jump_to_bottom)
        jump_to_line_start_action.triggered.connect(self.jump_to_line_start)
        jump_to_line_end_action.triggered.connect(self.jump_to_line_end)

        # Format Menu
        format_menu = menubar.addMenu('Format')
        format_menu.addAction(bold_action)
        format_menu.addAction(italic_action)
        format_menu.addAction(bold_italic_action)
        format_menu.addAction(strikethrough_action)
        format_menu.addAction(highlight_action)
        format_menu.addAction(subscript_action)
        format_menu.addAction(superscript_action)

        clear_formatting_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\clearformat.png"),"Clear Formatting", self)
        format_menu.addAction(clear_formatting_action)
        clear_formatting_action.triggered.connect(self.clear_formatting)

        # Elements Menu
        element_menu = menubar.addMenu('Elements')
        header_menu = QMenu("Header", self)
        header_actions = []
        header_names = ["H1", "H2", "H3", "H4", "H5", "H6"]
        for i, name in enumerate(header_names, start=1):
            action = QAction(name, self)
            action.triggered.connect(lambda checked, i=i: self.apply_header(i))  # Connect action to apply_header
            header_menu.addAction(action)
            header_actions.append(action)
        element_menu.addMenu(header_menu)
        list_menu = QMenu("List", self)
        checklist_menu = QMenu("Checklist", self)
        ordered_list_action = QAction("Ordered List", self)
        unordered_list_action = QAction("Unordered List", self)
        ordered_list_action.triggered.connect(lambda: self.apply_list(1))  # Ordered List
        unordered_list_action.triggered.connect(lambda: self.apply_list(2))
        list_menu.addAction(ordered_list_action)
        list_menu.addAction(unordered_list_action)

        # Add sub-menu actions for "Unchecked Checklist" and "Checked Checklist"
        unchecked_checklist_action = QAction("Unchecked Checklist", self)
        checked_checklist_action = QAction("Checked Checklist", self)
        unchecked_checklist_action.triggered.connect(lambda: self.apply_checklist(1))  # Unchecked Checklist
        checked_checklist_action.triggered.connect(lambda: self.apply_checklist(2))  # Checked Checklist
        checklist_menu.addAction(unchecked_checklist_action)
        checklist_menu.addAction(checked_checklist_action)
        element_menu.addMenu(list_menu)
        element_menu.addMenu(checklist_menu)
        element_menu.addAction(section_header_action)
        element_menu.addAction(link_action)
        element_menu.addAction(image_action)
        element_menu.addAction(table_action)
        element_menu.addAction(add_equation_action)
        element_menu.addAction(footnote_action)
        element_menu.addAction(toc_action)
        element_menu.addAction(hr_action)
        element_menu.addSeparator()

        blocks_menu = QMenu("Blocks", self)
        element_menu.addMenu(blocks_menu)

        # Define block types and their corresponding actions
        block_types = {
            'Quote block': self.insert_blockquote,
            'Inline code block': self.make_inline_code,
            'Multiline code block': self.insert_code_block,
            'Note block': lambda: self.insert_admonition_from_menu('note'),
            'Warning block': lambda: self.insert_admonition_from_menu('warning'),
            'Danger block': lambda: self.insert_admonition_from_menu('danger'),
            'Success block': lambda: self.insert_admonition_from_menu('success'),
            'Info block': lambda: self.insert_admonition_from_menu('info'),
            'Tip block': lambda: self.insert_admonition_from_menu('tip'),
        }

        # Create actions for each block type
        for block_name, block_function in block_types.items():
            action = QAction(block_name, self)
            action.triggered.connect(block_function)
            blocks_menu.addAction(action)

        # View Menu
        view_menu = menubar.addMenu('View')

        # Existing Actions
        toggle_format_toolbar_action = QAction("Toggle Format Toolbar", self)
        toggle_format_toolbar_action.setCheckable(True)
        toggle_format_toolbar_action.setChecked(True)
        toggle_format_toolbar_action.triggered.connect(self.toggle_format_toolbar)

        toggle_file_toolbar_action = QAction("Toggle File Toolbar", self)
        toggle_file_toolbar_action.setCheckable(True)
        toggle_file_toolbar_action.setChecked(True)
        toggle_file_toolbar_action.triggered.connect(self.toggle_file_toolbar)

        editor_view_action = QAction("Edit View", self)
        editor_view_action.setCheckable(True)
        editor_view_action.setChecked(False)
        editor_view_action.triggered.connect(self.enable_editor_view)

        preview_view_action = QAction("Full Preview", self)
        preview_view_action.setCheckable(True)
        preview_view_action.setChecked(False)
        preview_view_action.triggered.connect(self.enable_preview_view)

        splitter_orient = QAction("Switch Orientation", self)
        splitter_orient.setCheckable(True)
        splitter_orient.setChecked(False)
        splitter_orient.triggered.connect(self.splitter_or_func)

        clean_mode = QAction("Clean view", self)
        clean_mode.setCheckable(True)
        clean_mode.setChecked(False)
        clean_mode.triggered.connect(self.enable_clean_view)

        # Add actions to the "View" menu
        view_menu.addAction(toggle_format_toolbar_action)
        view_menu.addAction(toggle_file_toolbar_action)
        view_menu.addSeparator()
        view_menu.addAction(editor_view_action)
        view_menu.addAction(preview_view_action)
        view_menu.addAction(clean_mode)
        view_menu.addSeparator()
        view_menu.addAction(splitter_orient)

        # Full Screen Action
        self.fullscreen_action = QAction("Toggle Full Screen", self)
        self.fullscreen_action.setCheckable(True)  # Make it toggleable
        self.fullscreen_action.setChecked(False)   # Initially not checked (normal window)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)

        view_menu.addSeparator()
        view_menu.addAction(self.fullscreen_action)

        # Help Menu
        help_menu = menubar.addMenu('Help')
        
        self.showMaximized()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()  # Exit fullscreen
            self.fullscreen_action.setChecked(False)  # Update action state
        else:
            self.showFullScreen()  # Enter fullscreen
            self.fullscreen_action.setChecked(True)  # Update action state

    def open_main_menu_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Markdown Templates")
        dialog.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout(dialog)

        # Create the tab widget
        tab_widget = QTabWidget(dialog)
        layout.addWidget(tab_widget)

        # Create a scroll area for the button layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        button_widget = QWidget()
        button_layout = QGridLayout(button_widget)

        # Predefined Markdown templates
        templates = [
            ("README.md", 
                "# Project Title\n"
                "## Description\n"
                "A brief description of your project.\n"
                "## Installation\n"
                "Instructions for installing the project.\n"
                "## Usage\n"
                "How to use the project.\n"
                "## Contributing\n"
                "Guidelines for contributing to the project.\n"
                "## License\n"
                "License information."
            ),
            ("To-Do List", 
                "# To-Do List\n"
                "- [ ] Item 1\n"
                "- [ ] Item 2\n"
                "- [ ] Item 3"
            ),
            ("Notes", 
                "# Notes\n"
                "## Important Points\n"
                "- Point 1\n"
                "- Point 2\n"
                "- Point 3"
            ),
            ("Meeting Agenda", 
                "# Meeting Agenda\n"
                "1. Opening\n"
                "2. Discussion Points\n"
                "3. Closing"
            ),
            ("Blog Post", 
                "# Blog Post\n"
                "## Introduction\n"
                "Content goes here...\n"
                "## Conclusion"
            ),
            ("Recipe", 
                "# Recipe\n"
                "## Ingredients\n"
                "- Item 1\n"
                "- Item 2\n"
                "## Instructions\n"
                "1. Step 1\n"
                "2. Step 2"
            ),
            ("User Guide", 
                "# User Guide\n"
                "## Installation\n"
                "Steps to install the software...\n"
                "## Usage"
            ),
            ("Report", 
                "# Report\n"
                "## Summary\n"
                "Brief summary of the findings...\n"
                "## Conclusion"
            ),
            ("Resume", 
                "# Resume\n"
                "## Personal Information\n"
                "- Name\n"
                "- Contact\n"
                "## Experience\n"
                "- Job 1\n"
                "- Job 2"
            ),
            ("FAQ", 
                "# FAQ\n"
                "## Question 1\n"
                "Answer to question 1...\n"
                "## Question 2\n"
                "Answer to question 2..."
            ),
        ]

        # Create buttons for each template in a grid layout
        for i, (template_name, template_text) in enumerate(templates):
            button = QPushButton(template_name)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow buttons to expand
            button.setStyleSheet("""
            QPushButton{
            border-radius:7px;
                                 border:2px solid #ccc;
            }
                                 QPushButton:hover{
                                 border:2px solid royalblue;
                                 }
            """
            )
            button.clicked.connect(lambda _, text=template_text: self.insert_template(text))
            button_layout.addWidget(button, i // 2, i % 2)  # 2 buttons per row

        # Add the button layout to the scroll area
        button_widget.setLayout(button_layout)
        scroll_area.setWidget(button_widget)
        tab_widget.addTab(scroll_area, "Templates")

        dialog.setLayout(layout)
        dialog.show()

    def insert_template(self, template_text):
        cursor = self.text_edit.textCursor()
        cursor.insertText(template_text + "\n")
    def update_status_info(self):
        text = self.text_edit.toPlainText()
        word_count = len(text.split())
        line_count = text.count('\n') + 1  # Adding 1 for the last line
        column_count = len(text.split('\n')[-1])  # Columns in the last line
        space_count = text.count(' ')

        self.word_count_label.setText(f"Word count: {word_count}")
        self.space_count_label.setText(f"Spaces: {space_count}")

    def update_cursor_position(self):
        # Get the cursor object from the text edit
        cursor = self.text_edit.textCursor()
        
        # Get the current line number (block number)
        line_number = cursor.blockNumber() + 1  # Block number starts from 0, so add 1
        
        # Get the column number by calculating the position within the current line
        column_number = cursor.columnNumber()
    
        # Update the status bar labels with the current line and column
        self.line_count_label.setText(f"Line: {line_number}")
        self.column_count_label.setText(f"Column: {column_number}")

    def splitter_or_func(self):
        if self.splitter.orientation() == Qt.Horizontal:
            self.splitter.setOrientation(Qt.Vertical)
        else:
            self.splitter.setOrientation(Qt.Horizontal)
            self.splitter.setSizes([0, 500, 500])

    def clear_formatting(self):
        cursor = self.text_edit.textCursor()

        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # Clear Markdown formatting from selected text
            cleared_text = self.remove_markdown_formatting(selected_text)
            cursor.insertText(cleared_text)

        else:
            # If no selection, apply to the entire text
            full_text = self.text_edit.toPlainText()
            cleared_text = self.remove_markdown_formatting(full_text)
            self.text_edit.setPlainText(cleared_text)

    def remove_markdown_formatting(self, text):
        """Removes Markdown formatting elements from the given text."""
        import re
        # Regex patterns to remove various Markdown elements
        patterns = [
            (r'\*\*([^\*]+)\*\*', r'\1'),     # Bold
            (r'\*([^\*]+)\*', r'\1'),         # Italic
            (r'\~\~(.*?)\~\~', r'\1'),        # Strikethrough
            (r'\`(.*?)\`', r'\1'),            # Inline code
            (r'\[(.*?)\]\((.*?)\)', r'\1'),   # Links
            (r'\!\[(.*?)\]\((.*?)\)', r'\1'), # Images
            (r'\#{1,6}\s*(.*)', r'\1'),       # Headers
            (r'^\*\s+', '', re.MULTILINE),    # Unordered list
            (r'^\d+\.\s+', '', re.MULTILINE), # Ordered list
            (r'^\>\s+', '', re.MULTILINE),    # Blockquote
            (r'\-\s\[.\]\s+', ''),            # Task list
        ]

        # Remove Markdown formatting
        for pattern in patterns:
            if len(pattern) == 2:  # No flags provided
                text = re.sub(pattern[0], pattern[1], text)
            elif len(pattern) == 3:  # Flags provided
                text = re.sub(pattern[0], pattern[1], text, flags=pattern[2])
        
        return text
    
    def insert_toc(self):
        """Inserts [TOC] at the cursor position in the text edit."""
        cursor = self.text_edit.textCursor()
        cursor.insertText("[TOC]\n")

    def insert_table_of_contents(self, markdown_text):
        """Inserts a table of contents (ToC) at the top of the Markdown content."""
        import re

        toc_lines = []
        toc_placeholder = "[TOC]"

        # Find all headers in the markdown text
        headers = re.findall(r'(#+)\s+(.*)', markdown_text)
        for level, header_text in headers:
            header_id = header_text.strip().lower().replace(' ', '-')
            indentation = '    ' * (len(level) - 1)  # Indent based on header level
            toc_lines.append(f'{indentation}- [{header_text}](#{header_id})')

        toc = '\n'.join(toc_lines)

        # Insert ToC in place of the [TOC] tag
        if toc_placeholder in markdown_text:
            markdown_text = markdown_text.replace(toc_placeholder, toc)

        return markdown_text

    def indent_text(self):
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()

        if cursor.hasSelection():
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()

            # Move cursor to the start of the selection and process each line
            cursor.setPosition(selection_start)
            while cursor.position() < selection_end:
                cursor.movePosition(cursor.StartOfLine)
                cursor.insertText("    ")  # Indent with 4 spaces
                cursor.movePosition(cursor.NextBlock)
                selection_end += 4  # Adjust selection end due to added indentation

        # If no selection, indent the current line
        else:
            cursor.movePosition(cursor.StartOfLine)
            cursor.insertText("    ")

        cursor.endEditBlock()
    def dedent_text(self):
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()

        if cursor.hasSelection():
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()

            # Move cursor to the start of the selection and process each line
            cursor.setPosition(selection_start)
            while cursor.position() < selection_end:
                cursor.movePosition(cursor.StartOfLine)
                line = cursor.block().text()

                # Dedent only if the line starts with 4 spaces
                if line.startswith("    "):
                    for _ in range(4):
                        cursor.deleteChar()
                    selection_end -= 4  # Adjust selection end due to removed indentation

                cursor.movePosition(cursor.NextBlock)

        # If no selection, dedent the current line
        else:
            cursor.movePosition(cursor.StartOfLine)
            line = cursor.block().text()

            # Dedent only if the line starts with 4 spaces
            if line.startswith("    "):
                for _ in range(4):
                    cursor.deleteChar()

        cursor.endEditBlock()

    def jump_to_top(self):
        self.text_edit.moveCursor(self.text_edit.textCursor().Start)

    def jump_to_selection(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            self.text_edit.setTextCursor(cursor)
        else:
            QMessageBox.information(self, "Info", "No text selected")

    def jump_to_bottom(self):
        self.text_edit.moveCursor(self.text_edit.textCursor().End)

    def jump_to_line_start(self):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        self.text_edit.setTextCursor(cursor)

    def jump_to_line_end(self):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.EndOfBlock)
        self.text_edit.setTextCursor(cursor)

    def enable_clean_view(self, state):
        if state:
            self.format_toolbar.hide()
            self.file_toolbar.hide()
            self.file_label.hide()
            self.sep_label.hide()
            self.elements_toolbar.hide()
        else:
            self.format_toolbar.show()
            self.file_toolbar.show()
            self.file_label.show()
            self.sep_label.show()
            self.elements_toolbar.show()

    def enable_editor_view(self, state):
        if state:
            self.splitter.setSizes([0, 1000, 0])
        else:
            self.splitter.setSizes([0, 500, 500])

    def enable_preview_view(self, state):
        if state:
            self.splitter.setSizes([0, 0, 1000])
        else:
            self.splitter.setSizes([0, 500, 500])

    def copy_file_path(self):
        if self.current_file:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_file)

    # Function to save and close the current file
    def save_and_close(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())
            self.text_edit.clear()
            self.file_label.setText("•••")
            self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                      padding:3px;
font-size:17px;
""")
            self.current_file = None
            self.copy_path_button.setVisible(False)
            self.close_save_button.setVisible(False)
            self.reset_tree_view()

    def toggle_format_toolbar(self, state):
        if state:
            self.format_toolbar.show()
        else:
            self.format_toolbar.hide()

    def toggle_file_toolbar(self, state):
        if state:
            self.file_toolbar.show()
        else:
            self.file_toolbar.hide()

    def reset_tree_view(self):
        self.tree_view.collapseAll()
        root_path = QDir.rootPath()  # This sets to the root directory ("/" in Linux, "C:/" in Windows)
        root_index = self.file_system_model.index(root_path)
        self.tree_view.setRootIndex(root_index)
        home_path = QDir.homePath()
        home_index = self.file_system_model.index(home_path)
        self.tree_view.setRootIndex(home_index)
        self.tree_view.expand(self.file_system_model.index(QDir.homePath()))

    def show_badge_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Insert Badge")
        layout = QFormLayout(dialog)
        
        self.badge_lhs = QLineEdit()
        self.badge_rhs = QLineEdit()
        self.badge_color = QLineEdit()
        layout.addRow("Left Text:", self.badge_lhs)
        layout.addRow("Right Text:", self.badge_rhs)
        layout.addRow("Color:", self.badge_color)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.add_badge)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.add_badge)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def add_badge(self):
        lhs_text = self.badge_lhs.text()
        rhs_text = self.badge_rhs.text()
        color = self.badge_color.text()
        badge_syntax = f":badge|{lhs_text}|{rhs_text}|{color}:"
        cursor = self.text_edit.textCursor()
        cursor.insertText(badge_syntax)
        self.update_preview()

    def insert_footnote(self):
        cursor = self.text_edit.textCursor()

        # Insert the footnote reference at the cursor position
        footnote_reference = "Add text here"
        cursor.insertText(footnote_reference)

        # Insert the superscript footnote marker
        cursor.insertText(" [^1]")
        
        # Move the cursor to the end of the document to insert the footnote definition
        cursor.movePosition(cursor.End)
        cursor.insertText(f"\n\n[^1]: Add footnote text here.")

        # Apply superscript formatting to [^1]
        cursor.setPosition(cursor.position() - len(f"[^1]"))
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(f"[^1]"))

        format = QTextCharFormat()
        format.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        cursor.setCharFormat(format)

        # Update the preview
        self.update_preview()
        
    def toggle_mode(self):
        if self.is_dark_mode:
            # Light Mode JavaScript
            self.preview_browser.page().runJavaScript("""
                document.documentElement.style.backgroundColor = 'white';
                document.documentElement.style.color = 'black';

                document.querySelectorAll('pre').forEach(function(pre) {
                    pre.style.backgroundColor = '#f5f5f5';
                    pre.style.color = 'black';
                });
                document.querySelectorAll('code').forEach(function(code) {
                    code.style.backgroundColor = '#f5f5f5';
                    code.style.color = 'black';
                });
                document.querySelectorAll('blockquote').forEach(function(blockquote) {
                    blockquote.style.backgroundColor = '#f9f9f9';
                    blockquote.style.color = 'black';
                    blockquote.style.borderLeft = '5px solid #ccc';
                });
                document.querySelectorAll('table').forEach(function(table) {
                    table.style.backgroundColor = 'white';
                    table.style.color = 'black';
                    table.querySelectorAll('th').forEach(function(th) {
                        th.style.backgroundColor = '#f2f2f2';
                    });
                    table.querySelectorAll('tr:nth-child(even)').forEach(function(tr) {
                        tr.style.backgroundColor = '#f2f2f2';
                    });
                });

                // Admonitions in Light Mode
                document.querySelectorAll('.admonition.note').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#e7f3fe'; // Light blue
                    admonition.style.color = 'black';
                    admonition.style.borderLeft = '5px solid #007bff'; // Blue border
                });
                document.querySelectorAll('.admonition.warning').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#fff3cd'; // Light yellow
                    admonition.style.color = 'black';
                    admonition.style.borderLeft = '5px solid #ffa726'; // Orange border
                });
                document.querySelectorAll('.admonition.danger').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#f8d7da'; // Light red
                    admonition.style.color = 'black';
                    admonition.style.borderLeft = '5px solid #dc3545'; // Red border
                });
                document.querySelectorAll('.admonition.success').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#d4edda'; // Light blue
                    admonition.style.color = 'black';
                    admonition.style.borderLeft = '5px solid #28a745'; // Blue border
                });
                document.querySelectorAll('.admonition.info').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#d1ecf1'; // Light yellow
                    admonition.style.color = 'black';
                    admonition.style.borderLeft = '5px solid #17a2b8'; // Orange border
                });
                document.querySelectorAll('.admonition.tip').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#e2e3e5'; // Light red
                    admonition.style.color = 'black';
                    admonition.style.borderLeft = '5px solid #007bff'; // Red border
                });
                document.querySelectorAll('.custom-button').forEach(function(button) {
                    button.style.backgroundColor = '#007bff'; // Light mode button color
                });
                document.querySelectorAll('.highlight').forEach(function(highlight) {
                    highlight.style.backgroundColor = '#f9ff0f'; // Light mode highlight color
                    highlight.style.color = 'black'; // Text color for light mode
                });
            """)
        else:
            # Dark Mode JavaScript
            self.preview_browser.page().runJavaScript("""
                document.documentElement.style.backgroundColor = '#2e2e2e';
                document.documentElement.style.color = 'white';

                document.querySelectorAll('pre').forEach(function(pre) {
                    pre.style.backgroundColor = 'black';
                    pre.style.color = 'white';
                });
                document.querySelectorAll('code').forEach(function(code) {
                    code.style.backgroundColor = 'black';
                    code.style.color = 'white';
                });
                document.querySelectorAll('blockquote').forEach(function(blockquote) {
                    blockquote.style.backgroundColor = '#444';
                    blockquote.style.color = 'white';
                    blockquote.style.borderLeft = '5px solid #666';
                });
                document.querySelectorAll('table').forEach(function(table) {
                    table.style.backgroundColor = '#333';
                    table.style.color = 'white';
                    table.querySelectorAll('th').forEach(function(th) {
                        th.style.backgroundColor = '#555';
                    });
                    table.querySelectorAll('tr:nth-child(even)').forEach(function(tr) {
                        tr.style.backgroundColor = '#444';
                    });
                });

                // Admonitions in Dark Mode
                document.querySelectorAll('.admonition.note').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#005f7f'; // Dark blue
                    admonition.style.color = 'white';
                    admonition.style.borderLeft = '5px solid #00aaff'; // Brighter blue border
                });
                document.querySelectorAll('.admonition.warning').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#806000'; // Darker yellow
                    admonition.style.color = 'white';
                    admonition.style.borderLeft = '5px solid #ffcc00'; // Yellow border
                });
                document.querySelectorAll('.admonition.danger').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#721c24'; // Dark red
                    admonition.style.color = 'white';
                    admonition.style.borderLeft = '5px solid #f50000'; // Bright red border
                });
                document.querySelectorAll('.admonition.success').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#2f5b3b'; // Light blue
                    admonition.style.color = 'white';
                    admonition.style.borderLeft = '5px solid #28a745'; // Blue border
                });
                document.querySelectorAll('.admonition.info').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#2b4e58'; // Light yellow
                    admonition.style.color = 'white';
                    admonition.style.borderLeft = '5px solid #17a2b8'; // Orange border
                });
                document.querySelectorAll('.admonition.tip').forEach(function(admonition) {
                    admonition.style.backgroundColor = '#4e545c'; // Light red
                    admonition.style.color = 'white';
                    admonition.style.borderLeft = '5px solid #007bff'; // Red border
                });
                document.querySelectorAll('.custom-button').forEach(function(button) {
                    button.style.backgroundColor = '#005f7f'; // Dark mode button color
                });
                document.querySelectorAll('.highlight').forEach(function(highlight) {
                    highlight.style.backgroundColor = '#b0b000'; // Dark mode highlight color
                    highlight.style.color = 'white'; // Text color for dark mode
                });
            """)

        # Toggle the mode flag
        self.is_dark_mode = not self.is_dark_mode

    
    def update_preview(self):
        try:
            markdown_text = self.text_edit.toPlainText()

            processed_text = self.generate_toc(markdown_text)
            processed_text = self.custom_admonition_parser(processed_text)
            processed_text = self.custom_inline_alert_parser(processed_text)
            processed_text = self.custom_task_list_parser(processed_text)
            processed_text = self.custom_definition_list_parser(processed_text)
            processed_text = self.highlight_text_with_equal(processed_text)

            # Parse the markdown text with checkbox and admonition block support
            html = markdown2.markdown(
                processed_text,
                extras=[
                    "fenced-code-blocks",
                    "tables",
                    "strike",
                    "cuddled-lists",
                    "metadata",
                    "footnotes",
                    "task_list",
                    "abbr",  # Adds support for abbreviations
                    "def_list",  # Adds support for definition lists
                    "smarty",
                    "toc",
                    "pypages"  # Adds support for smart quotes and dashes
                ]
            )

            pygments_css = HtmlFormatter().get_style_defs('.codehilite')

            # CSS for rendering the admonition blocks and other elements
            styled_html = f"""
            <html>
            <head>
            <style>
            body {{
                line-height: 1.6;
                margin: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            table, th, td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            img {{
                display: inline-block;
                max-width: 100%;
                height: auto;
            }}
            blockquote {{
                margin: 20px 0;
                padding: 10px 20px;
                background-color: #f9f9f9;
                border-left: 5px solid #ccc;
                border-radius: 3px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin: 20px 0 10px;
                padding-bottom: 10px;
                border-bottom: 1px solid #ddd;
            }}
            .btn {{
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-align: center;
                border-radius: 4px;
                text-decoration: none;
            }}
            pre {{
                background-color: #E9E9E9;
                padding: 10px;
                overflow-x: auto;
                border-radius: 5px;
            }}
            code {{
                background-color: #E9E9E9;
                padding: 2px 4px;
                border-radius: 3px;
            }}
            mark {{
                background-color: #f9ff0f;
                border-radius: 7px;
                padding: 4px;
                color: black;
            }}
            input[type="checkbox"] {{
                transform: scale(1.2);
                margin-right: 10px;
            }}
            li.task-list-item {{
                list-style-type: none;
            }}
            /* Inline Alert Styles */
            .inline-alert {{
                padding: 0.5em;
                border-radius: 5px;
            }}
            /* Admonition styles */
            .admonition {{
                border-left: 5px solid #ccc;
                padding: 10px;
                margin: 20px 0;
                border-radius: 3px;
            }}
            .admonition.note {{
                background-color: #e7f3fe;
                border-color: #007bff;
            }}
            .admonition.warning {{
                background-color: #fff3cd;
                border-color: #ffa726;
            }}
            .admonition.danger {{
                background-color: #f8d7da;
                border-color: #dc3545;
            }}
            .admonition.success {{
                background-color: #d4edda;
                border-color: #28a745;
            }}
            .admonition.info {{
                background-color: #d1ecf1;
                border-color: #17a2b8;
            }}
            .admonition.tip {{
                background-color: #e2e3e5;
                border-color: #007bff;
            }}
            progress {{
            width: 100%;
        }}
            /* Badge Styles */
            .custom-badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 12px;
                background-color: #007bff;
                color: white;
                margin: 0 5px;
            }}

            /* Highlight Block Styles */
            .highlight {{
                background-color: #f9ff0f;
                border-radius: 7px;
                padding: 4px;
                color: black;
            }}

            /* Callout Styles */
            .custom-callout {{
                padding: 10px;
                border-left: 5px solid #007bff;
                background-color: #e3f2fd;
                margin: 10px 0;
            }}

            /* Button Styles */
            .custom-button {{
                display: inline-block;
                padding: 10px 15px;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
            }}
            /* Custom Progress Bar Styles */
.custom-progress-bar {{
    background-color: #f3f3f3;
    border-radius: 8px;
    overflow: hidden;
}}
            </style>
            <style>
            {pygments_css}
            </style>
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script type="text/javascript">
            document.addEventListener('DOMContentLoaded', function() {{
                mermaid.initialize({{startOnLoad:true}});
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
            }});
            </script>
            <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>
            <script type="text/javascript">
            window.MathJax = {{
                tex: {{
                    inlineMath: [['$', '$'], ['\\(', '\\)']],
                    packages: {{'[+]': ['noerrors']}}
                }},
                options: {{
                    ignoreHtmlClass: 'tex2jax_ignore',
                    processHtmlClass: 'tex2jax_process'
                }}
            }};
            document.addEventListener('DOMContentLoaded', function() {{
                MathJax.typesetPromise().catch(function(err) {{
                    console.error('MathJax typeset error:', err);
                }});
            }});
            </script>
            </head>
            <body>{html}</body>
            </html>
            """

            self.preview_browser.setHtml(styled_html)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating the preview: {e}")

    def highlight_text_with_equal(self, text):
        return re.sub(r'==(.+?)==', r'<span class="highlight">\1</span>', text)

    def custom_admonition_parser(self, text):
        admonition_pattern = r'::: (\w+)\s+(.*?)\n:::\s*'
        return re.sub(admonition_pattern, r'<div class="admonition \1">\2</div>', text, flags=re.DOTALL)
    
    def insert_admonition_from_menu(self, admonition_type):
        # Define the Markdown format for the selected admonition
        markdown_format = f"::: {admonition_type}\nYour message here\n:::\n"

        # Insert the Markdown into the QTextEdit
        cursor = self.text_edit.textCursor()
        cursor.insertText(markdown_format)
        self.text_edit.setTextCursor(cursor)

    def insert_admonition_from_combobox(self):
        # Get the selected index

        selected_index = self.admonition_combobox.currentIndex()
        
        # Define Markdown format based on the selected index
        if selected_index == 0:
            return  # Do nothing if the default option is selected
        elif selected_index == 1:
            self.insert_blockquote()
            return
        elif selected_index == 2:
            self.make_inline_code()
            return
        elif selected_index == 3:
            self.insert_code_block()
            return
        else:
            selected_admonition = self.admonition_combobox.currentText().replace(" block" or " Block", "").lower()

            if selected_admonition=="note":
                markdown_format = f"\n::: {selected_admonition}\n<span style='color: #007bff; font-weight: bold;'>{selected_admonition.capitalize()}:</span>\n\nYour message here\n:::\n"
            elif selected_admonition=="warning":
                markdown_format = f"\n::: {selected_admonition}\n<span style='color: #ffa726; font-weight: bold;'>{selected_admonition.capitalize()}:</span>\n\nYour message here\n:::\n"
            elif selected_admonition=="danger":
                markdown_format = f"\n::: {selected_admonition}\n<span style='color: #dc3545; font-weight: bold;'>{selected_admonition.capitalize()}:</span>\n\nYour message here\n:::\n"
            elif selected_admonition=="success":
                markdown_format = f"\n::: {selected_admonition}\n<span style='color: #28a745; font-weight: bold;'>{selected_admonition.capitalize()}:</span>\n\nYour message here\n:::\n"
            elif selected_admonition=="info":
                markdown_format = f"\n::: {selected_admonition}\n<span style='color: #17a2b8; font-weight: bold;'>{selected_admonition.capitalize()}:</span>\n\nYour message here\n:::\n"
            elif selected_admonition=="tip":
                markdown_format = f"\n::: {selected_admonition}\n<span style='color: #007bff; font-weight: bold;'>{selected_admonition.capitalize()}:</span>\n\nYour message here\n:::\n"
            else:
                markdown_format = f"\n::: {selected_admonition}\nYour message here\n:::\n"

            cursor = self.text_edit.textCursor()
            cursor.insertText(markdown_format)
            self.text_edit.setTextCursor(cursor)

            self.admonition_combobox.setCurrentIndex(0)

    def custom_inline_alert_parser(self, text):
        inline_alert_pattern = r'> (.*?)\n'
        return re.sub(inline_alert_pattern, r'<div class="alert">\1</div>', text)

    def custom_task_list_parser(self, text):
        task_list_pattern = r'- \[(x| )\] (.*?)\n'
        return re.sub(task_list_pattern, lambda m: f'<li class="task-list-item"><input type="checkbox" {"checked" if m.group(1) == "x" else ""}> {m.group(2)}</li>', text)

    def custom_definition_list_parser(self, text):
        definition_list_pattern = r'(\w.+?)\n: (.+?)\n'
        return re.sub(definition_list_pattern, r'<dl><dt>\1</dt><dd>\2</dd></dl>', text)

    def generate_toc(self, markdown_text):
        # Regular expression to find headings
        headings = re.findall(r'^(#{1,6})\s+(.*)', markdown_text, re.MULTILINE)

        # If no headings, return the original text
        if not headings:
            return markdown_text

        toc_lines = []
        toc_lines.append("<ul>")

        # Generate ToC based on the headings
        for level, title in headings:
            indent_level = len(level) - 1
            toc_lines.append(f'{"    " * indent_level}<li><a href="#{title}">{title}</a></li>')

        toc_lines.append("</ul>")

        toc = "\n".join(toc_lines)

        # Replace the [TOC] placeholder with the generated ToC
        return markdown_text.replace('[TOC]', toc)


    def save_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
            self.preview_browser.page().printToPdf(file_path)

    def toggle_tree_view(self):
        if self.tree_view.isVisible():
            self.tree_view.hide()  # Collapse TreeView
            self.splitter.setSizes([0, 500, 500])
        else:
            self.tree_view.show()
            self.splitter.setSizes([200, 500, 500])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg','.md', '.commonmark', '.markdown', '.textile', '.mmd', '.Rmd', '.gfm', '.txt', '.rtf', '.docx', '.xml', '.odt')):
                event.acceptProposedAction()  # Accept only if it's an `.md` file
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_path = urls[0].toLocalFile()

            # Check if the dropped file is a Markdown-related file
            if file_path.endswith(('.md', '.commonmark', '.markdown', '.textile', '.mmd', '.Rmd', '.gfm', '.txt', '.rtf', '.docx', '.xml', '.odt')):
                self.open_file_using_Drag_drop(file_path)  # Call the file opening function with the file path
                event.acceptProposedAction()
            elif urls[0].scheme() in ['http', 'https']:
                image_url = urls[0].toString()
                image_name = os.path.basename(image_url)  # You can modify how you want the image name
                markdown_image = f"![{image_name}]({image_url})"
                self.text_edit.insertPlainText(markdown_image)  # Insert Markdown for web image
                event.acceptProposedAction()
            else:
                # Check if the dropped file is an image
                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']:
                    image_name = os.path.basename(file_path)
                    # Convert the file path to a file:// URL
                    file_url = QUrl.fromLocalFile(file_path).toString()
                    markdown_image = f"[{image_name}]({file_url})"
                    self.text_edit.insertPlainText(markdown_image)
                    event.acceptProposedAction()
                else:
                    event.ignore()
        else:
            event.ignore()

    def open_file_using_Drag_drop(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", 
"Markdown Files (*.md);;"
"CommonMark Files (*.commonmark);;"
"Markdown Extra Files (*.markdown);;"
"GitHub Flavored Markdown Files (*.gfm);;"
"Word Files (*.docx);;"
"LaTeX Files (*.tex);;"
"OpenDocument Text (*.odt);;"
"Rich Text Format (*.rtf);;"
"Plain Text (*.txt);;"
"All Files (*)")
        try:
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                file_base_name = os.path.basename(file_path)
                self.text_edit.setPlainText(file_content)
                self.current_file = file_path
                self.file_label.setText(f"<b>{file_base_name}</b> - {file_path}")
                self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                              border:1px solid #92d051;
                                      padding:3px;
font-size:17px;
""")
                self.copy_path_button.setVisible(True)
                self.close_save_button.setVisible(True)
        except Exception as e:
            self.file_label.setStyleSheet("""
    background:#f2f2f2;
    border-radius:9px;
    border:1px solid red;
    padding:3px;
    font-size:17px;
""")
            QTimer.singleShot(5000, lambda: self.file_label.setStyleSheet("""
                background:#f2f2f2;
                border-radius:9px;
                padding:3px;
                font-size:17px;
            """))
            QMessageBox.critical(self, "Error", f"An error occurred while opening the file:\n{str(e)}")

    def open_file_from_tree(self, index):
        file_path = self.file_system_model.filePath(index)
        try:
            if file_path:
                file_base_name = os.path.basename(file_path)
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    # For image files, insert Markdown at the cursor position
                    image_markdown = f"![{file_base_name}]({file_path})"
                    cursor = self.text_edit.textCursor()
                    cursor.insertText(image_markdown)
                    self.text_edit.setTextCursor(cursor)
                else:
                    # For other file types, open and read the file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                        self.text_edit.setPlainText(file_content)
                    
                self.current_file = file_path
                self.file_label.setText(f"<b>{file_base_name}</b> - {file_path}")
                self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                              border:1px solid #92d051;
                                      padding:3px;
font-size:17px;
""")
                self.copy_path_button.setVisible(True)
                self.close_save_button.setVisible(True)
                self.update_preview()
            else:
                self.file_label.setText("•••")
                self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                      padding:3px;
font-size:17px;
""")
                self.copy_path_button.setVisible(False)
                self.close_save_button.setVisible(False)
        except Exception as e:
            self.file_label.setStyleSheet("""
    background:#f2f2f2;
    border-radius:9px;
    border:1px solid red;
    padding:3px;
    font-size:17px;
""")
            QTimer.singleShot(5000, lambda: self.file_label.setStyleSheet("""
                background:#f2f2f2;
                border-radius:9px;
                padding:3px;
                font-size:17px;
            """))
            QMessageBox.critical(self, "Error", f"An error occurred while opening the file:\n{str(e)}")


    def convert_size(self, size_bytes):
        """
        Converts the given file size in bytes to GB:MB:Bits format
        """
        size_in_bits = size_bytes * 8  # Convert bytes to bits
        size_gb = size_in_bits // (8 * 1024 * 1024 * 1024)  # Calculate GB
        size_in_bits -= size_gb * (8 * 1024 * 1024 * 1024)

        size_mb = size_in_bits // (8 * 1024 * 1024)  # Calculate MB
        size_in_bits -= size_mb * (8 * 1024 * 1024)

        return size_gb, size_mb, size_in_bits  # Remaining bits

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", 
"Markdown Files (*.md);;"
"CommonMark Files (*.commonmark);;"
"Markdown Extra Files (*.markdown);;"
"Textile Files (*.textile);;"
"MultiMarkdown Files (*.mmd);;"
"GitHub Flavored Markdown Files (*.gfm);;"
"PDF Files (*.pdf);;"
"HTML Files (*.html);;"
"Word Files (*.docx);;"
"LaTeX Files (*.tex);;"
"EPUB Files (*.epub);;"
"OpenDocument Text (*.odt);;"
"Rich Text Format (*.rtf);;"
"XML Files (*.xml);;"
"Plain Text (*.txt);;"
"Beamer Files (*.tex);;"
"All Files (*)", options=options)
        if file_name:
            self.current_file = file_name
            self.save_file()

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", 
"Markdown Files (*.md);;"
"CommonMark Files (*.commonmark);;"
"Markdown Extra Files (*.markdown);;"
"GitHub Flavored Markdown Files (*.gfm);;"
"Word Files (*.docx);;"
"LaTeX Files (*.tex);;"
"OpenDocument Text (*.odt);;"
"Rich Text Format (*.rtf);;"
"Plain Text (*.txt);;"
"All Files (*)", options=options)
        
        try:
            if file_name:
                self.current_file = file_name

                file_base_name = os.path.basename(file_name) 

                # Update the file label
                self.file_label.setText(f"<b>{file_base_name}</b> - {file_name}")
                self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                              border:1px solid #92d051;
                                      padding:3px;
font-size:17px;
""")
                self.copy_path_button.setVisible(True)
                self.close_save_button.setVisible(True)

                # Open and display the file in the text edit
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.text_edit.setPlainText(file.read())
                
                self.update_preview()

                # Find the index of the file in the QFileSystemModel and highlight it in the tree view
                file_index = self.file_system_model.index(file_name)
                if file_index.isValid():
                    self.tree_view.setCurrentIndex(file_index)
                    self.tree_view.scrollTo(file_index)  # Scroll to the file in the tree view

            else:
                self.file_label.setText("•••")
                self.file_label.setStyleSheet("""
background:#f2f2f2;
                                      border-radius:9px;
                                      padding:3px;
font-size:17px;
""")
                self.copy_path_button.setVisible(False)
                self.close_save_button.setVisible(False)
        except Exception as e:
            self.file_label.setStyleSheet("""
    background:#f2f2f2;
    border-radius:9px;
    border:1px solid red;
    padding:3px;
    font-size:17px;
""")
            QTimer.singleShot(5000, lambda: self.file_label.setStyleSheet("""
                background:#f2f2f2;
                border-radius:9px;
                padding:3px;
                font-size:17px;
            """))
            QMessageBox.critical(self, "Error", f"An error occurred while opening the file:\n{str(e)}")
    def make_bold(self):
        self.format_text('**', '**')

    def make_italic(self):
        self.format_text('*', '*')

    def make_bold_italic(self):
        self.format_text('***', '***')

    def make_strikethrough(self):
        self.format_text('~~', '~~')

    def make_inline_code(self):
        self.format_text('`', '`')

    def format_text(self, start_delim, end_delim):
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()
        cursor.insertText(start_delim + cursor.selectedText() + end_delim)
        cursor.endEditBlock()
        self.update_preview()

    def apply_header(self, index):
        headers = ['# ', '## ', '### ', '#### ', '##### ', '###### ']
        if index != 0:
            self.apply_list(None)
            self.format_text(headers[index - 1], '')
            self.update_preview()
        else:
            self.apply_list(None)
            self.format_text('', '')
            self.update_preview()

    def apply_checklist(self, index):
        checklist = ['- [ ] ', '- [x] ']
        if index != 0:
            self.format_text(checklist[index - 1], '')
        elif index == 0:
            self.format_text('', '')

    def apply_list(self, index):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if not selected_text and index==1:
            formatted_lines = [f"{i + 1}. " for i, line in enumerate(self.text_edit.toPlainText().split('\n')) if line]
            cursor.insertText('\n'.join(formatted_lines))
        elif not selected_text and index==2:
            formatted_lines = [f"- " for i, line in enumerate(self.text_edit.toPlainText().split('\n')) if line]
            cursor.insertText('\n'.join(formatted_lines))
        elif index == 1:  # Ordered List
            lines = selected_text.split('\n')
            formatted_lines = [f"{i + 1}. {line}" for i, line in enumerate(lines) if line]
            cursor.insertText('\n'.join(formatted_lines))
        elif index == 2:  # Unordered List
            lines = selected_text.split('\n')
            formatted_lines = [f"- {line}" for line in lines if line]
            cursor.insertText('\n'.join(formatted_lines))
        self.update_preview()

    def eq_win(self):
        self.eqwin = QDialog(self)
        self.eqwin.setWindowTitle("Equations")
        self.eqwin.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\equation.png"))
        self.eqwin.setGeometry(100, 100, 676, 240)
        self.eqwin.setStyleSheet("""background:#f2f2f2;""")

        tsymcursor = self.text_edit.textCursor()

        trigo_fn = {
        "Sin": "$\\sin()$","Cos": "$\\cos()$","Tan": "$\\tan()$",
        "Cosec": "$\\csc()$","Sec": "$\\sec()$","Cot": "$\\cot()$",
        "Sinh": "$\\sinh()$","Cosh": "$\\cosh()$","Tanh": "$\\tanh()$",
        "Cosech": "$\\csch()$","Sech": "$\\sech()$","Coth": "$\\coth()$",
        "Sin⁻¹": "$\\sin^{-1}()$","Cos⁻¹": "$\\cos^{-1}()$","Tan⁻¹": "$\\tan^{-1}()$",
        "Cosec⁻¹": "$\\csc^{-1}()$","Sec⁻¹": "$\\sec^{-1}()$","Cot⁻¹": "$\\cot^{-1}()$",
        "Sinh⁻¹": "$\\sinh^{-1}()$","Cosh⁻¹": "$\\cosh^{-1}()$","Tanh⁻¹": "$\\tanh^{-1}()$",
        "Cosech⁻¹": "$\\csch^{-1}()$","Sech⁻¹": "$\\sech^{-1}()$","Coth⁻¹": "$\\coth^{-1}()$"
        }

        log_fn = {
            "Log": "$\\log()$","Ln": "$\\ln()$","Log⁻¹": "$\\log^{-1}()$",
    "Exp": "$\\exp()$","E": "$e$","10^x": "$10^x$",
    "2^x": "$2^x$","Log₁₀": "$\\log_{10}()$","Log₂": "$\\log_{2}()$",
    "Logₑ": "$\\log_{e}()$","Exp⁻¹": "$\\exp^{-1}()$","10^(-x)": "$10^{-x}$",
    "2^(-x)": "$2^{-x}$","Natural Log": "$\\ln(x)$","Logarithm": "$\\log_b(x)$",
    "Power": "$b^x$","Exp Growth": "$a e^{bx}$","Exp Decay": "$a e^{-bx}$",
    "Log Growth": "$a \\log_b(x)$","Log Decay": "$a \\log_b(x)^{-1}$"
        }

        algebraic = {
    "Polynomial": "$P(x) = a_n x^n + a_{n-1} x^{n-1} + \\cdots + a_1 x + a_0$",
    "Quadratic": "$ax^2 + bx + c$",
    "Cubic": "$ax^3 + bx^2 + cx + d$",
    "Linear": "$mx + b$",
    "Exponential": "$a e^{bx}$",
    "Rational": "$\\frac{P(x)}{Q(x)}$",
    "Absolute Value": "$|x|$",
    "Square Root": "$\\sqrt{x}$",
    "Cube Root": "$\\sqrt[3]{x}$",
    "Nth Root": "$\\sqrt[n]{x}$",
    "Logarithmic": "$a \\log_b(x) + c$",
    "Step Function": "$\\lfloor x \\rfloor$",
    "Greatest Integer": "$\\lfloor x \\rfloor$",
    "Least Integer": "$\\lceil x \\rceil$",
    "Piecewise": "$\\begin{cases} a x + b & \\text{if } x < 0 \\\\ c x^2 + d & \\text{if } x \\geq 0 \\end{cases}$",
    "Floor Function": "$\\lfloor x \\rfloor$",
    "Ceiling Function": "$\\lceil x \\rceil$"
}
        
        calculas = {
    "Derivative": "$\\frac{d}{dx} f(x)$",
    "Partial Derivative": "$\\frac{\\partial}{\\partial x} f(x, y)$",
    "Second Derivative": "$\\frac{d^2}{dx^2} f(x)$",
    "Integral": "$\\int f(x) \\, dx$",
    "Definite Integral": "$\\int_{a}^{b} f(x) \\, dx$",
    "Double Integral": "$\\int_{a}^{b} \\int_{c}^{d} f(x, y) \\, dy \\, dx$",
    "Triple Integral": "$\\int_{a}^{b} \\int_{c}^{d} \\int_{e}^{f} f(x, y, z) \\, dz \\, dy \\, dx$",
    "Surface Integral": "$\\int_{S} f(x, y, z) \\, dS$",
    "Line Integral": "$\\int_{C} f(x, y) \\, ds$",
    "Gradient": "$\\nabla f(x, y, z)$",
    "Divergence": "$\\nabla \\cdot \\mathbf{F}$",
    "Curl": "$\\nabla \\times \\mathbf{F}$",
    "Laplace Transform": "$\\mathcal{L}\\{f(t)\\}(s)$",
    "Inverse Laplace Transform": "$\\mathcal{L}^{-1}\\{F(s)\\}(t)$",
    "Fourier Transform": "$\\mathcal{F}\\{f(t)\\}(\\omega)$",
    "Inverse Fourier Transform": "$\\mathcal{F}^{-1}\\{F(\\omega)\\}(t)$",
    "Taylor Series": "$f(x) = f(a) + f'(a)(x - a) + \\frac{f''(a)}{2!}(x - a)^2 + \\cdots$",
    "Maclaurin Series": "$f(x) = f(0) + f'(0)x + \\frac{f''(0)}{2!}x^2 + \\cdots$",
    "Integral Test": "$\\int_{a}^{\\infty} f(x) \\, dx$",
    "Comparison Test": "$\\text{Compare } f(x) \\text{ and } g(x)$",
}


        def create_button(text, insert_text, parent):
            button = QPushButton(text, parent)
            button.setFixedWidth(160)
            button.setStyleSheet("""
font-size:15px;
""")
            button.pressed.connect(lambda: tsymcursor.insertText(insert_text))
            return button

        # Create a tab widget
        tab = QTabWidget(self.eqwin)  # Adjust the geometry as needed
        tab.setStyleSheet("""
                                 QPushButton{
                                 border-radius:7px;
                                 border:1px solid #ccc;
                          padding:3px;}
QPushButton:hover{
                          border:1px solid royalblue;
                          color:royalblue;
                          }
QTabWidget::pane { 
            background: white;
            border-radius: 10px;
        }
        QTabWidget::tab-bar {
            alignment: center;
            border-radius:4px;
            background:white;
        }
        
        QTabBar::tab {
            background: white;
            border: 0px solid lightgrey;
            padding: 5px;
            width:150px;
            border-radius:6px;
            margin-bottom:7px;
            margin:4px;
        }
                          QTabBar::tab:hover {
            background: white;
            border-bottom: 3px solid grey;
            color:black;
            padding: 5px;
            border-radius:3px;
            margin-bottom:7px;
            margin:4px;
        }
        
        QTabBar::tab:selected {
            background: white;
            border-bottom: 3px solid royalblue;
            color:royalblue;
            padding: 5px;
            border-radius:3px;
            margin-bottom:7px;
            margin:4px;
        }
                                 """)

        # Create the tab for Trigonometric Functions
        trig_functions_tab = QWidget()
        trig_grid = QGridLayout(trig_functions_tab)

        # Add buttons for trigonometric functions
        row, column = 0, 0
        for name, insert_text in trigo_fn.items():
            button = create_button(name, insert_text, trig_functions_tab)
            trig_grid.addWidget(button, row, column)
            column += 1
            if column > 3:  # Adjust column limit as per your layout
                column = 0
                row += 1

        trig_functions_tab.setLayout(trig_grid)

        log_functions_tab = QWidget()
        log_grid = QGridLayout(log_functions_tab)

        # Add buttons for logarithmic functions
        row, column = 0, 0
        for name, insert_text in log_fn.items():
            button = create_button(name, insert_text, log_functions_tab)
            log_grid.addWidget(button, row, column)
            column += 1
            if column > 3:  # Adjust column limit as per your layout
                column = 0
                row += 1

        log_functions_tab.setLayout(log_grid)

        algebraic_functions_tab = QWidget()
        algebraic_grid = QGridLayout(algebraic_functions_tab)

        # Add buttons for trigonometric functions
        row, column = 0, 0
        for name, insert_text in algebraic.items():
            button = create_button(name, insert_text, algebraic_functions_tab)
            algebraic_grid.addWidget(button, row, column)
            column += 1
            if column > 3:  # Adjust column limit as per your layout
                column = 0
                row += 1

        algebraic_functions_tab.setLayout(algebraic_grid)

        calculas_functions_tab = QWidget()
        calculas_grid = QGridLayout(calculas_functions_tab)

        # Add buttons for trigonometric functions
        row, column = 0, 0
        for name, insert_text in calculas.items():
            button = create_button(name, insert_text, calculas_functions_tab)
            calculas_grid.addWidget(button, row, column)
            column += 1
            if column > 3:  # Adjust column limit as per your layout
                column = 0
                row += 1

        calculas_functions_tab.setLayout(calculas_grid)

        # Add the Trigonometric Functions tab to the tab widget
        tab.addTab(trig_functions_tab, "Trigonometric Functions")
        tab.addTab(log_functions_tab, "Logarithmic Functions")
        tab.addTab(algebraic_functions_tab, "Algebraic Functions")
        tab.addTab(calculas_functions_tab, "Calculas Functions")

        self.eqwin.show()

    def show_link_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\link.png"))
        dialog.setWindowTitle("Add Link")
        dialog.setStyleSheet("""
QDialog {
                             background:#f2f2f2;
                             }
QLabel{
                             font-size:12px;
                             background:#f2f2f2;
                             }
QLineEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border-bottom:1px solid #ccc;
                             background:white;
                             }
QLineEdit:focus {
                             border:2px solid royalblue;}
QTextEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border:1px solid #ccc;
                             background:white;
                             }
QTextEdit:focus {
                             border:2px solid royalblue;}
QPushButton{
                             border-radius:5px;
                             padding:5px;
                             border:1px solid #ccc;
                             font-size:12px;
                             background:white;
                             }
QPushButton:hover{
                             color:royalblue;
                             border:2px solid royalblue;

""")
        layout = QFormLayout(dialog)
        
        self.link_url = QLineEdit()
        self.link_text = QLineEdit()
        layout.addRow("URL:", self.link_url)
        layout.addRow("Text:", self.link_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.add_link)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        button_stylesheet = """
            QPushButton:hover {
                border: 1px solid royalblue;
                color: royalblue;
            }
        """

        ok_button.setStyleSheet(button_stylesheet)
        cancel_button.setStyleSheet(button_stylesheet)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def add_link(self):
        url = self.link_url.text()
        text = self.link_text.text()
        if url:
            if text:
                self.text_edit.insertPlainText(f"[{text}]({url})")
                self.update_preview()
        elif url:
            self.text_edit.insertPlainText(f"[]({url})")
            self.update_preview()
        elif text:
            self.text_edit.insertPlainText(f"[{text}](url of link)")
            self.update_preview()
        else:
            self.text_edit.insertPlainText(f"[title of link](url of link)")
            self.update_preview()

    def show_image_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Insert Image")
        dialog.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\image.png"))
        dialog.setStyleSheet("""
QDialog {
                             background:#f2f2f2;
                             }
QLabel{
                             font-size:12px;
                             background:#f2f2f2;
                             }
QLineEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border-bottom:1px solid #ccc;
                             background:white;
                             }
QLineEdit:focus {
                             border:2px solid royalblue;}
QTextEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border:1px solid #ccc;
                             background:white;
                             }
QTextEdit:focus {
                             border:2px solid royalblue;}
QPushButton{
                             border-radius:5px;
                             padding:5px;
                             border:1px solid #ccc;
                             font-size:12px;
                             background:white;
                             }
QPushButton:hover{
                             color:royalblue;
                             border:2px solid royalblue;

""")
        layout = QFormLayout(dialog)
        
        self.image_url = QLineEdit()
        self.alt_text = QLineEdit()
        layout.addRow("Image URL:", self.image_url)
        layout.addRow("Alt Text:", self.alt_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.add_image)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        button_stylesheet = """
            QPushButton:hover {
                border: 1px solid royalblue;
                color: royalblue;
            }
        """

        ok_button.setStyleSheet(button_stylesheet)
        cancel_button.setStyleSheet(button_stylesheet)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def open_progress_bar_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\progbar.png"))
        dialog.setWindowTitle("Insert Progress Bar")
        dialog.setStyleSheet("""
QDialog {
                             background:#f2f2f2;
                             }
QLabel{
                             font-size:12px;
                             background:#f2f2f2;
                             }
QLineEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border-bottom:1px solid #ccc;
                             background:white;
                             }
QLineEdit:focus {
                             border:2px solid royalblue;}
QTextEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border:1px solid #ccc;
                             background:white;
                             }
QTextEdit:focus {
                             border:2px solid royalblue;}
QPushButton{
                             border-radius:5px;
                             padding:5px;
                             border:1px solid #ccc;
                             font-size:12px;
                             background:white;
                             }
QPushButton:hover{
                             color:royalblue;
                             border:2px solid royalblue;

""")

        layout = QFormLayout(dialog)

        # Create input fields with labels
        progress_value_input = QLineEdit(dialog)
        progress_value_input.setPlaceholderText("Enter progress percentage (0-100%)")

        max_value_input = QLineEdit(dialog)
        max_value_input.setPlaceholderText("Enter max value (default is 100)")

        width_input = QLineEdit(dialog)
        width_input.setPlaceholderText("Enter width (e.g., 100px or 100%)")

        height_input = QLineEdit(dialog)
        height_input.setPlaceholderText("Enter height (e.g., 20px)")

        color_input = QLineEdit(dialog)
        color_input.setPlaceholderText("Enter color (e.g., #4caf50)")

        # Set fixed width for all line edits
        fixed_width = 250  # Set suitable width for the placeholders
        for line_edit in [progress_value_input, max_value_input, width_input,
                          height_input, color_input]:
            line_edit.setFixedWidth(fixed_width)

        layout.addRow("Max Value:", max_value_input)
        layout.addRow("Progress Value:", progress_value_input)
        layout.addRow("Width:", width_input)
        layout.addRow("Height:", height_input)
        layout.addRow("Color:", color_input)

        # Create button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_progress_bar(progress_value_input.text(),
                                                                  max_value_input.text(),
                                                                  width_input.text(),
                                                                  height_input.text(),
                                                                  color_input.text(),
                                                                  dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Set custom styles for buttons
        button_stylesheet = """
            QPushButton:hover {
                border: 1px solid royalblue;
                color: royalblue;
            }
        """

        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        ok_button.setStyleSheet(button_stylesheet)
        cancel_button.setStyleSheet(button_stylesheet)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_progress_bar(self, progress_value, max_value, width, height, color, dialog):
        # Input validation
        if not progress_value.isdigit() or not (0 <= int(progress_value) <= 100):
            QMessageBox.warning(dialog, "Invalid Input", "Please enter a valid percentage between 0 and 100.")
            return

        # Default max value if not specified
        max_value = max_value or "100"

        cursor = self.text_edit.textCursor()
        # Insert the progress bar tag at the cursor position
        cursor.insertText(
            f'\n<div style="padding: 2px; width: {width};">'
            f'<progress value="{progress_value}" max="{max_value}" '
            f'style="width: 100%; height: {height}; background-color: {color};">'
            f'</progress>'
            f'</div>'
        )
        dialog.accept()
        self.update_preview()

    def add_image(self):
        url = self.image_url.text()
        alt_text = self.alt_text.text()
        if url:
            if alt_text:
                self.text_edit.insertPlainText(f"\n![{alt_text}]({url})")
                self.update_preview()
        elif url:
            self.text_edit.insertPlainText(f"\n![]({url})")
            self.update_preview()
        elif alt_text:
            self.text_edit.insertPlainText(f"\n![{alt_text}](url of image)")
            self.update_preview()
        else:
            self.text_edit.insertPlainText(f"\n![title of image](url of image)")
            self.update_preview()

    def show_section_header_dialog(self):
        dialog = QDialog(self)
        dialog.setGeometry(600, 300, 700, 500)
        dialog.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\sectionheader.png"))
        dialog.setWindowTitle("Add Header")
        dialog.setStyleSheet("""
QDialog {
                             background:#f2f2f2;
                             }
QLabel{
                             font-size:12px;
                             background:#f2f2f2;
                             }
QLineEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border-bottom:1px solid #ccc;
                             background:white;
                             }
QLineEdit:focus {
                             border:2px solid royalblue;}
QTextEdit {
                             border-radius:5px;
                             font-size:12px;
                             padding:5px;
                             border:1px solid #ccc;
                             background:white;
                             }
QTextEdit:focus {
                             border:2px solid royalblue;}
QPushButton{
                             border-radius:5px;
                             padding:5px;
                             border:1px solid #ccc;
                             font-size:12px;
                             background:white;
                             }
QPushButton:hover{
                             color:royalblue;
                             border:2px solid royalblue;

""")
        layout = QFormLayout(dialog)
        
        self.header_text = QLineEdit()
        layout.addRow("Header Text:", self.header_text)

        self.content_text = QTextEdit()
        layout.addRow("Content:", self.content_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.add_header)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        button_stylesheet = """
            QPushButton:hover {
                border: 1px solid royalblue;
                color: royalblue;
            }
        """

        ok_button.setStyleSheet(button_stylesheet)
        cancel_button.setStyleSheet(button_stylesheet)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def add_header(self):
        header = self.header_text.text()
        content = self.content_text.toPlainText()
        if header:
            if content:
                self.text_edit.insertPlainText(f"<details>\n<summary>{header}</summary>\n{content}\n</details>")
                self.update_preview()
        elif content:
            self.text_edit.insertPlainText(f"<details>\n<summary>Your Header Here</summary>\n{content}\n</details>")
            self.update_preview()
        elif header:
            self.text_edit.insertPlainText(f"<details>\n<summary>{header}</summary>\nYour Content Here\n</details>")
            self.update_preview()
        else:
            self.text_edit.insertPlainText(f"<details>\n<summary>Your Header Here</summary>\nYour Content Here\n</details>")
            self.update_preview()

    def insert_table_dialog(self):
        # Create the dialog window
        dialog = QDialog()
        dialog.setWindowTitle("Insert Table")
        dialog.setWindowIcon(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\table.png"))
        dialog.setGeometry(600, 300, 700, 500)

        # Main layout for the dialog
        layout = QVBoxLayout(dialog)

        # Create a toolbar for table actions
        toolbar = QToolBar("Table Actions")
        toolbar.setStyleSheet("""
background:white;
                              border-radius:8px;
                              padding:5px;
""")
        layout.addWidget(toolbar)

        table_widget = QTableWidget(2, 2)
        table_widget.setHorizontalHeaderLabels(["Header 1", "Header 2"])
        layout.addWidget(table_widget)

        # Function to add a row
        def add_row():
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)

        # Function to add a column
        def add_column():
            col_position = table_widget.columnCount()
            table_widget.insertColumn(col_position)

        # Function to delete the currently selected row
        def delete_row():
            current_row = table_widget.currentRow()
            if current_row >= 0:
                table_widget.removeRow(current_row)

        # Function to delete the currently selected column
        def delete_column():
            current_col = table_widget.currentColumn()
            if current_col >= 0:
                table_widget.removeColumn(current_col)

        def clear_table():
            table_widget.clear()
            table_widget.setRowCount(0)
            table_widget.setColumnCount(0)

        def clear_table_contents():
            table_widget.clearContents()

        # Function to edit table headers
        def edit_headers():
            cols = table_widget.columnCount()
            for col in range(cols):
                current_header = table_widget.horizontalHeaderItem(col).text() if table_widget.horizontalHeaderItem(col) else ''
                new_header, ok = QInputDialog.getText(dialog, f"Edit Header for Column {col+1}", "Enter new header:", text=current_header)
                if ok and new_header:
                    table_widget.setHorizontalHeaderItem(col, QTableWidgetItem(new_header))

        # Add actions for toolbar buttons
        add_row_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\addrow.png"),"Add Row", dialog)
        add_row_action.triggered.connect(add_row)
        toolbar.addAction(add_row_action)

        add_column_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\addcol.png"),"Add Column", dialog)
        add_column_action.triggered.connect(add_column)
        toolbar.addAction(add_column_action)

        delete_row_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\delrow.png"),"Delete Row", dialog)
        delete_row_action.triggered.connect(delete_row)
        toolbar.addAction(delete_row_action)

        delete_column_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\delcol.png"),"Delete Column", dialog)
        delete_column_action.triggered.connect(delete_column)
        toolbar.addAction(delete_column_action)

        clear_whole_table = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\deltab.png"),"Clear Table", dialog)
        clear_whole_table.triggered.connect(clear_table)
        toolbar.addAction(clear_whole_table)

        clear_table_contents_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\delcont.png"),"Clear Table Contents", dialog)
        clear_table_contents_action.triggered.connect(clear_table_contents)
        toolbar.addAction(clear_table_contents_action)

        # Add header editing action to toolbar
        edit_headers_action = QAction(QtGui.QIcon("C:\\Users\\rishi\\OneDrive\\Documents\\ME_Icons\\edithead.png"),"Edit Headers", dialog)
        edit_headers_action.triggered.connect(edit_headers)
        toolbar.addAction(edit_headers_action)

        # Function to convert the table to Markdown and insert into the text edit
        def embed_table():
            rows = table_widget.rowCount()
            cols = table_widget.columnCount()

            # Get the content from the table widget
            markdown_table = []

            # Extract the header row
            headers = ["| " + " | ".join([table_widget.horizontalHeaderItem(c).text() if table_widget.horizontalHeaderItem(c) else '' for c in range(cols)]) + " |"]
            markdown_table.append(headers[0])

            # Add separator row
            separators = "| " + " | ".join(["-" * 8 for _ in range(cols)]) + " |"
            markdown_table.append(separators)

            # Extract each row of the table
            for row in range(rows):
                row_data = []
                for col in range(cols):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else " ")
                markdown_table.append("| " + " | ".join(row_data) + " |")

            # Join the table lines and insert into text_edit
            markdown_text = "\n".join(markdown_table)
            self.text_edit.insertPlainText(markdown_text)
            dialog.accept()  # Close the dialog

        # Add 'Embed' button to insert the table as markdown
        button_layout = QHBoxLayout()
        embed_button = QPushButton("Embed Table")
        embed_button.clicked.connect(embed_table)
        embed_button.setStyleSheet("""
                                   QPushButton{
                                   border-radius:5px;
                                   padding:6px;
                                   background:white;}

QPushButton:hover{
border:1px solid royalblue;
                                   color:royalblue;}
""")
        button_layout.addWidget(embed_button)

        layout.addLayout(button_layout)

        # Show the dialog and wait for user action
        dialog.exec_()

    def insert_blockquote(self):
        cursor = self.text_edit.textCursor()
        cursor.insertText("> " + cursor.selectedText().replace("\n", "\n> "))
        self.update_preview()

    def insert_code_block(self):
        self.format_text("```\n", "\n```")

    def highlight_text(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if selected_text:
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(f'=={selected_text}==')
            cursor.endEditBlock()
            self.update_preview()

    def make_subscript(self):
        self.format_text("<sub>", "</sub>")

    def make_superscript(self):
        self.format_text("<sup>", "</sup>")

    def insert_horizontal_line(self):
        self.text_edit.insertPlainText("\n---\n")
        self.update_preview()

    def insert_comment(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if selected_text:
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(f'<!-- {selected_text} -->')
            cursor.endEditBlock()
            self.update_preview()

    def remove_comment(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if selected_text:
            uncommented_text = selected_text.replace("<!-- ", "").replace(" -->", "")
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(uncommented_text)
            cursor.endEditBlock()
            self.update_preview()

    def new(self):
        spawn = MarkdownEditor()

        spawn.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    editor = MarkdownEditor()
    editor.showMaximized()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
