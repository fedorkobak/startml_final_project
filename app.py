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
    '''
    Returns using the database session.
    '''
    with SessionLocal() as db:
        return db

@app.get("/user/{id}", response_model=UserGet)
def get_user(id:int, db: Session = Depends(get_db)):
    '''
    Get record from table user by id.
    
    Parameters
    -------------
    id : int
        id of the user;
    db : Session 
        sqlalchemy connection session.

    Returns
    ------------
    If passed id exists - instance of the User class.
    If there is no id passed in the user table, an HTTPException
    with status 404 is thrown.
    '''
    response = db.query(User).filter(User.id == id).one_or_none()

    if response is None:
        print(response is None)
        raise HTTPException(404, f"No user with id {id}")

    return response

@app.get("/post/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    '''
    Get record from table post by id.

    Parameters
    --------------
    id : int
        id of the post;
    db : Session
        Describes connection to the database.
    '''
    response = db.query(Post).filter(Post.id == id).one_or_none()

    if response is None:
        print(response is None)
        raise HTTPException(404, f"No post with id {id}")

    return response

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_feeds_by_user(id:int, limit = 10, db : Session = Depends(get_db)):
    '''
    Returns the freashest feeds for a given user.

    Parameters
    --------------
    id : int
        id of the user;
    limit : int
        how many actions to show (if any).

    Returns
    --------------
    List of feeds.
    '''
    return (
        db.query(Feed).
        filter(Feed.user_id == id).
        order_by(desc(Feed.time)).
        limit(limit).
        all()
    )

@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_feeds_by_post(id:int, limit = 10, db : Session = Depends(get_db)):
    '''
    Returns the freashest feeds for a given post.

    Parameters
    --------------
    id : int
        id of the post;
    limit : int
        how many actions to show (if any).

    Returns
    --------------
    List of feeds.
    '''
    return (
        db.query(Feed).
        filter(Feed.post_id == id).
        order_by(desc(Feed.time)).
        limit(limit).
        all()
    )

@app.get("/post/recommendations/", response_model = List[PostGet])
def get_recommendations(id:int, limit = 10, db : Session = Depends(get_db)):
    '''
    Aparently it's a plug for model results. 
    But at the moment it returns some number 
    of the most popular (by likes) posts.

    Parameters
    --------------
    id : int
        id of the user?;
    limit : int
        how many posts to show (if any).

    Returns
    --------------
    List of posts.
    '''
    return (
        db.query(Post).
        join(Feed).
        filter(Feed.action == "like").
        group_by(Post.id).
        order_by(desc(func.count())).
        limit(limit).
        all()
    )