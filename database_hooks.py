from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL


def DB_find(TableClass, **kwargs) -> list:
    '''
    Searches the Database using kwargs parameters
    Returns a list of TableClass objects
    TableClass must be subclass of sqlalchemy.orm.decl_api.DeclarativeMeta
    '''
    engine = create_engine(DATABASE_URL.replace("postgres", "postgresql"))
    Session = sessionmaker(engine)
    session = Session()
    try:
        query = select(TableClass)
        if len(kwargs) != 0:
            query = query.filter_by(**kwargs)

        result = session.execute(query).all()
        session.close()
        return [row[0] for row in result]

    except Exception as e:
        print("Exception at database_hooks.DB_find :", e)
        return list()


def DB_update(TableClass, oldRec: dict, newRec: dict) -> bool:
    '''
    Update the Database Table oldRec to newRec
    Returns True on success
    TableClass must be subclass of sqlalchemy.orm.decl_api.DeclarativeMeta
    '''
    engine = create_engine(DATABASE_URL.replace("postgres", "postgresql"))
    Session = sessionmaker(engine)
    session = Session()
    try:
        query = select(TableClass)
        if len(oldRec) != 0:
            query = query.filter_by(**oldRec)

        result = session.execute(query).all()
        for row in result:
            obj = row[0]
            for key in newRec:
                obj.__setattr__(key, newRec[key])

        session.commit()
        session.close()
        return True
    except Exception as e:
        print("Exception at database_hooks.DB_update :", e)
        session.rollback()
        session.close()
        return False


def DB_add(TableClass, **kwargs) -> bool:
    '''
    Add new record into Database Table
    Returns True on success
    TableClass must be subclass of sqlalchemy.orm.decl_api.DeclarativeMeta
    '''
    engine = create_engine(DATABASE_URL.replace("postgres", "postgresql"))
    Session = sessionmaker(engine)
    session = Session()
    try:
        obj = TableClass(**kwargs)
        session.add(obj)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print("Exception at database_hooks.DB_add :", e)
        session.rollback()
        session.close()
        return False


def DB_remove(TableClass, **kwargs) -> bool:
    '''
    Searches the Database using kwargs parameters and then deletes them
    Returns a list of TableClass objects
    TableClass must be subclass of sqlalchemy.orm.decl_api.DeclarativeMeta
    '''
    engine = create_engine(DATABASE_URL.replace("postgres", "postgresql"))
    Session = sessionmaker(engine)
    session = Session()
    try:
        query = select(TableClass)
        if len(kwargs) != 0:
            query = query.filter_by(**kwargs)

        result = session.execute(query).all()
        for row in result:
            session.delete(row[0])
        session.commit()
        session.close()
        return True
    except Exception as e:
        print("Exception at database_hooks.DB_remove :", e)
        return False
