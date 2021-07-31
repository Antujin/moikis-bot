import os
import requests
import datetime
import json


def read_data_from_api(event_id, raidhelper_token=None):
    result = {}
    answers = {}
    url = f'http://51.195.103.14:3000/api/raids/{event_id}'
    auth_token = raidhelper_token or os.environ.get('RAIDHELPER_BEARER_TOKEN')
    print(auth_token)
    headers = {'authorization': f'Bearer {auth_token}'}
    response = requests.get(url=url, headers=headers).json()
    print(response)
    raw_date = response['raids']['date']
    raw_time = response['raids']['time']
    date = datetime.datetime.strptime(raw_date + '+' + raw_time, '%d-%m-%Y+%H:%M')
    description = response['raids']['description']
    question, answers_list = description.split('=')
    for i, answer in enumerate(answers_list.split(',')):
        answers.update({chr(65+i): {'text': answer,
                                    'count': 0,
                                    'voters': []
                                    }})
    for user in response['raidusers']:
        vote = user['spec'][0]
        answers[vote]['voters'].append(user['username'].replace('**', ''))
        answers[vote]['count'] += 1
    return question, answers, len(response['raidusers'])


if __name__ == '__main__':
    print(read_data_from_api(870049755277979658, raidhelper_token='FPjSDr38ed9j3iD923jDS'))
