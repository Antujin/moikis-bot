import gspread
import os



def publishsheets(sheet_name):
    try:
        created_sheet = False
        gc = gspread.service_account()
        input_sh = gc.open('Mah Oida Raidplanung')
        worksheet = input_sh.worksheet(title=sheet_name)
        publish_name = sheet_name.replace('Planung', 'Kader')
        try:
            output_sh = gc.open(publish_name)
        except:
            owner_mail = os.environ.get('OWNER_MAIL')
            output_sh = gc.create(publish_name)
            output_sh.share(owner_mail, perm_type='user', role='writer')
            created_sheet = True

        new_ws = worksheet.copy_to(output_sh.id)
        output_sh.del_worksheet(output_sh.sheet1)
        new_worksheet = output_sh.worksheet(new_ws['title'])
        new_worksheet.update_title(publish_name)
        output_sh.share(None, 'anyone', role='reader', with_link=True)
        response = ['OK', f'https://docs.google.com/spreadsheets/d/{output_sh.id}/edit#gid={new_worksheet.id}']
    except Exception as e:
        response = 'Error'
        print(e)
    return response


if __name__ == '__main__':
    print(publishsheets('Planung 21.03.2021'))
