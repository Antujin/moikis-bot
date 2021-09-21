import csv
import datetime
import traceback

import gspread
from gspread.utils import rowcol_to_a1
import numpy as np
import requests
from gspread_formatting import *
import os
from dateutil import parser

border_fmt = Borders(top=Border('Solid'), bottom=Border('Solid'), right=Border('solid'), left=Border('solid'))
heading_format = cellFormat(borders=border_fmt,
                            textFormat=textFormat(bold=True, fontSize=14),
                            horizontalAlignment='CENTER'
                            )
Main_heading_format = cellFormat(borders=border_fmt,
                                 textFormat=textFormat(bold=True, fontSize=20),
                                 horizontalAlignment='CENTER'
                                 )
mythic_pref = {'1_': 'Mythic progress',
               '2_': 'Mythic OHNE progress',
               '3_': 'HC mit mythic farm',
               '4_': 'HC only'}
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
spec_role = {'Blood': 'Tank',
             'Unholy': 'Melee',
             'Frost1': 'Melee',
             'Havoc': 'Melee',
             'Vengeance': 'Tank',
             'Fury': 'Melee',
             'Arms': 'Melee',
             'Windwalker': 'Melee',
             'Mistweaver': 'Healer',
             'Brewmaster': 'Tank',
             'Balance': 'Range',
             'Restoration': 'Healer',
             'Restoration1': 'Healer',
             'Feral': 'Melee',
             'Guardian': 'Tank',
             'Protection': 'Tank',
             'Protection1': 'Tank',
             'Retribution': 'Melee',
             'Holy': 'Healer',
             'Holy1': 'Healer',
             'Subtlety': 'Melee',
             'Marksman': 'Range',
             'Beastmastery': 'Range',
             'Arcane': 'Range',
             'Frost': 'Range',
             'Demonology': 'Range',
             'Affliction': 'Range',
             'Discipline': 'Healer',
             'Shadow': 'Range',
             'Elemental': 'Range',
             'Enhancement': 'Melee',
             }
def read_data_from_api(event_id):
    result = {}
    url = f'http://51.195.103.14:3000/api/raids/{event_id}'
    auth_token = os.environ.get('RAIDHELPER_BEARER_TOKEN')
    headers = {'authorization': f'Bearer {auth_token}'}
    response = requests.get(url=url, headers=headers).json()
    print(response)
    #print(response.json()['raidusers'])
    raw_date = response['raids']['date']
    raw_time = response['raids']['time']
    date = datetime.datetime.strptime(raw_date + '+' + raw_time, '%d-%m-%Y+%H:%M')
    for user in response['raidusers']:
        result.update({user['userid']: {'class': user['spec'],
                                        #'spec': player_spec.replace('1', ''),
                                        'role': user['role'],
                                        'color': class_color[user['spec']],
                                        'name': user['username'].replace('**',''),
                                        'signup time': parser.parse(user['entrydate']),
                                        }
                       }
                       )
    return result, date

