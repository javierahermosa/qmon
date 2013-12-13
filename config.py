import os
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['javiereahermosa@yahoo.com'])
SECRET_KEY = '@#$^NOTRATIS$&^DEMETERTELOCOYU'

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = "HSJDAHSGDHAGY#T*Q*($()())"

login_serializer = URLSafeTimedSerializer(SECRET_KEY)

REMEMBER_COOKIE_NAME = 'qomon_remember'

REMEMBER_COOKIE_DURATION = timedelta(days=14)

#RECAPTCHA_USE_SSL = False
#RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
#RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
#RECAPTCHA_OPTIONS = {'theme': 'white'}

