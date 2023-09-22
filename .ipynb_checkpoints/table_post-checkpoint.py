from sqlalchemy import (
    Column,
    Integer,
    String,
    desc
)

from database import (
    Base, 
    SessionLocal
)

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key = True)
    text = Column(String)
    topic = Column(String)

if __name__ == "__main__":
    lst = (
        SessionLocal().
        query(Post).
        filter(Post.topic=="business").
        order_by(desc(Post.id)).
        limit(10).
        all()
    )
    print([p.id for p in lst])