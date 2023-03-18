from PyQt5 import uic
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import pandas as pd
import convertion
from time import sleep


class IntroScreen(QWidget):
    def __init__(self):
        super(IntroScreen, self).__init__()
        uic.loadUi('intro.ui', self)

        ## variables
        self.subject = None
        self.string_classes= None

        ## Buttons
        self.mecatronica_button = self.findChild(QPushButton, 'mecatronica_button')
        self.biomedica_button = self.findChild(QPushButton, 'biomedica_button')
        self.open_file_button = self.findChild(QPushButton, 'open_file_button_button')

        ## Combo Box
        self.subject_menu = self.findChild(QComboBox, 'subject_menu')
        self.subject_menu.addItems(self.get_previous_data())
        self.subject_menu.currentIndexChanged.connect(self._selection_change)
        self.count_selections_classes = [0] * self.subject_menu.count()

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

        self.set_grid_dimmensions()

        ## Schedule colors
        self.colors = ['#98F5FF','#8EE5EE','#7AC5CD','#ADD8E6','#B2DFEE','#97FFFF','#8DEEEE', '#79CDCD', '#7FFF00', ]

        ## Initialize functions
        self.show()

################# SETUP METHODS ##########################

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
    
    def _selection_change(self, index):
        """Select from items combo box a subject and print it in GUI"""
        self.changes_classes_in_comboBox = self.times_selection_changed(index)
        try:
            self.clean_data_from_schedule()
            list_of_classes, current_text = convertion.find_class(self.subject_menu.currentText(), self.string_classes)
            self.cleaned_list_of_classes = convertion.clean_list_of_classes(list_of_classes)
            self.list_dict = convertion.get_classes_data(self.cleaned_list_of_classes)
            new_ordered_list = self.order_classes(self.list_dict)
            self.display_classes(new_ordered_list)
        except IndexError:
            pass
        # self.changes_classes_in_comboBox += 1
        # self.changes_classes_in_comboBox = self.times_selection_changed(index)

    def times_selection_changed(self, index):
        selectedOption = self.subject_menu.itemText(index)
        self.count_selections_classes[index] += 1
        changed_class =  self.count_selections_classes[index]
        print("Selected option:", selectedOption, ", count:", changed_class)
        return changed_class

