"""User roles"""

from enum import Enum


class Roles(str, Enum):
    """roles enum"""

    STUDENT = "Student"
    INSTRUCTOR = "Instructor"
    STAFF = "Staff"
    ADMIN = "Administrator"
