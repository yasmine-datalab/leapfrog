"""Note model"""
from schemas import Note as NoteBase

from .document import DocumentBase


class Note(DocumentBase, NoteBase):
    """Notes class"""

    class Settings:
        """Database setting"""

        name = "note"
