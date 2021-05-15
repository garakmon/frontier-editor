import sys
import re

from PyQt6.QtCore import *
from PyQt6 import QtWidgets, QtGui, uic
from PyQt6.QtWidgets import QFileDialog, QCompleter



class Parser():

    def __init__(self):
        pass


    def strip_comments(self, text=""):
        return re.sub(r"//.*?(\r\n?|\n)|/\*.*?\*/", "", text, flags=re.DOTALL)


    def evaluate_expression(self, expression="", known_constants=None):
        # TODO: if this is being distributed, make this safe
        return int(eval(expression, known_constants))


    def read_c_constants(self, filepath="", prefix=""):

        constants = {}

        with open(filepath, "r", encoding="utf-8") as in_file:
            constants_text = in_file.read()

        constants_text = self.strip_comments(constants_text)

        define_regex = re.compile(r"#define\s+(?P<define_name>[A-z0-9_]*)\s+(?P<value_expression>[A-z0-9_()+&-|<> ]*)")

        for match in re.finditer(define_regex, constants_text):

            label = match.group("define_name")
            expr  = match.group("value_expression")

            if expr and label not in constants:
                constants[label] = self.evaluate_expression(expr.strip(), constants)
            

        # why is this key being inserted????
        constants.pop("__builtins__")
        delete = []
        for c in constants.keys():
            if not c.startswith(prefix):
                delete.append(c)
        for c in delete:
            constants.pop(c)

        return constants


    def reverse_dict(self, original_dict={}):
        return {value: key for key, value in original_dict.items()}


    pass



class FrontierEditor():

    def __init__(self):

        self.app = QtWidgets.QApplication(sys.argv)
        self.mainwindow = uic.loadUi("forms/MainWindow.ui")
        self.init_ui()
        self.connect_signals()

        self.parser = Parser()

        self.root = ""
        self.constants = dict()
        self.frontier_mons = dict()

        pass


    def connect_signals(self):

        self.mainwindow.pushButton_addMon.clicked.connect(self.show_add_mon_window)
        self.mainwindow.actionOpen.triggered.connect(self.open_project)

        pass


    def init_ui(self):
        '''disable ui until user opens a project'''
        self.mainwindow.tabWidget.setEnabled(False)

        pass


    def run(self):

        self.mainwindow.show()
        self.app.exec()

        pass


    def show_add_mon_window(self):

        add_window = uic.loadUi("forms/AddFrontierMon.ui");
        add_window.setModal(True)

        add_window.comboBox_species.setEditable(True)
        add_window.comboBox_species.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        add_window.comboBox_species.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        
        add_window.comboBox_species.clear()
        add_window.comboBox_species.addItems(self.constants["species"].values())

        add_window.exec()

        pass


    def open_project(self):

        dlg = QFileDialog()
        project_dir = dlg.getExistingDirectory()

        if project_dir:
            self.root = project_dir
            self.load_project()
            self.mainwindow.tabWidget.setEnabled(True)

        pass


    def load_frontier_battle_mons(self):

        self.constants["frontier_mons"] = self.parser.reverse_dict(self.parser.read_c_constants(self.root + "/include/constants/battle_frontier_mons.h", "FRONTIER_MON_"))
        
        with open(self.root + "/src/data/battle_frontier/battle_frontier_mons.h", "r", encoding="utf-8") as f:
            text = f.read()

        frontier_mon_re = re.compile(r"\[(?P<mon_const>[A-Za-z0-9_]+)\][\s=\{\}]+.species.+(?P<species>SPECIES_[A-Za-z0-9_]+)"
            + r".+\s+.moves.+(?P<move1>MOVE_[A-Za-z0-9_]+).+(?P<move2>MOVE_[A-Za-z0-9_]+).+(?P<move3>MOVE_[A-Za-z0-9_]+).+(?P<move4>MOVE_[A-Za-z0-9_]+)")

        for match in re.finditer(frontier_mon_re, text):

            bfmon_name = match.group("mon_const")
            bfmon_species = match.group("species")
            bfmon_moves = [match.group("move1"), match.group("move2"), match.group("move3"), match.group("move4")]

            self.frontier_mons[bfmon_name] = {
                "name": bfmon_name,
                "species": bfmon_species,
                "moves": bfmon_moves,
            }

        self.mainwindow.comboBox_species.setEditable(True)
        self.mainwindow.comboBox_species.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.mainwindow.comboBox_species.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.mainwindow.comboBox_species.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        self.mainwindow.comboBox_species.currentTextChanged.connect(self.display_frontier_mon)

        self.mainwindow.comboBox_species.clear()
        self.mainwindow.comboBox_species.addItems(self.frontier_mons.keys())

        pass


    def display_frontier_mon(self, monconst):

        #print("display_frontier_mon", monconst)

        monref = self.frontier_mons[monconst]

        self.mainwindow.lineEdit_move1.setText(monref["moves"][0])
        self.mainwindow.lineEdit_move2.setText(monref["moves"][1])
        self.mainwindow.lineEdit_move3.setText(monref["moves"][2])
        self.mainwindow.lineEdit_move4.setText(monref["moves"][3])

        pass


    def load_project(self):

        self.constants = dict()

        self.constants["species"] = self.parser.reverse_dict(self.parser.read_c_constants(self.root + "/include/constants/species.h", "SPECIES"))

        #print(self.constants)

        self.load_frontier_battle_mons()

        pass


    pass



def main():

    prog = FrontierEditor()
    prog.run()
    pass



if __name__ == '__main__':
    main()
