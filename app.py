import pickle
import numpy as np
import pandas as pd
from datetime import datetime
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
from database import SessionLocal, engine
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


# This is loading precomputed data about the post text.
# For all posts performed tfidf transformation.
# ORM doesn't used here because sometimes list of used
# tfidf features can be changed.
post_data = pd.read_sql(
    "SELECT * FROM public.kobfedsur_post_features_lesson_22;",
    con = engine,
    index_col= "post_id"
)
post_data.index.name = "id"
# this is the model of the project
model = pickle.load(open("model/model.pck","rb"))

@app.get("/post/recommendations/", response_model = List[PostGet])
def get_recommendations(
        id:int, 
        time: datetime,
        limit:int = 10, db : Session = Depends(get_db)
    )-> List[PostGet]:
    '''
    Calls a model that returns best recommendations 
    for the user who has passed.

    Parameters
    --------------
    id : int
        id of the user?;
    time : datetime
        when user asks information;
    limit : int
        how many posts to show (if any).

    Returns
    --------------
    List of posts.
    '''
    user = db.query(User).filter(User.id == id).one_or_none()
    
    model_input = post_data.drop("text", axis = 1).copy()
    model_input["age"] = user.age
    model_input["country"] = user.country
    model_input["city"] = user.city
    model_input["exp_group"] = user.exp_group
    model_input["gender"] = user.gender
    model_input["os"] = user.os
    model_input["source"] = user.source
    model_input["month"] = time.month
    model_input["year"] = time.year
    model_input["hour"] = time.hour
    model_input["exp_group"] = model_input["exp_group"].astype("O")
    model_input["gender"] = model_input["gender"].astype("O")
    
    
    # use model to get probabilities that
    # user will like a particular post
    pred = model.predict_proba(
        model_input[model.feature_names_]
    )[:,1]
    
    # getting ids of posts with biggest probabilities
    posts = post_data.index[np.argsort(pred)[-limit:]]
    
    return (
        post_data.loc[posts, ["topic", "text"]].
        reset_index().apply(
            lambda row: row.to_dict(), axis = 1
        ).to_list()
    )