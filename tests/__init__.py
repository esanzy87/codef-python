import os
from .. import InvokerFactory


# Environment Variables
CLIENT_ID = os.environ.get('CODEF_CLIENT_ID', 'ef27cfaa-10c1-4470-adac-60ba476273f9')
CLIENT_SECRET = os.environ.get('CODEF_CLIENT_SECRET', '83160c33-9045-4915-86d8-809473cdf5c3')
BASE_URL = os.environ.get('CODEF_BASE_URL', 'https://sandbox.codef.io')
PUBLIC_KEY = os.environ.get('CODEF_PUBLIC_KEY', 'MIIX1qwe34')
BANKING_USERID = '12345'
BANKING_PASSWORD = '12345'


invoker_factory = InvokerFactory(CLIENT_ID, CLIENT_SECRET, BASE_URL, PUBLIC_KEY)
