from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return {
        'data':{'name':'Ian'}
    }

@app.get('/about')
def about():
    return {
        'data':'This is new'
    }