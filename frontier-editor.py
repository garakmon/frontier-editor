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

        #frontier_mon_re = re.compile(r"\[(?P<mon_const>[A-Za-z0-9_]+)\][\s=\{\}]+.species.+(?P<species>SPECIES_[A-Za-z0-9_]+)"
        #    + r".+\s+.moves.+(?P<move1>MOVE_[A-Za-z0-9_]+).+(?P<move2>MOVE_[A-Za-z0-9_]+).+(?P<move3>MOVE_[A-Za-z0-9_]+).+(?P<move4>MOVE_[A-Za-z0-9_]+)")

        frontier_mon_re = re.compile(r"\[(?P<mon_const>FRONTIER_MON[A-Za-z0-9_]+)\]\s*=\s*\{(?P<info>[^\[]+)")

        fm_species_re = re.compile(r"species[\s=]+(?P<species>[A-Za-z0-9_]+)")
        fm_moves_re = re.compile(r"moves[\s=\{]+(?P<move1>MOVE_[|A-Za-z0-9_]+)[\s,]+(?P<move2>MOVE_[|A-Za-z0-9_]+)[\s,]+(?P<move3>MOVE_[|A-Za-z0-9_]+)[\s,]+(?P<move4>MOVE_[|A-Za-z0-9_]+)")
        fm_item_re = re.compile(r"itemTableId[\s=]+(?P<item>[A-Za-z0-9_]+)")
        fm_ev_re = re.compile(r"evSpread[\s=]+(?P<ev1>[|A-Za-z0-9_]+\b)[\s|]*(?P<ev2>[A-Za-z0-9_]+)?\b[\s|]*(?:(?P<ev3>[A-Za-z0-9_]+))?")
        fm_nature_re = re.compile(r"nature[\s=]+(?P<nature>[|A-Za-z0-9_]+)")

        for match in re.finditer(frontier_mon_re, text):

            bfmon_name = match.group("mon_const")
            bfmon_info = match.group("info")

            bfmon_species = fm_species_re.findall(bfmon_info)[0]
            bfmon_moves = list(fm_moves_re.findall(bfmon_info)[0])
            bfmon_item = fm_item_re.findall(bfmon_info)[0]
            bfmon_evs = list(fm_ev_re.findall(bfmon_info)[0])
            bfmon_nature = fm_nature_re.findall(bfmon_info)[0]

            self.frontier_mons[bfmon_name] = {
                "name": bfmon_name,
                "species": bfmon_species,
                "moves": bfmon_moves,
                "item": bfmon_item,
                "evs": bfmon_evs,
                "nature": bfmon_nature
            }

        print(self.frontier_mons)

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

        self.mainwindow.lineEdit_item.setText(monref["item"])
        self.mainwindow.lineEdit_nature.setText(monref["nature"])

        self.mainwindow.lineEdit_ev1.setText(monref["evs"][0])
        self.mainwindow.lineEdit_ev2.setText(monref["evs"][1])
        self.mainwindow.lineEdit_ev3.setText(monref["evs"][2])
        
        if monref["evs"][2]:
            self.mainwindow.label_ev1.setText("170")
            self.mainwindow.label_ev2.setText("170")
            self.mainwindow.label_ev3.setText("170")

        elif monref["evs"][1]:
            self.mainwindow.label_ev1.setText("255")
            self.mainwindow.label_ev2.setText("255")
            self.mainwindow.label_ev3.setText("0")

        else:
            self.mainwindow.label_ev1.setText("255")
            self.mainwindow.label_ev2.setText("0")
            self.mainwindow.label_ev3.setText("0")
            

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
