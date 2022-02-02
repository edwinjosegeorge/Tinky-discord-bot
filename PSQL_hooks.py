from sqlalchemy import create_engine, Column, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL
from difflib import SequenceMatcher


engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)
base = declarative_base()


class CollegeStudent(base):
    __tablename__ = 'college'

    name = Column(String(40), nullable=False)
    admn = Column(String(6), primary_key=True, nullable=False)
    branch = Column(String(2), nullable=False)
    year = Column(String(4), nullable=False)
    id = Column(String(20))

    def nameSimilarity(self, name: str) -> bool:
        # compare name for 80% similarity
        seq = SequenceMatcher(None, self.name, name.strip().upper())
        return float(seq.ratio()) > 0.8

    def __str__(self):
        return f"| {self.name} | {self.admn} | {self.branch} | {self.year} |"

    def __repr__(self):
        return self.__str__()


base.metadata.create_all(engine)


def DB_find(**kwargs):
    '''Searches the DB
        if count(result)=1 -> return CollegeStudent
        else return count
    '''

    for key in kwargs:
        kwargs[key] = str(kwargs[key]).upper().strip()

    with Session() as session:
        try:
            query = select(CollegeStudent).filter_by(**kwargs)
            result = session.execute(query).all()
            count = len(result)
            if count == 1:
                return result[0][0]
            return count
        except Exception as e:
            print(e)
            return 0


def DB_update(admn: str, name: str, id: str) -> bool:
    '''
    Modifies the 'id' field in the DB , returns true on success
    '''

    admn = admn.upper().strip()
    name = name.upper().strip()
    id = id.upper().strip()

    with Session() as session:
        try:
            if DB_find(id=id) != 0:
                raise ValueError(f"ID {id} is have already registered")

            query = select(CollegeStudent).filter_by(admn=admn)
            result = session.execute(query).all()
            count = len(result)
            if count != 1:
                raise ValueError(f"ADMN {admn} is not found")

            student = result[0][0]

            if student.id is not None:
                raise ValueError(
                    f"ADMN {student.admn} have already registered")
            if not student.nameSimilarity(name):
                raise ValueError(
                    f"Name {student.name} differs from name {name}")

            student.id = id
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
    return False


def DB_add(**kwargs):
    for key in kwargs:
        kwargs[key] = str(kwargs[key]).upper().strip()

    with Session() as session:
        try:
            item = CollegeStudent(**kwargs)
            session.add(item)

            # add multiple items
            # session.add_all([item1, item2, item3])

            session.commit()
        except Exception as e:
            print(e)
            session.rollback()


def DB_remove(**kwargs):
    for key in kwargs:
        kwargs[key] = str(kwargs[key]).upper().strip()

    with Session() as session:
        try:
            query = select(CollegeStudent).filter_by(**kwargs)
            for item in session.execute(query).all():
                session.delete(item[0])
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
