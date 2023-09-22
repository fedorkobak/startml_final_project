from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP
)
from sqlalchemy.orm import relationship

from database import (
    Base,
    SessionLocal
)

from table_user import User
from table_post import Post

class Feed(Base):
    __tablename__ = "feed_action"
    #id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id"),
        primary_key=True,
    )
    user = relationship(User)
    
    post_id = Column(
        Integer,
        ForeignKey("post.id"),
        primary_key=True,
    )
    post = relationship(Post)
    
    action= Column(String)
    time = Column(TIMESTAMP)

if __name__ == "__main__":
    lst = SessionLocal().query(Feed.user_id).limit(10).all()
    print([l.user_id for l in lst])