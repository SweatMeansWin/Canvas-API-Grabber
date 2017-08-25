Base class for access to Canvas test platform.
You will get access to courses, users and assignments data with Canvas API token and upload it to Google spreadsheets.

Base configuration file expected by '%projectdir%/files/canvas_conf.json'
(You may change it in 'config/utils.py' constants

Config (JSON file) body:
```python
{
    app_id (int): Canvas App ID
    courses (list[dict]): [
        {
            id (int): Course Id
            name (str): Convenient course name
            instructor_id (int): Course admin user id
            exclude_ids (list[int]): Ignored students user id
            spreadsheet (str): Google spreadsheet id
            student_order (list[int]): Students order in which return data, can be None
        },
    ],
    output_directory (str): Output save path, can be None
    token (str): Canvas Access token
    google-api-token-path (str): File path to google API Access token
    google-api-oauth-storage-path (str): File path to google Oauth storage json
}
```

How to update google spreadsheet every hour (using crontab):
```console
    sudo docker build -t canvas-updater .
    sudo crontab -e
        @hourly docker run canvas-updater
```
