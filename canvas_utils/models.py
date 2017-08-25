"""
Canvas API models
"""


class Collection:
    """
    Base collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        self._api = api
        self._url = url
        self._parent = parent
        self._model = lambda *x: None

    def all(self):
        """ get all data models """
        objects = self._api.get_all(self._url.format(''))
        return [
            self._model(obj, self._api, self._url, self._parent)
            for obj in objects
        ]

    def get(self, identifier):
        """ get data model by pk """
        obj = self._api.get(self._url.format(identifier)).json()
        return self._model(obj, self._api, self._url, self._parent)


class Accounts(Collection):
    """
    Account collection model
    """
    def __init__(self, api, url='', parent=None):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/accounts/{}'
        self._model = Account


class Courses(Collection):
    """
    Course collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/courses/{}'
        self._model = Course


class Modules(Collection):
    """
    Module collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/modules/{}'
        self._model = Module


class ModuleItems(Collection):
    """
    Module item collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/items/{}'
        self._model = ModuleItem


class Assignments(Collection):
    """
    Assignments collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/assignments/{}'
        self._model = Assignment


class Submissions(Collection):
    """
    Submission collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/submissions/{}'
        self._model = Submission


class Users(Collection):
    """
    User collection model
    """
    def __init__(self, api, url, parent):
        """ create instance """
        super().__init__(api, url, parent)
        self._url += '/users/{}'
        self._model = User


class Model:
    """
    Model base class
    """
    def __init__(self, json, api, parent):
        """ create instance """
        self._json = json
        self._api = api
        self._parent = parent
        self._url = lambda: None

    def __str__(self):
        """ overload """
        return '{}: {}'.format(self['id'], self['name'])

    def __repr__(self):
        """ overload """
        return str(self)

    def __getitem__(self, item):
        """ overload """
        return self._json[item]

    def json(self):
        """ for comfort """
        return self._json


class Account(Model):
    """
    Account model
    """
    def __init__(self, json, api, url, parent):
        """ create instance """
        super().__init__(json, api, parent)
        self._url = lambda: url.format(self['id'])
        self.courses = Courses(self._api, self._url(), self)


class Course(Model):
    """
    Course model
    """
    def __init__(self, json, api, _, parent):
        """ create instance """
        super().__init__(json, api, parent)
        self._url = lambda: '/courses/{}'.format(self['id'])
        self.modules = Modules(self._api, self._url(), self)
        self.assignments = Assignments(self._api, self._url(), self)
        self.users = Users(self._api, self._url(), self)


class Module(Model):
    """
    Module model
    """
    def __init__(self, json, api, url, parent):
        super().__init__(json, api, parent)
        self._url = lambda: url.format(self['id'])
        self.items = ModuleItems(self._api, self._url(), self)


class Assignment(Model):
    """
    Assignment model
    """
    def __init__(self, json, api, url, parent):
        """ create instance """
        super().__init__(json, api, parent)
        self._url = lambda: url.format(self['id'])
        self.submissions = Submissions(self._api, self._url(), self)


class Submission(Model):
    """
    Submission model
    """
    def __init__(self, json, api, url, parent):
        super().__init__(json, api, parent)
        self._url = lambda: url.format(self['id'])

    def __str__(self):
        return '{}: {} [{}]'.format(self['id'], self['user_id'], self['score'])


class User(Model):
    """
    User model
    """
    def __init__(self, json, api, url, parent):
        """ create instance """
        super().__init__(json, api, parent)
        self._url = lambda: url.format(self['id'])

    def __str__(self):
        """ overload """
        return '{}: {} {}'.format(self['id'], self['login_id'], self['name'])


class ModuleItem(Model):
    """
    Module item model
    """
    def __init__(self, json, api, url, parent):
        """ create instance """
        super().__init__(json, api, parent)
        self._url = lambda: url.format(self['id'])
        self._update_data = lambda: {'module_item': self._json}
        self.content = None

    def __str__(self):
        """ overload """
        return '{}: {}'.format(self['type'], self['title'])
