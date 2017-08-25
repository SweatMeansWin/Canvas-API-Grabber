"""
Module contain class that do main job
"""
import json
import os

import config
from canvas_utils.api_client import CanvasAPIClient
from google_utils import SpreadSheetLoader


class CanvasInfoLoader:
    """
    Класс загрузчик данных с платформы Canvas
    """

    def __init__(self):
        """ Установим необходимые аттрибуты """
        self._conf = config.get()
        self._client = CanvasAPIClient(
            app_id=self._conf['app_id'],
            token=self._conf['token'],
        )
        self._out_dir = self._conf['output_directory']
        if self._out_dir and not os.path.exists(self._out_dir):
            os.mkdir(self._out_dir)
        self._loader = SpreadSheetLoader(
            client_secret_file=self._conf['google-api-token-path'],
            oauth_path=self._conf['google-api-oauth-storage-path'],
        )

    def reload_configuration(self):
        """ Обновим конфиг из файла """
        self._conf = config.get()

    def update_info(self):
        """ На основании конфигурации, обновим данные Canvas """
        for course_info in self._conf['courses']:
            print("{!s} has started".format(course_info['name']))
            try:
                course_data = self._get_course_data_by_id(course_info)
            except Exception as exc:
                print(
                    "Errors '{!s}': {!r}".format(
                        course_info['name'],
                        str(exc)
                    )
                )
                continue

            # Если есть директория сохранения, то выгрузим данные на диск
            if self._out_dir:
                with open(
                    file=os.path.join(self._out_dir, course_info['name'] + '.json'),
                    mode='w',
                    encoding='utf-8',
                ) as f:
                    json.dump(course_data, f)

            # Загрузим на гуглдок
            self._loader.upload(
                self._prettify_data(course_data),
                course_info,
            )
            print("{!s} has completed".format(course_info['name']))

    def _get_course_data_by_id(self, course_info):
        """
        Получает информацию о курсе: пользователи, тесты, сдачи

        Args:
            course_info (dict): информамция о курсе

        Returns:
            dict: данные в JSON
        """
        course_data = {}
        # Получим аккаунт администратора
        account = self._client.accounts.get(course_info['instructor_id'])
        # Из списка курсов получим нужный нам
        course = account.courses.get(course_info['id'])
        # Начинаем заполнять
        course_data['course_info'] = course.json()
        # Отфильтруем лишних пользователей
        course_data['users'] = list(filter(
            lambda u: u['id'] not in course_info['exclude_ids'],
            [u.json() for u in course.users.all()]
        ))
        # Получим тесты
        course_data['assignments'] = []
        for assignment in course.assignments.all():
            if any(
                [
                    x in assignment['name']
                    for x in (
                        'Instructor Use Only',
                        'с раздаточными материалами',
                    )
                ]
            ):
                continue
            course_data['assignments'].append(
                {
                    'assignments_info': assignment.json(),
                    'submissions': [
                        s.json() for s in assignment.submissions.all()
                    ]
                }
            )

        return course_data

    @staticmethod
    def _prettify_data(data):
        """
        Выберем только нужные данные

        Returns:
            dict: словарик
        """
        return {
            'id': data['course_info']['id'],
            'name': data['course_info']['name'],
            'users': [
                {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['login_id'],
                } for user in data['users']
            ],
            'assignments': [
                {
                    'name': assignment['assignments_info']['name'],
                    'results': [
                        {
                            'user_id': submission['user_id'],
                            'score': submission['score'],
                            'attempt': submission['attempt'],
                        } for submission in assignment.get('submissions', [])
                    ]
                } for assignment in data['assignments']
            ],
        }
