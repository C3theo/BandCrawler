"""
Shocal App Creation.
"""

from app import shocal, db
from app.models import Catalog

@shocal.shell_context_processor
def make_shell_context():
    return {'db': db, 'Catalog': Catalog}