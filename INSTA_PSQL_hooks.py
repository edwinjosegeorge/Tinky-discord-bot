from sqlalchemy import create_engine, Column, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL

engine = create_engine(DATABASE_URL.replace("postgres", "postgresql"))
Session = sessionmaker(engine)
base = declarative_base()


class Instagram(base):
    __tablename__ = 'instagram'

    username = Column(String(20), primary_key=True, nullable=False)
    recent_post = Column(String(20), nullable=False)


base.metadata.create_all(engine)


def DB_find_all():
    '''
    Searches the DB, returns a list of usernames
    '''
    rtn_list = list()
    with Session() as session:
        try:
            query = select(Instagram)
            result = session.execute(query).all()
            for row in result:
                rtn_list.append(row[0].username)
            return rtn_list
        except Exception as e:
            print(e)
            return rtn_list


def DB_find(username):
    '''
    Searches the DB, returns recent_post if found
    '''
    with Session() as session:
        try:
            query = select(Instagram).filter_by(username=username)
            result = session.execute(query).all()
            if len(result) != 1:
                return None
            return result[0][0].recent_post
        except Exception as e:
            print(e)
            return None


def DB_update_id(username, post_id) -> bool:
    """
    Update post_id of user in DB
    return True on success
    """
    with Session() as session:
        try:
            query = select(Instagram).filter_by(username=username)
            result = session.execute(query).all()
            if len(result) != 1:
                return False
            result[0][0].recent_post = post_id
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
    with Session() as session:
        try:
            item = Instagram(**kwargs)
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

    with Session() as session:
        try:
            query = select(Instagram).filter_by(**kwargs)
            for item in session.execute(query).all():
                session.delete(item[0])
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False