################# DISPLAY CLASSES METHODS ##########################

    def set_label_in_schedule(self, index):
        """"Set Professor name in schedule"""
        professor_list = self.dict['Professor'].split(' ')
        short_name = ' '.join(professor_list[0:3:2])
        self.label = QLabel(short_name)
        self.set_color_class(index)
        return self.label

    def set_color_class(self, index):
        """Set a color in label"""
        return self.label.setStyleSheet(f"background-color: {self.colors[index]};")

    def display_classes(self, list_dict):
        """Display classes in schedule"""
        count_MJ = 0
        count_LMV = 0
        for index in range(len(list_dict)):
            self.dict = list_dict[index]
            if self.dict['Day'] == '135':
                count_LMV = self.LMV_label_process(list_dict, count_LMV, index)
            else:
                count_MJ = self.MJ_label_process(list_dict, count_MJ, index)

    def LMV_label_process(self, list_dict, count, index):
        if self.not_repeated_hour(index, list_dict) is not True:
            list_days = self.set_LMV_classes(count)
            count += 1
            self.check_repeated_hour_classes(index, list_dict, list_days)
        else:
            list_days = self.set_LMV_classes(count)
            count += 1
        return count

    def MJ_label_process(self, list_dict, count, index):
        if self.not_repeated_hour(index, list_dict) is not True:
            list_days = self.set_MJ_classes(count)
            count += 1
            self.check_repeated_hour_classes(index, list_dict, list_days)
        else:
            list_days = self.set_MJ_classes(count)
            count += 1
        return count

    def not_repeated_hour(self, index, list_dict):
        next = index + 1
        first_hour = self.dict['Hour']
        next_hour = list_dict[next]['Hour']
        state = False
        if first_hour != next_hour:
            state = True
        return state

    def check_repeated_hour_classes(self, index, list_dict, list_days):
            next = index + 1
            first_hour = self.dict['Hour']
            next_hour = list_dict[next]['Hour']
            day = self.dict['Day']
            if first_hour == next_hour and day == list_dict[next]['Day']:
                if list_days == 'Class of three hours':
                    three_hour = self.separate_hour_from_class(next_hour)
                    for hour in three_hour:
                        self.find_replace_repeated_data(hour, day, index)
                elif type(list_days) == list:
                    for day in list_days:
                        self.find_replace_repeated_data(next_hour, day, index)

    def find_replace_repeated_data(self, hour, day, index):
        spot = self.findChild(QHBoxLayout, f'{hour}_{day}')
        if self.changes_classes_in_comboBox > 1:
            label_spot = 0
            old_label = spot.itemAt(label_spot).widget()
            spot.removeWidget(old_label)
        label = self.set_label_in_schedule(index)
        spot.addWidget(label)

    def set_LMV_classes(self, color):
        """Set Monday, Wednesday and Friday classes"""
        days = self.dict['Day']
        hour = self.dict['Hour']
        days_list = [int(days[0]), int(days[1]), int(days[2])]
        for day in days_list:
            self.find_hour_replace_data(hour, day, color)
        return days_list

    def set_MJ_classes(self, color):
        """Set Tuesday and Thursday classes"""
        day = self.dict['Day']
        real_hour = self.dict['Hour']
        three_hour = self.separate_hour_from_class(real_hour)
        for hour in three_hour:
            self.find_hour_replace_data(hour, day, color)
        return 'Class of three hours'

    def separate_hour_from_class(self, hour):
        numeric_part = int(hour[1:])
        letter_part = str(hour[:1])
        next_numbers = [numeric_part, numeric_part+1, numeric_part+2]
        three_hour = [letter_part + str(num) for num in next_numbers]
        return three_hour

    def find_hour_replace_data(self, hour:str, day:str, color):
        # print(f'{hour}_{day}')
        spot = self.findChild(QHBoxLayout, f'{hour}_{day}')
        old_label = spot.itemAt(0).widget()
        spot.removeWidget(old_label)
        label = self.set_label_in_schedule(color)
        spot.addWidget(label)

    def clean_data_from_schedule(self):
        """Clean data from schedule"""
        for i in range(self.schedule_grid.count()):
            item = self.schedule_grid.itemAt(i)
            if item is not None:
                layout = item.layout()
                if layout is not None:
                    for j in range(layout.count()):
                        widget = layout.itemAt(j).widget()
                        if isinstance(widget, QLabel):
                            widget.setStyleSheet("")
                            widget.setText("")


################# ORDER CLASSES METHODS ##########################

    def _order_key(self, order_dict, dict):
        return order_dict[dict['Hour']]

    def order_classes_by_hour(self, list_dict):
        sorted_list = sorted(list_dict, key=lambda dict: self._order_key(self.rows, dict))
        return sorted_list

    def order_classes_by_day(self, list_dict):
        list_135 = []
        list_24 = []

        for dict in list_dict:
            if '135' in dict['Day']:
                list_135.append(dict)
            elif '2' in dict['Day'] or '4' in dict['Day']:
                list_24.append(dict)
        new_order = list_135 + list_24
        return new_order

    def order_classes(self, list_dict):
        list_by_hour = self.order_classes_by_hour(list_dict)
        list_by_day = self.order_classes_by_day(list_by_hour)
        return list_by_day

################# GRID METHODS ##########################

    def set_grid_dimmensions(self):
        factor = 1
        for column in self.columns.values():
            self.schedule_grid.setColumnStretch(column, factor)
        for row in self.rows.values():
            self.schedule_grid.setRowStretch(row, factor)



app = QApplication(sys.argv) 
window = IntroScreen() 
app.exec_() 