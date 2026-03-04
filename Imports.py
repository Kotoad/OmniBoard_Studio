"""
Imports.py - Centralized Import Manager

All imports in ONE place to avoid circular dependencies.
Every other file imports from this file.

This is the SINGLE SOURCE OF TRUTH for imports.
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import sys
import os
import json
import threading
import paramiko
import subprocess
import ctypes
import math
import time
import warnings
from datetime import datetime
if sys.platform == 'win32':
    # Code for Windows
    from ctypes import windll, wintypes, byref
elif sys.platform.startswith('linux'):
    # Code for Linux
    import fcntl
from pathlib import Path

# ============================================================================
# PYQT6 IMPORTS
# ============================================================================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea,QSizePolicy,  
    QLineEdit, QComboBox, QDialog, QTabWidget, QFileDialog, QMessageBox, QScroller,
    QInputDialog, QStyleOptionComboBox, QStyledItemDelegate, QTextEdit, QProgressDialog,
    QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsPathItem, QGraphicsItem, QGraphicsPixmapItem, QGraphicsObject,
    QListWidgetItem, QStackedWidget, QGraphicsObject, QGraphicsEllipseItem, QSplashScreen,
    QTextBrowser, QToolBar, QSlider
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, pyqtSignal, QRegularExpression, QTimer, QEvent,
    pyqtProperty, QEasingCurve, QRectF, QPropertyAnimation, QObject, QLine, QCoreApplication,
    QSortFilterProxyModel, QAbstractAnimation, QPointF, QRectF, QThread,
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QPalette, QMouseEvent, QKeySequence, QShortcut, QEventPoint,
    QRegularExpressionValidator, QFont, QPixmap, QImage, QStandardItem, QMovie, QTouchEvent,
    QPainterPath, QIcon, QStandardItemModel, QAction, QPixmap, QInputDevice, QCursor,
    QIntValidator, QDoubleValidator
)
from PyQt6.QtTest import QTest

from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
# ============================================================================
# PROJECT-SPECIFIC IMPORTS (Internal)
# ============================================================================

# Data structures and settings (NO GUI DEPENDENCIES - safe to import)
from App_settings import AppSettings
from Project_Data import ProjectData

def get_Graphic_Programing_Window():
    """Lazy import GUI MainWindow - avoid circular deps"""
    from GUI_pyqt import GUI, GridCanvas
    return GUI, GridCanvas

def get_Code_Compiler():
    """Lazy import CodeCompiler - avoid circular import"""
    from code_compiler import CodeCompiler
    return CodeCompiler

def get_Spawn_Blocks():
    """Lazy import spawning_blocks and blocks_events - avoid circular import"""
    from spawn_blocks_pyqt import spawning_blocks, blocks_events, BlockGraphicsItem
    return BlockGraphicsItem, spawning_blocks, blocks_events

def get_Device_Settings_Mindow():
    """Lazy import DeviceSettingsWindow - avoid circular import"""
    from settings_window import DeviceSettingsWindow
    return DeviceSettingsWindow

def get_Path_Manager():
    """Lazy import PathManager - avoid circular import"""
    from Path_manager_pyqt import PathManager, PathGraphicsItem
    return PathManager, PathGraphicsItem

def get_Blocks_Window():
    """Lazy import blocksWindow - avoid circular import"""
    from Blocks_window_pyqt import blocksWindow
    return blocksWindow

def get_Help_Window():
    """Lazy import HelpWindow - avoid circular import"""
    from Help_window import HelpWindow
    return HelpWindow

def get_State_Machine():
    """Lazy import AppStateMachine - avoid circular import"""
    from state_machine import AppStateMachine, CanvasStateMachine
    return AppStateMachine, CanvasStateMachine

def get_State_Manager():
    """Lazy import StateManager - avoid circular import"""
    from state_manager import StateManager
    return StateManager

def get_Translation_Manager():
    """Lazy import TranslationManager - avoid circular import"""
    from Translation_manager import TranslationManager
    return TranslationManager

def get_Data_Control():
    """Lazy import DataControl - avoid circular import"""
    from Data_control import DataControl
    return DataControl

def get_Code_Editor_Window():
    """Lazy import CodeEditorWindow - avoid circular import"""
    from Code_editor_window import CodeEditorWindow
    return CodeEditorWindow

def get_Utils():
    """Lazy import Utils to avoid circular dependency"""
    import Utils
    return Utils

def get_File_Manager():
    """Lazy import FileManager when needed"""
    from FileManager import FileManager
    return FileManager

