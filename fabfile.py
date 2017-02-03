from fabric.api import local

def init_db():
    local('python manage.py init_db')

def test():
    local('py.test tests')
