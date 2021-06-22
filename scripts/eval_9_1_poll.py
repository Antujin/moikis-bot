import gspread
from gspread.utils import rowcol_to_a1
from gspread_formatting import *

class_color = {'DK': Color(0.77, 0.12, 0.23),
               'Shaman': Color(0, 0.44, 0.87),
               'DH': Color(0.64, 0.19, 0.79),
               'Warrior': Color(0.78, 0.61, 0.43),
               'Monk': Color(0.33, 1, 0.52),
               'Druid': Color(1, 0.49, 0.04),
               'Paladin': Color(0.96, 0.55, 0.73),
               'Rogue': Color(1, 0.96, 0.41),
               'Hunter': Color(0.67, 0.83, 0.45),
               'Mage': Color(0.41, 0.8, 0.94),
               'Warlock': Color(0.58, 0.51, 0.79),
               'Priest': Color(1, 1, 1),
               'Absence': Color(0.5, 0.5, 0.5),
               }

def EvalPoll():
    gc = gspread.service_account()
    sh = gc.open('Mah Oida 9.1 Abfrage (Antworten)')
    worksheet = sh.worksheet(title='Formularantworten 1')
    name_list = worksheet.col_values(2)
    print(len(name_list), name_list)


if __name__ == '__main__':
    EvalPoll()


