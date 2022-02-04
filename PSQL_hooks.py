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
    '''
    Searches the DB, returns the list of CollegeStudent objects
    '''
    for key in kwargs:
        kwargs[key] = str(kwargs[key]).strip().upper()

    with Session() as session:
        rtn_list = list()
        try:
            query = select(CollegeStudent).filter_by(**kwargs)
            result = session.execute(query).all()
            for row in result:
                rtn_list.append(row[0])
            return rtn_list
        except Exception as e:
            print(e)
            return list()


def DB_update_id(admn: str, id) -> bool:
    """
    Update id of an admn in DB
    return True on success
    """
    admn = admn.strip().upper()
    with Session() as session:
        try:
            query = select(CollegeStudent).filter_by(admn=admn)
            result = session.execute(query).all()
            count = len(result)
            if count == 0:
                raise ValueError(f"ADMN {admn} is not found")

            student = result[0][0]
            student.id = id
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False


def DB_add(**kwargs) -> bool:
    """
    Add new instances into DB
    return True on sucess
    """
    for key in kwargs:
        kwargs[key] = str(kwargs[key]).upper().strip()

    with Session() as session:
        try:
            item = CollegeStudent(**kwargs)
            session.add(item)

            # add multiple items
            # session.add_all([item1, item2, item3])

            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False


def DB_remove(**kwargs) -> bool:
    """
    Remove record(s) from DB if found
    return True on success
    """

    for key in kwargs:
        kwargs[key] = str(kwargs[key]).upper().strip()
    with Session() as session:
        try:
            query = select(CollegeStudent).filter_by(**kwargs)
            for item in session.execute(query).all():
                session.delete(item[0])
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False
