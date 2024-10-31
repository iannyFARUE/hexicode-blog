from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query,status
from sqlmodel import Field, SQLModel,create_engine, select,Session
from passlib.context import CryptContext


class BlogBase(SQLModel):
    title: str = Field(index = True)
    description: str
    
class Blog(BlogBase, table=True):
    id: Union[int,None] = Field(default=None,primary_key=True)
    published: Union[bool,None]
    
class BlogPublic(BlogBase):
    id:int
    
class BlogCreate(BlogBase):
    published: Union[bool,None]
    

class BlogUpdate(BlogBase):
    title: Union[str,None]  = None
    description: Union[str,None]  = None
    published: Union[bool,None]  = None
    
class UserBase(SQLModel):
    username: str 
    email: str
    fullname: Union[str,None]
    
class User(UserBase, table=True):
    password:str
    id:int = Field(default=None,primary_key=True)
    disabled: Union[bool,None]
    
class UserPublic(UserBase):
    id:int

class UserCreate(UserBase):
    disabled: bool = Field(default=True)
    password:str
    
    
### Hashing utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

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

@app.get('/blogs', response_model=list[BlogPublic])
def read_blogs(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    blogs = session.exec(select(Blog).offset(offset).limit(limit)).all()
    return blogs

@app.get('/blogs/{blog_id}', response_model=BlogPublic)
def read_blog(blog_id: int,session: SessionDep):
    blog= session.get(Blog,blog_id)
    if not blog:
        raise HTTPException(status_code=404,detail="Blog not found")
    return  blog


@app.post('/blogs', response_model=BlogPublic, status_code=status.HTTP_201_CREATED)
def create_blog(blog: BlogCreate,session:SessionDep):
    db_blog = Blog.model_validate(blog)
    session.add(db_blog)
    session.commit()
    session.refresh(db_blog)
    return db_blog

@app.delete("/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(blog_id: int, session: SessionDep):
    blog = session.get(Blog,blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    session.delete(blog)
    session.commit()
    return {'ok':True}

@app.patch("/blogs/{blog_id}", response_model=BlogPublic)
def update_hero(blog_id: int, blog: BlogUpdate, session: SessionDep):
    blog_db = session.get(Blog,blog_id)
    if not blog_db:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog_data = blog.model_dump(exclude_unset=True)
    blog_db.sqlmodel_update(blog_data)
    session.add(blog_db)
    session.commit()
    session.refresh(blog_db)
    return blog_db


@app.post("/users",response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session:SessionDep):
    db_user = User.model_validate(user)
    hashedPassword = get_password_hash(db_user.password)
    new_user = User(username=db_user.username, email=db_user.email,password=hashedPassword, fullname=db_user.fullname,disabled=db_user.disabled)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user




