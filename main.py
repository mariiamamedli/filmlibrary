"""
Поле id в таблицах базы должно быть автоинкрементным!
"""

import sqlite3
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QWidget, QInputDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("filmui.ui", self)
        self.con = sqlite3.connect("films_db.sqlite")
        self.update_result()
        self.update_result_2()
        self.pushButton.clicked.connect(self.show_dialog_add)
        self.pushButton_2.clicked.connect(self.show_dialog_edit)
        self.pushButton_3.clicked.connect(self.delete_elem)
        self.pushButton_4.clicked.connect(self.add_genre)
        self.pushButton_5.clicked.connect(self.edit_genre)
        self.pushButton_6.clicked.connect(self.delete_genre)

    def update_result(self):
        self.statusBar.showMessage('')
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM films").fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(['ИД', 'Название фильма', 'Год выпуска', 'Жанр', 'Длительность'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def update_result_2(self):
        self.statusBar.showMessage('')
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM genres").fetchall()
        self.tableWidget_2.setRowCount(len(result))
        self.tableWidget_2.setColumnCount(len(result[0]))
        self.tableWidget_2.setHorizontalHeaderLabels(['ИД', 'Название жанра'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(val)))

    def show_dialog_add(self):
        self.dialog = Dialog_add(self)
        self.dialog.show()
        self.dialog.exec_()

    def show_dialog_edit(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if len(rows) != 1:
            self.statusBar.showMessage('Выберите один элемент')
        else:
            id = self.tableWidget.item(rows[0], 0).text()
            self.dialog = Dialog_edit(self, id)
            self.dialog.show()
            self.dialog.exec_()

    def delete_elem(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if len(rows) == 0:
            self.statusBar.showMessage('Выберите элементы')
        else:
            ids = [self.tableWidget.item(i, 0).text() for i in rows]
            valid = QMessageBox.question(
                self, '', "Действительно удалить элементы с id " + ",".join(ids),
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                cur = self.con.cursor()
                cur.execute("DELETE FROM films WHERE id IN (" + ", ".join(
                    '?' * len(ids)) + ")", ids)
                self.con.commit()
            self.update_result()

    def add_genre(self):
        name, ok_pressed = QInputDialog.getText(self, "Добавить элемент", "Название жанра")
        if ok_pressed:
            if name != '':
                self.con.cursor().execute("""INSERT INTO genres(title) VALUES(?)""", (name, ))
                self.con.commit()
                self.update_result_2()
            else:
                self.statusBar.showMessage('Название жанра не должно быть пустым')

    def edit_genre(self):
        rows = list(set([i.row() for i in self.tableWidget_2.selectedItems()]))
        if len(rows) != 1:
            self.statusBar.showMessage('Выберите один элемент')
        else:
            id = self.tableWidget_2.item(rows[0], 0).text()
            genre = list(self.con.cursor().execute("""SELECT title FROM genres WHERE id = ?""", (id, )))[0][0]
            name, ok_pressed = QInputDialog.getText(self, "Добавить элемент", "Название жанра", text=genre)
            if ok_pressed:
                if name != '':
                    self.con.cursor().execute("""UPDATE genres SET title = ? WHERE id = ?""", (name, id))
                    self.con.commit()
                    self.update_result_2()
                else:
                    self.statusBar.showMessage('Название жанра не должно быть пустым')

    def delete_genre(self):
        rows = list(set([i.row() for i in self.tableWidget_2.selectedItems()]))
        if len(rows) == 0:
            self.statusBar.showMessage('Выберите элементы')
        else:
            ids = [self.tableWidget_2.item(i, 0).text() for i in rows]
            valid = QMessageBox.question(
                self, '', "Действительно удалить элементы с id " + ",".join(ids),
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                cur = self.con.cursor()
                cur.execute("DELETE FROM genres WHERE id IN (" + ", ".join(
                    '?' * len(ids)) + ")", ids)
                self.con.commit()
            self.update_result_2()


class Dialog_add(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi("filmui2.ui", self)
        self.comboBox.addItems(list(map(lambda x: x[0], self.parent.con.cursor().execute("""SELECT title FROM genres"""))))
        self.label_5.setHidden(True)
        self.setModal(True)
        self.pushButton.clicked.connect(self.add_elem)

    def add_elem(self):
        try:
            self.label_5.setHidden(True)
            assert int(self.lineEdit_2.text()) <= 2021
            assert int(self.lineEdit_3.text()) > 0
            assert self.lineEdit.text() != ''
            genre = list(self.parent.con.cursor().execute("""SELECT id FROM genres WHERE title == ?""",
                                                          (self.comboBox.currentText(), )))[0][0]
            self.parent.con.cursor().execute("""INSERT INTO films(title, year, genre, duration)
             VALUES(?, ?, ?, ?)""", (self.lineEdit.text(), int(self.lineEdit_2.text()),
                                     int(genre), int(self.lineEdit_3.text())))
            self.parent.con.commit()
            self.parent.update_result()
            self.close()
        except Exception:
            self.label_5.setHidden(False)


class Dialog_edit(QDialog):
    def __init__(self, parent, id):
        super().__init__()
        self.parent = parent
        self.id = id
        self.parent.statusBar.showMessage('')
        uic.loadUi("filmui2.ui", self)
        self.setWindowTitle('Редактировать элемент')
        a = list(map(lambda x: x[0], self.parent.con.cursor().execute("""SELECT title FROM genres""")))
        self.comboBox.addItems(a)
        g = list(self.parent.con.cursor().execute("""SELECT title FROM genres WHERE id in
         (SELECT genre FROM films WHERE id = ?)""", (id, )))[0][0]
        t = list(self.parent.con.cursor().execute("""SELECT title FROM films WHERE id = ?""", (id,)))[0][0]
        y = list(self.parent.con.cursor().execute("""SELECT year FROM films WHERE id = ?""", (id,)))[0][0]
        d = list(self.parent.con.cursor().execute("""SELECT duration FROM films WHERE id = ?""", (id,)))[0][0]
        self.comboBox.setCurrentIndex(a.index(g))
        self.lineEdit.setText(t)
        self.lineEdit_2.setText(str(y))
        self.lineEdit_3.setText(str(d))
        self.label_5.setHidden(True)
        self.setModal(True)
        self.pushButton.clicked.connect(self.edit_elem)

    def edit_elem(self):
        try:
            self.label_5.setHidden(True)
            assert int(self.lineEdit_2.text()) <= 2021
            assert int(self.lineEdit_3.text()) > 0
            assert self.lineEdit.text() != ''
            id = self.id
            genre = list(self.parent.con.cursor().execute("""SELECT id FROM genres WHERE title == ?""",
                                                          (self.comboBox.currentText(), )))[0][0]
            self.parent.con.cursor().execute("UPDATE films SET title = ? WHERE id = ?", (self.lineEdit.text(), id))
            self.parent.con.cursor().execute("UPDATE films SET year = ? WHERE id = ?", (self.lineEdit_2.text(), id))
            self.parent.con.cursor().execute("UPDATE films SET duration = ? WHERE id = ?", (self.lineEdit_3.text(), id))
            self.parent.con.cursor().execute("UPDATE films SET genre = ? WHERE id = ?", (str(genre), id))
            self.parent.con.commit()
            self.parent.update_result()
            self.close()
        except Exception:
            self.label_5.setHidden(False)


app = QApplication(sys.argv)
ex = App()
ex.show()
sys.exit(app.exec())