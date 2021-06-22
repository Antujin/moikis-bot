import gspread
from gspread.utils import rowcol_to_a1
from gspread_formatting import *
role_id = {'Ranged DPS': 0,
           'Melee  DPS': 1,
           'Heiler': 2,
           'Tank': 3}
border_fmt = Borders(top=Border('Solid'), bottom=Border('Solid'), right=Border('solid'), left=Border('solid'))
heading_format = cellFormat(borders=border_fmt,
                            textFormat=textFormat(bold=True, fontSize=14),
                            horizontalAlignment='CENTER'
                            )
Main_heading_format = cellFormat(borders=border_fmt,
                                 textFormat=textFormat(bold=True, fontSize=20),
                                 horizontalAlignment='CENTER'
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

def EvalPoll():
    gc = gspread.service_account()
    sh = gc.open('Mah Oida 9.1 Abfrage (Antworten)')
    worksheet = sh.worksheet(title='Formularantworten 1')
    list_of_dicts = worksheet.get_all_records()
    users = {}
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
        users.update({raidteam: {'name': name,
                                 'klasse': klasse,
                                 'fmt': fmt}})
    print(users)

if __name__ == '__main__':
    EvalPoll()


