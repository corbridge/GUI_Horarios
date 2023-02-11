from PyQt5 import uic
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import pandas as pd
import convertion
from time import sleep
from random import choice


class IntroScreen(QWidget):
    def __init__(self):
        super(IntroScreen, self).__init__()
        uic.loadUi('intro.ui', self)

        ## variables
        self.subject = None
        self.string_classes= None

        ## Texts
        self.subject_info = self.findChild(QLabel, 'subject_response')

        ## Buttons
        self.mecatronica_button = self.findChild(QPushButton, 'mecatronica_button')
        self.biomedica_button = self.findChild(QPushButton, 'biomedica_button')
        self.open_file_button = self.findChild(QPushButton, 'open_file_button_button')

        ## Combo Box
        self.subject_menu = self.findChild(QComboBox, 'subject_menu')
        self.subject_menu.addItems(self.get_previous_data())
        self.subject_menu.currentIndexChanged.connect(self._selection_change)

        ## Button actions
        self.mecatronica_button.clicked.connect(self.mecatronica_button_click)
        self.biomedica_button.clicked.connect(self.biomedica_button_click)
        self.open_file_button.clicked.connect(self.open_file)

        ## Schedule grid
        self.schedule_grid = self.findChild(QGridLayout, 'grid_schedule')
        self.rows = {'M1': 1,
                     'M2': 2,
                     'M3': 3,
                     'M4': 4,
                     'M5': 5,
                     'M6': 6,
                     'V1': 7,
                     'V2': 8,
                     'V3': 9,
                     'V4': 10,
                     'V5': 11,
                     'V6': 12,
                     'N1': 13,
                     'N2': 14,
                     'N3': 15,
                     'N4': 16,
                     'N5': 17,
                     'N6': 18}
        
        self.columns = {'1': 1,
                        '2': 2,
                        '3': 3,
                        '4': 4,
                        '5': 5,
                        '6': 6}

        self.colors = ['red','blue','green','yellow','purple','pink','orange']

        ## Initialize functions
        self.show()

    def get_previous_data(self):
        """"Gets previous data from past csv_file"""
        try:
            csv_file_read = pd.read_csv('csv_file.csv')
            self._parsing_csv_file(csv_file_read)
            self.items_list = self._make_subject_items()
            return self.items_list
        except FileNotFoundError:
            self.items_list = []
            return self.items_list

    def mecatronica_button_click(self):
        print('mecatronica')

    def biomedica_button_click(self):
        print('biomedica')

    def open_file(self):
        """Open excel file, and return a new items list from excel"""
        file, _ = QFileDialog.getOpenFileName(self, 'Open File', 'c:\\', 'Excel Files (*.xlsx)')
        csv_file = convertion.from_excel_to_csv(file)
        self._parsing_csv_file(csv_file)
        self.new_item_list = self._make_subject_items()
        self.subject_menu.addItems(self.new_item_list)

    def _parsing_csv_file(self, csv_file):
        """Parse in csv file to return string of classes"""
        csv_dict = convertion.get_dict_from_csv(csv_file)
        self.string_classes = convertion.parse_classes(csv_dict)
    
    def _make_subject_items(self):
        """Convert string classes into a list to use in items"""
        self.subject_list = convertion.get_subject_list(self.string_classes)
        return self.subject_list
    
    def _selection_change(self):
        """Select from items combo box a subject and print it in GUI"""
        try:
            self.clean_data_from_schedule()
            list_of_classes, current_text = convertion.find_class(self.subject_menu.currentText(), self.string_classes)
            self.subject_info.setText(current_text)
            self.cleaned_list_of_classes = convertion.clean_list_of_classes(list_of_classes)
            self.list_dict = convertion.get_classes_data(self.cleaned_list_of_classes)
            self.get_hour_and_day(self.list_dict)
        except IndexError:
            pass
    
    def set_label_in_schedule(self):
        self.label = QLabel("Hola")
        self.get_random_color()
        return self.label

    def get_random_color(self):
        color = choice(self.colors)
        return self.label.setStyleSheet(f"background-color: red;")

    def get_hour_and_day(self, list_dict):
        for dict in list_dict:
            self.set_label_in_schedule()
            if dict['Day'] == '135':
                days = str(dict['Day'])
                days_list = [int(days[0]), int(days[1]), int(days[2])]
                for day in days_list:
                    self.set_label_in_schedule()
                    self.schedule_grid.addWidget(self.label, self.rows[dict['Hour']], day)
            else:
                start_hour = self.rows[dict['Hour']]
                three_hour = [start_hour, start_hour + 1, start_hour + 2]
                for hour in three_hour:
                    self.set_label_in_schedule()
                    self.schedule_grid.addWidget(self.label, hour, self.columns[dict['Day']])

    def clean_data_from_schedule(self):
        for i in range(self.schedule_grid.count()):
            item = self.schedule_grid.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QLabel):
                row, column, rowSpan, columnSpan = self.schedule_grid.getItemPosition(i)
                if row != 0 and column != 0:
                    widget.setStyleSheet("")
                    widget.setText("")





app = QApplication(sys.argv) 
window = IntroScreen() 
app.exec_() 