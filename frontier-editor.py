import sys
import re

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog



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

        define_regex = re.compile(r"#define\s+(?P<define_name>" + prefix + r"[A-z0-9_]*)\s+(?P<value_expression>[A-z0-9_()+&-|<> ]*)")

        for match in re.finditer(define_regex, constants_text):

            label = match.group("define_name")
            expr  = match.group("value_expression")

            if expr and label not in constants:
                constants[label] = self.evaluate_expression(expr.strip(), constants)
            

        # why is this key being inserted????
        constants.pop("__builtins__")
        return constants


    def reverse_dict(self, original_dict={}):
        return {value: key for key, value in original_dict.items()}


    pass



class FrontierEditor():

    def __init__(self):

        self.app = QtWidgets.QApplication(sys.argv)
        self.mainwindow = uic.loadUi("forms/MainWindow.ui")
        self.connect_signals()

        self.root = ""

        pass


    def connect_signals(self):

        self.mainwindow.pushButton_addMon.clicked.connect(self.show_add_mon_window)
        self.mainwindow.actionOpen.triggered.connect(self.open_project)

        pass


    def run(self):

        self.mainwindow.show()
        self.app.exec()

        pass


    def show_add_mon_window(self):

        add_window = uic.loadUi("forms/AddFrontierMon.ui");
        add_window.setModal(True)
        add_window.exec()

        pass


    def open_project(self):

        dlg = QFileDialog()
        project_dir = dlg.getExistingDirectory()

        if project_dir:
            self.root = project_dir
            self.load_project()

        pass


    def load_project(self):

        self.constants = dict()

        parser = Parser()
        self.constants["species"] = parser.reverse_dict(parser.read_c_constants(self.root + "/include/constants/species.h", "SPECIES"))

        #print(self.constants)

        pass


    pass



def main():

    prog = FrontierEditor()
    prog.run()
    pass



if __name__ == '__main__':
    main()
