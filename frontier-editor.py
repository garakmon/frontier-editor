import sys
from PyQt6 import QtWidgets, uic



mainwindow = None

def show_add_mon_window():

    global mainwindow

    add_window = uic.loadUi("forms/AddFrontierMon.ui");
    add_window.setModal(True)
    add_window.exec()

    pass



def connect_signals(window):

    window.pushButton_addMon.clicked.connect(show_add_mon_window)

    pass



def main():

    global mainwindow

    app = QtWidgets.QApplication(sys.argv)

    mainwindow = uic.loadUi("forms/MainWindow.ui")

    connect_signals(mainwindow)

    mainwindow.show()
    app.exec()

    pass



if __name__ == '__main__':
    main()
