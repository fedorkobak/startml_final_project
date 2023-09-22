from sqlalchemy import (
    desc,
    func
)
from sqlalchemy.orm import Session
from fastapi import (
    FastAPI, 
    Depends,
    HTTPException
)
from typing import List

from schema import (
    UserGet,
    PostGet,
    FeedGet
)
from database import SessionLocal
from table_user import User
from table_post import Post
from table_feed import Feed

app = FastAPI()

def get_db():
    with SessionLocal() as db:
        return db

@app.get("/user/{id}", response_model=UserGet)
def get_user(id:int, db: Session = Depends(get_db)):
    response = db.query(User).filter(User.id == id).one_or_none()

    if response is None:
        print(response is None)
        raise HTTPException(404, f"No user with id {id}")

    return response

@app.get("/post/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    response = db.query(Post).filter(Post.id == id).one_or_none()

    if response is None:
        print(response is None)
        raise HTTPException(404, f"No post with id {id}")

    return response

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_feeds_by_user(id:int, limit = 10, db : Session = Depends(get_db)):
    return (
        db.query(Feed).
        filter(Feed.user_id == id).
        order_by(desc(Feed.time)).
        limit(limit).
        all()
    )

@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_feed_by_post(id:int, limit = 10, db : Session = Depends(get_db)):
    return (
        db.query(Feed).
        filter(Feed.post_id == id).
        order_by(desc(Feed.time)).
        limit(limit).
        all()
    )

@app.get("/post/recommendations/", response_model = List[PostGet])
def get_recommendations(id:int, limit = 10, db : Session = Depends(get_db)):
    return (
        db.query(Post).
        join(Feed).
        filter(Feed.action == "like").
        group_by(Post.id).
        order_by(desc(func.count())).
        limit(limit).
        all()
    )