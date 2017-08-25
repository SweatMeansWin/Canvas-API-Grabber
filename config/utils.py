"""
Содержит методы работы с конфигурацией
"""
import json
import os


CONFIGURATION_DIRECTORY = 'files'
CONFIGURATION_FILENAME = 'canvas_conf.json'
_conf_path = os.path.join(CONFIGURATION_DIRECTORY, CONFIGURATION_FILENAME)


class ConfigFileError(Exception):
    pass


_necessary_fields_info = (
    ('app_id', int),
    ('courses', list),
    ('token', str),
    ('google-api-token-path', str),
    ('google-api-oauth-storage-path', str),
)


def _validate(config_data):
    """
    Проверим, что в файле всего хватает

    Args:
        config_data (dict): данные конфигурации

    Raises:
        ConfigFileError: неправильный формат файла конфигурации
    """
    _fields = []
    for (_field, _type) in _necessary_fields_info:
        if _field not in config_data:
            _fields.append('Отсутствует обязательное поле {}'.format(_field))
        elif not isinstance(config_data[_field], _type):
            _fields.append('Неверный тип поля {}: ({}, ожидается {})'.format(
                _field,
                str(type(config_data[_field])),
                str(_type),
            ))
    if _fields:
        raise ConfigFileError(
            '\n'.join(_fields)
        )


def get():
    """
    Returns:
        dict: настройки формата:
            app_id (int): идентификатор приложения
            courses (list[dict]): [
                {
                    id (int): идентификатор курса
                    name (str): название курса
                    instructor_id (int): идентификатор администратора курса
                    exclude_ids (list[int]): идентификаторы пользователей, чьи данные не нужны
                    spreadsheet (str): идентификатор гугл таблицы
                    student_order (list[int]): в определенных случаях нам нужен определенный порядок студентов
                }, ...
            ],
            output_directory (str): путь сохранения файлов курсов
            token (str): строковое значение токена canvas
            google-api-token-path (str): путь до файла с токеном google api
            google-api-oauth-storage-path (str): путь до файла с данными oauth google api

    Raises:
        FileNotFoundError: файл отсутствует
        ConfigFileError: ошибка чтения/отсутствие обязательных полей
    """
    try:
        f = open(_conf_path)
    except FileNotFoundError:
        raise FileNotFoundError("{} file not found".format(_conf_path))

    try:
        _data = json.loads(f.read())
    except json.decoder.JSONDecodeError:
        raise ConfigFileError("Config file bad format")

    _validate(_data)
    return _data
