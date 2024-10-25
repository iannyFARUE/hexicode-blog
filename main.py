from typing import Optional
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return {
        'data':{'name':'Ian'}
    }

@app.get('/blog')
def index(limit=40,published: bool = True, sort: Optional[str]=None):
    if published:
        return {
            'data':f'50 from database'
        }
    else:
        return {'data':f'{limit} from DB in else'}


@app.get('/blog/unpublished')
def unpublished():
    return {
        'data': 'Unplished type'
    }

@app.get('/blog/{id}')
def show(id: int):
    # fetch blog with id = id
    return {
        'data':id
    }

@app.get("/blog/{id}/comments")
def comment(id:int):
    # fetch comments of blog by id = id
    return {'id':{'id':id}}


@app.post('/blog')
def create_blog():
    return {'data':'Post created'}
