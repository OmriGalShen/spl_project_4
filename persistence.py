import atexit
import sqlite3
import dto
import dbtools

# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('grades.db')
        self.students = dbtools.Dao(dto.Student,self._conn)
        self.assignments = dbtools.Dao(dto.Assignment,self._conn)
        self.grades = dbtools.Dao(dto.Grade,self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE students (
            id      INT         PRIMARY KEY,
            name    TEXT        NOT NULL
        );

        CREATE TABLE assignments (
            num                 INT     PRIMARY KEY,
            expected_output     TEXT    NOT NULL
        );

        CREATE TABLE grades (
            student_id      INT     NOT NULL,
            assignment_num  INT     NOT NULL,
            grade           INT     NOT NULL,

            FOREIGN KEY(student_id)     REFERENCES students(id),
            FOREIGN KEY(assignment_num) REFERENCES assignments(num),

            PRIMARY KEY (student_id, assignment_num)
        );
    """)


# the repository singleton
repo = _Repository()
atexit.register(repo._close)