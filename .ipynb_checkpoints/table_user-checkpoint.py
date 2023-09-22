from sqlalchemy import (
    Column,
    Integer,
    String,
    func, 
    desc
)

from database import Base, SessionLocal

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    gender = Column(Integer)
    age = Column(Integer)
    country = Column(String)
    city = Column(String)
    exp_group = Column(Integer)
    os = Column(String)
    source = Column(String)

if __name__ == "__main__":
    lst = (
        SessionLocal().
        query(User.country, User.os, func.count()).
        filter(User.exp_group == 3).
        group_by(User.country, User.os).
        order_by(desc(func.count())).
        having(func.count() > 100).
        all()
    )
    print([u for u in lst])