def read_csv_data(csv_file, event_id_Umfrage=None):
    result = {}
    with open(csv_file, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for i, line in enumerate(reader):
            if i == 0:
                continue
            elif i == 1:
                raw_date = line[1]
                raw_time = line[2]
                date = datetime.datetime.strptime(raw_date + '+' + raw_time, '%d-%m-%Y+%H:%M')
                continue
            elif i < 4:
                continue
            #print(i, line)
            response = line[0]
            player_class = line[1]
            player_name = line[2]
            player_id = line[3]
            signup_time = line[4]
            result.update({player_id: {'class': player_class,
                                       #'spec': player_spec.replace('1', ''),
                                       'role': response,
                                       'color': class_color[player_class],
                                       'mythic_pref': None,
                                       'name': player_name,
                                       'signup time': signup_time,
                                       }
                           }
                          )
    return result, date

def export_data_to_google(event_id):
    try:
        gc = gspread.service_account()
        #data, date = read_csv_data(event_id)
        data, date = read_data_from_api(event_id)
        sh = gc.open('Mah Oida Raidplanung')
        worksheet_old = sh.sheet1
        try:
            worksheet = sh.worksheet(title=f'Planung {date.strftime("%d.%m.%Y")}')#date + ' Kader')
            sh.del_worksheet(worksheet)
        except:
            pass
        worksheet = sh.add_worksheet(title=f'Planung {date.strftime("%d.%m.%Y")}', rows="50", cols="20")# rows="50", cols="20")

        #sh.del_worksheet(worksheet_old)
        upload_data = []
        worksheet_fmt = []

        tanks = []
        ranges = []
        healer = []
        melees = []
        absents = []
        tentatives = []
        benched = []
        lates = []
        fmt_dict = {}
        for i,key in enumerate(data.keys()):
            fmt = cellFormat(backgroundColor=data[key]['color'], borders=border_fmt)
            if data[key]['role'] == 'Tanks':
                tanks.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Healers':
                healer.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Ranged':
                ranges.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Melee':
                melees.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Absence':
                absents.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Tentative':
                tentatives.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Late':
                lates.append(data[key]['name'])
                fmt_dict.update({key: fmt})
            elif data[key]['role'] == 'Bench':
                benched.append(data[key]['name'])
                fmt_dict.update({key: fmt})
        output_size = (8, max([len(tanks), len(melees), len(healer), len(ranges), len(absents),len(lates), len(benched)])+1)
        output_data = np.full(output_size, fill_value='', dtype='U40').transpose()
        output_data[0, 0] = 'Tank'
        output_data[0, 1] = 'Heal'
        output_data[0, 2] = 'Range DD'
        output_data[0, 3] = 'Melee DD'
        output_data[0, 4] = 'Bench'
        output_data[0, 5] = 'Verspätet'
        output_data[0, 6] = 'Vorläufig'
        output_data[0, 7] = 'Abwesend'
        for i, tank in enumerate(tanks):
            output_data[i+1, 0] = tank
        for i, heal in enumerate(healer):
            output_data[i+1, 1] = heal
        for i, rang in enumerate(ranges):
            output_data[i+1, 2] = rang
        for i, melee in enumerate(melees):
            output_data[i+1, 3] = melee
        for i, bench in enumerate(benched):
            output_data[i + 1, 4] = bench
        for i, late in enumerate(lates):
            output_data[i + 1, 5] = late
        for i, tentative in enumerate(tentatives):
            output_data[i+1, 6] = tentative
        for i, absent in enumerate(absents):
            output_data[i+1, 7] = absent
        last_line = output_size[1]
        worksheet_fmt = []
        x = 1
        y = 2
        startcell = (x,y)
        worksheet_fmt = []
        for key in fmt_dict.keys():
            fmt = cellFormat(backgroundColor=data[key]['color'], borders=border_fmt)
            pos = np.where(output_data == data[key]['name'])
            #print(pos,data[key]['name'])
            worksheet_fmt.append((rowcol_to_a1(pos[0]+y, pos[1]+x), fmt))
        counter_line = np.full((1,output_size[0]), fill_value='', dtype='U40').transpose()
        for j in range(output_size[0]):
            counter_line[j,0]=(f'=COUNTUNIQUE({chr(j+65)}3:{chr(j+65)}{last_line+1})')


        #worksheet.update(rowcol_to_a1(y,x), output_data.tolist())

        pos = rowcol_to_a1(last_line+4,1)
        overview = [{
            'range': 'J1:J6',
            'values': [['Stand:'], ['Geliste Namen'], ['Angemeldet'], ['Eingeplant'], ['Bench'], ['Bilanz']],
        }, {
            'range':  rowcol_to_a1(y,x),
            'values': output_data.tolist(),
        }, {
            'range':  rowcol_to_a1(1,1),
            'values': [[f'Anmeldungen {date.strftime("%d.%m.%Y  %H:%M")} Uhr']],
        }, {
            'range': rowcol_to_a1(last_line+7,1),
            'values': [['Team Ketchup'], ['Tank', 'Healer', 'Ranged', 'Melee']]
        }, {
            'range': rowcol_to_a1(last_line+7,11),
            'values': [['Bench'], ['Tank', 'Healer', 'Ranged', 'Melee']]
        }, {
            'range': rowcol_to_a1(last_line + 8 +14, 1),
            'values': [[f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 1)}:{rowcol_to_a1(last_line + 8 + 13, 1)})',
                        f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 2)}:{rowcol_to_a1(last_line + 8 + 13, 2)})',
                        f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 3)}:{rowcol_to_a1(last_line + 8 + 13, 3)})',
                        f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 4)}:{rowcol_to_a1(last_line + 8 + 13, 4)})',
                        f'=SUM({rowcol_to_a1(last_line + 8 +14, 1)}: {rowcol_to_a1(last_line + 8 +14, 4)})']]
        }, {
            'range': rowcol_to_a1(last_line + 8 +14, 6),
            'values': [[f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 6)}:{rowcol_to_a1(last_line + 8 + 13, 6)})',
                        f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 7)}:{rowcol_to_a1(last_line + 8 + 13, 7)})',
                        f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 8)}:{rowcol_to_a1(last_line + 8 + 13, 8)})',
                        f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 9)}:{rowcol_to_a1(last_line + 8 + 13, 9)})',
                        f'=SUM({rowcol_to_a1(last_line + 8 +14, 6)}: {rowcol_to_a1(last_line + 8 +14, 9)})']]
        }, {
            'range': rowcol_to_a1(last_line+7,6),
            'values': [['Team Mayo'], ['Tank', 'Healer', 'Ranged', 'Melee']]
        }, {
            'range': 'K1:K6',
            'values': [[datetime.datetime.now().strftime('%d.%m %H:%M')],
                       [f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 1)}:{rowcol_to_a1(last_line + 8 + 13, 4)};A3:{chr(65+output_size[0]-1)}{last_line+3}; {rowcol_to_a1(last_line + 8 +1, 6)}:{rowcol_to_a1(last_line + 8 + 13, 9)}; {rowcol_to_a1(last_line + 8 +1, 11)}:{rowcol_to_a1(last_line + 8 + 13, 14)})'],
                       [f'=COUNTUNIQUE(A3:{chr(65+output_size[0]-2)}{last_line+3})'],
                       [f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 1)}:{rowcol_to_a1(last_line + 8 + 13, 4)}; {rowcol_to_a1(last_line + 8 +1, 6)}:{rowcol_to_a1(last_line + 8 + 13, 9)} )'],
                       [f'=COUNTUNIQUE({rowcol_to_a1(last_line + 8 +1, 11)}:{rowcol_to_a1(last_line + 8 + 13, 14)})'],
                       ['=K3-K4-K5']]
        }]
        worksheet.merge_cells(rowcol_to_a1(last_line+7,1)+':'+rowcol_to_a1(last_line+7,4))
        worksheet.merge_cells(rowcol_to_a1(last_line+7,6)+':'+rowcol_to_a1(last_line+7,9))
        worksheet.merge_cells(rowcol_to_a1(last_line+7,11)+':'+rowcol_to_a1(last_line+7,14))
        worksheet.merge_cells(rowcol_to_a1(1,1)+':'+rowcol_to_a1(1,output_size[0]))
        worksheet.batch_update(overview, value_input_option='USER_ENTERED',)
        worksheet.update(pos, counter_line.tolist(), raw=False, major_dimension='COLUMNS')

        worksheet_fmt.append((rowcol_to_a1(last_line+8,1)+':'+rowcol_to_a1(last_line+8,4),heading_format))
        worksheet_fmt.append((rowcol_to_a1(last_line+8,6)+':'+rowcol_to_a1(last_line+8,9),heading_format))
        worksheet_fmt.append((rowcol_to_a1(last_line+8,11)+':'+rowcol_to_a1(last_line+8,14),heading_format))
        worksheet_fmt.append((rowcol_to_a1(last_line+7,6),Main_heading_format))
        worksheet_fmt.append((rowcol_to_a1(last_line+7,11),Main_heading_format))
        worksheet_fmt.append((rowcol_to_a1(last_line+7,1),Main_heading_format))
        worksheet_fmt.append((rowcol_to_a1(1,1),Main_heading_format))
        worksheet_fmt.append((rowcol_to_a1(y,x)+':'+rowcol_to_a1(y,x+7),heading_format))
        format_cell_ranges(worksheet, worksheet_fmt)
        return ['OK', date, f'https://docs.google.com/spreadsheets/d/{sh.id}/edit#gid={worksheet.id}', worksheet.title]
    except Exception as e:
        traceback.print_exc()
        raise e


if __name__ == '__main__':
    r = export_data_to_google('862422922253041675')
    print(r)