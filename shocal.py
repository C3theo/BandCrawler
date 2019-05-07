"""
Shocal App Creation.
"""

from app import shocal, db
from app.models import Artist, Track, Concert

@shocal.shell_context_processor
def make_shell_context():
    return {'db': db, 'Concert': Concert, 'Artist': Artist, 'Track': Track}