import gspread
import numpy as np
from gspread.utils import rowcol_to_a1
from gspread_formatting import *
import datetime
from gspread_pandas import Spread

role_id = {'Ranged DPS': 0,
           'Melee  DPS': 1,
           'Heiler': 2,
           'Tank': 3}
border_fmt = Borders(top=Border('Solid'), bottom=Border('Solid'), right=Border('solid'), left=Border('solid'))
no_border_fmt = Borders(top=Border('None'), bottom=Border('None'), right=Border('None'), left=Border('None'))
heading_format = cellFormat(borders=border_fmt,
                            textFormat=textFormat(bold=True, fontSize=14),
                            horizontalAlignment='CENTER'
                            )
Main_heading_format = cellFormat(borders=border_fmt,
                                 textFormat=textFormat(bold=True, fontSize=20),
                                 horizontalAlignment='CENTER'
                                 )
base_fmt = cellFormat(
    backgroundColor=color(1, 1, 1),
    borders=no_border_fmt,
    textFormat=textFormat(bold=False, fontSize=10),
    horizontalAlignment='LEFT',
    #backgroundColor=Color(1, 1, 1),
    )
class_color = {'Todesritter': Color(0.77, 0.12, 0.23),
               'Schamane': Color(0, 0.44, 0.87),
               'Demonhunter': Color(0.64, 0.19, 0.79),
               'Dämonenjäger': Color(0.64, 0.19, 0.79),
               'Krieger': Color(0.78, 0.61, 0.43),
               'Mönch': Color(0.33, 1, 0.52),
               'Druide': Color(1, 0.49, 0.04),
               'Paladin': Color(0.96, 0.55, 0.73),
               'Schurke': Color(1, 0.96, 0.41),
               'Jäger': Color(0.67, 0.83, 0.45),
               'Magier': Color(0.41, 0.8, 0.94),
               'Hexenmeister': Color(0.58, 0.51, 0.79),
               'Priester': Color(1, 1, 1),
               'Heilig Priester': Color(1, 1, 1),
               'Disziplin Priester': Color(1, 1, 1),
               'Absence': Color(0.5, 0.5, 0.5),
               }
Team = ['Ketchup only', 'Ketchup präferiert', 'Egal ob Ketchup/Mayo', 'Mayo präferiert', 'Mayo only']

def clear_sheet():
    sheet = Spread('9.1 Auswertung')
    sheet.clear_sheet(rows=100, cols=100)
    sheet.merge_cells(start='A1', end='D100')
    gc = gspread.service_account()
    sh_output = gc.open('9.1 Auswertung')
    worksheet_output = sh_output.sheet1
    format_cell_range(worksheet_output, 'A1', base_fmt)
    sheet.unmerge_cells()



def EvalPoll():
    gc = gspread.service_account()
    sh = gc.open('Mah Oida 9.1 Abfrage (Antworten)')
    worksheet = sh.worksheet(title='Formularantworten 1')
    sh_output = gc.open('9.1 Auswertung')
    worksheet_output = sh_output.sheet1
    list_of_dicts = worksheet.get_all_records()
    users = {}
    fmt_dict = {'': cellFormat()}
    for entry in list_of_dicts:
        name = entry['Char oder Discord name']
        role = entry['Welche Rolle willst du im Sanctum of Domination Mythic Raid primär ausfüllen?']
        if role == 'Ranged DPS':
            klasse = entry['Welchen Ranged DD willst du spielen?']
        elif role == 'Melee DPS':
            klasse = entry['Welchen Melee DD willst du spielen?']
        elif role == 'Tank':
            klasse = entry['Welche Klasse willst du spielen?']
        elif role == 'Heiler':
            klasse = entry['Welchen Heiler möchtest du spielen?']
        else:
            klasse = 'Absence'
        raidteam = entry['In welchem Raidteam willst du raiden? Wenn du "Nur Team Ketchup" bzw. "Nur Team Mayo" auswählst, werden wir dich für das jeweils andere Team nciht berücksichtigen. Die anderen Optionen sehen wir als Präferenzen.']

        fmt = cellFormat(backgroundColor=class_color[klasse], borders=border_fmt)
        if raidteam not in users.keys():
            users.update({raidteam: [{'name': name,
                                      'klasse': klasse,
                                      'role': role,
                                      'fmt': fmt}]})
        else:
            users[raidteam].append({'name': name,
                                    'klasse': klasse,
                                    'role': role,
                                    'fmt': fmt})
    result = []
    for i in range(5):
        ranges = []
        melees = []
        healer = []
        tanks = []
        for user in users[i+1]:
            if user['role'] == 'Ranged DPS':
                ranges.append([user['name'], user['fmt']])
            elif user['role'] == 'Melee DPS':
                melees.append([user['name'], user['fmt']])
            elif user['role'] == 'Healer':
                healer.append([user['name'], user['fmt']])
            elif user['role'] == 'Tank':
                tanks.append([user['name'], user['fmt']])
        output_size = (4, max([len(tanks), len(melees), len(healer), len(ranges)])+1)
        output_data = np.full(output_size, fill_value='', dtype='U40').transpose()
        output_data[0, 0] = 'Tank'
        output_data[0, 1] = 'Heal'
        output_data[0, 2] = 'Range DD'
        output_data[0, 3] = 'Melee DD'
        for j, tank in enumerate(tanks):
            output_data[j+1, 0] = tank[0]
            fmt_dict.update({output_data[j+1, 0]: tank[1]})
        for j, heal in enumerate(healer):
            output_data[j+1, 1] = heal[0]
            fmt_dict.update({output_data[j + 1, 1]: heal[1]})
        for j, rang in enumerate(ranges):
            output_data[j+1, 2] = rang[0]
            fmt_dict.update({output_data[j + 1, 2]: rang[1]})
        for j, melee in enumerate(melees):
            output_data[j+1, 3] = melee[0]
            fmt_dict.update({output_data[j + 1, 3]: melee[1]})
        result.append(output_data)
    last_line=0
    startcell = (1, 2)
    overview = []
    worksheet_fmt = []
    for k,res in enumerate(result):
        x = startcell[0]
        y = startcell[1] + last_line
        last_line += len(res)+2
        for i, line in enumerate(res):
            if i == 0:
                continue
            for j, elem in enumerate(line):
                if res[i, j] == '':
                    continue
                fmt = fmt_dict[res[i, j]]
                worksheet_fmt.append((rowcol_to_a1(i + y, j + x), fmt))

        overview.append({
            'range': rowcol_to_a1(y, x),
            'values': res.tolist(),
            })
        overview.append({
            'range': rowcol_to_a1(y-1,x),
            'values': [[Team[k]]]
        },)
        print(rowcol_to_a1(y-1, x) + ':' + rowcol_to_a1(y-1, x+3))
        worksheet_output.merge_cells(rowcol_to_a1(y-1, x) + ':' + rowcol_to_a1(y-1, x+3))
        worksheet_fmt.append((rowcol_to_a1(y, x) + ':' + rowcol_to_a1(y, x+3), heading_format))
        worksheet_fmt.append((rowcol_to_a1(y-1, x), Main_heading_format))

    worksheet_output.batch_update(overview, value_input_option='USER_ENTERED', )
    format_cell_ranges(worksheet_output, worksheet_fmt)
if __name__ == '__main__':
    clear_sheet()
    EvalPoll()


