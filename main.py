from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, SQLModel,create_engine, select,Session


class Blog(SQLModel, table=True):
    id: Union[int,None] = Field(default=None,primary_key=True)
    title: str = Field(index = True)
    description: str
    published: Union[bool,None]

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.get('/blogs')
def read_blogs(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[Blog]:
    blogs = session.exec(select(Blog).offset(offset).limit(limit)).all()
    return blogs

@app.get('/blogs/{blog_id}')
def read_blog(blog_id: int,session: SessionDep):
    blog= session.get(Blog,blog_id)
    if not blog:
        raise HTTPException(status_code=404,detail="Blog not found")
    return  blog


@app.post('/blogs')
def create_blog(blog: Blog,session:SessionDep)-> Blog:
    session.add(blog)
    session.commit()
    session.refresh(blog)
    return blog

@app.delete("/blogs/{blog_id}")
def delete_hero(blog_id: int, session: SessionDep):
    blog = session.get(Blog,blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    session.delete(blog)
    session.commit()
    return {'ok':True}

