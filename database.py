from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from settings import DATABASE_URL
from difflib import SequenceMatcher

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


class Instagram(base):
    __tablename__ = 'instagram'

    username = Column(String(20), primary_key=True, nullable=False)
    recent_post = Column(String(20), nullable=False)


def initialize():
    engine = create_engine(DATABASE_URL.replace("postgres", "postgresql"))
    base.metadata.create_all(engine)
