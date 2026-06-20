import os
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER'):
    from .base import *
else:
    from .base import *