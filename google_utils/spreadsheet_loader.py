"""
Contains class updating google spreadsheet
"""
import argparse
import httplib2
import pytz
import os
from datetime import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class SpreadSheetLoader:
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    MAX_LETTER = ord('Z') + 1
    OFFSET_CHAR = ord('C')

    def __init__(self, client_secret_file, oauth_path):
        """
        Args:
            client_secret_file (str): путь до файла с токеном google
            oauth_path (str): путь до настроек google api
        """
        self._secret_file = client_secret_file
        self._oauth_path = oauth_path

    def upload(self, course_data, course_info):
        """
        Загружает данные об успеваемости курса в google spreadsheet

        Args:
            course_data (dict): словарь с данными курса
            course_info (dict): словарь настроек курса
        """
        # Получим из токена учетные данные, провалидируем, создадим клиент и прочие вещи
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        service = discovery.build(
            'sheets', 'v4', http=http, discoveryServiceUrl=discovery_url
        )

        # Полезно будет знать количество студентов
        students_count = len(course_data['users'])
        if 'student_order' in course_info:
            students_positions = dict(zip(
                course_info['student_order'],
                range(len(course_info['student_order']))
            ))
        else:
            students_positions = dict(zip(
                [r['id'] for r in course_data['users']],
                range(students_count),
            ))

        students_scores = []
        for assign in course_data['assignments']:
            # Изначально у всех 0 баллов
            _student_scores = [0] * students_count
            # Посмотрим чьи результаты у нас есть, и проставим их
            for as_res in assign['results']:
                # По идентификатору получим ID
                idx = students_positions.get(as_res['user_id'])
                if idx is not None:
                    # Возможно здесь может придти Null
                    _student_scores[idx] = as_res['score'] or 0

            students_scores.append(_student_scores)

        assignments_count = len(course_data['assignments'])
        students_offset = students_count + 4
        pos_increment = iter(range(len(students_positions), 2 ** 10))
        names = (
            user['name'] for user in sorted(
                course_data['users'],
                key=lambda x: students_positions[x['id']] if x['id'] in students_positions else next(pos_increment)
            )
        )

        timestamp = datetime.now().astimezone(pytz.timezone('Asia/Yekaterinburg'))
        offset = self.OFFSET_CHAR + assignments_count
        end_result_char = '{add}{char}'.format(
            add=chr(64 + offset // self.MAX_LETTER) if offset >= self.MAX_LETTER else '',
            char=chr(offset if offset < self.MAX_LETTER else offset - 26),
        )
        upload_data = {
            'header': {
                'range': 'B1:C2',
                'majorDimension': 'ROWS',
                'values': [
                    ['', 'Тесты:'],
                    ['Студенты:', '']
                ],
            },
            'students': {
                'range': 'B3:B{number}'.format(number=students_offset),
                'majorDimension': 'COLUMNS',
                'values': [list(names)]
            },
            'assignments': {
                'range': 'D1:{char}1'.format(
                    char=end_result_char
                ),
                'majorDimension': 'ROWS',
                'values': [
                    [a['name'] for a in course_data['assignments']]
                ],
            },
            'results': {
                'range': 'D3:{char}{number}'.format(
                    char=end_result_char,
                    number=students_offset,
                ),
                'majorDimension': 'COLUMNS',
                'values': students_scores,
            },
            'updated_at': {
                'range': 'B1',
                'majorDimension': 'ROWS',
                'values': [
                    ['Обновлено\n{!s}'.format(timestamp.strftime('%c'))]
                ]
            }
        }

        execute_result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=course_info['spreadsheet'],
            body={
                'valueInputOption': 'RAW',
                'includeValuesInResponse': False,
                'data': [{**v} for v in upload_data.values()],
            }
        ).execute()

        return len(execute_result['responses'])

    def _get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        # store = Storage(os.path.join(os.getcwd(), self._oauth_path))
        store = Storage(self._oauth_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self._secret_file, self.SCOPES)
            flow.user_agent = ""
            credentials = tools.run_flow(
                flow,
                store,
                argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            )
        return credentials
