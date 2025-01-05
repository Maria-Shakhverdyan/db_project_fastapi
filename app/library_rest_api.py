from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
import os
import uvicorn
from fastapi.templating import Jinja2Templates
from models import Book, Reader, Loan

from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

templates = Jinja2Templates(directory="ui")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    topic: str

class ReaderCreate(BaseModel):
    name: str
    address: str
    phone: str

class LoanCreate(BaseModel):
    reader_id: int
    book_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("library_ui.html", {"request": request})

@app.post("/loans/", response_class=JSONResponse)
def issue_book(loan: LoanCreate, db: Session = Depends(get_db)):
    try:
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not available")

        reader = db.query(Reader).filter(Reader.id == loan.reader_id).first()
        if not reader:
            raise HTTPException(status_code=404, detail="Reader not found")

        new_loan = Loan(book_id=book.id, reader_id=reader.id)
        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)
        return {"message": "Book issued successfully", "loan": new_loan}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/readers/", response_class=JSONResponse)
def create_reader(reader: ReaderCreate, db: Session = Depends(get_db)):
    try:
        new_reader = Reader(
            name=reader.name,
            address=reader.address,
            phone=reader.phone
        )
        db.add(new_reader)
        db.commit()
        db.refresh(new_reader)
        return {"message": "Reader added successfully", "reader": new_reader}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/readers/", response_class=JSONResponse)
def read_readers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    readers = db.query(Reader).offset(skip).limit(limit).all()
    return readers

@app.post("/books/", response_class=JSONResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    try:
        existing_book = db.query(Book).filter(Book.title == book.title).first()
        if existing_book:
            raise HTTPException(status_code=400, detail="Book with this title already exists")
        new_book = Book(
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            topic=book.topic
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return {"message": "Book added successfully", "book": new_book}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books/", response_class=JSONResponse)
def read_books(skip: int = 0, limit: int = 10, order_by: str = "title", ascending: bool = True, db: Session = Depends(get_db)):
    query = db.query(Book)
    if order_by in ["title", "author", "publisher", "topic"]:
        query = query.order_by(getattr(Book, order_by).asc() if ascending else getattr(Book, order_by).desc())
    books = query.offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=BookCreate)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=BookCreate)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    try:
        existing_book = db.query(Book).filter(Book.id == book_id).first()
        if existing_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        existing_book.title = book.title
        existing_book.author = book.author
        existing_book.publisher = book.publisher
        existing_book.topic = book.topic
        db.commit()
        db.refresh(existing_book)
        return existing_book
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        db.delete(book)
        db.commit()
        return {"detail": "Book deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/readers/{reader_id}")
def delete_reader(reader_id: int, db: Session = Depends(get_db)):
    try:
        reader = db.query(Reader).filter(Reader.id == reader_id).first()
        if reader is None:
            raise HTTPException(status_code=404, detail="Reader not found")

        loans = db.query(Loan).filter(Loan.reader_id == reader_id).all()
        for loan in loans:
            db.delete(loan)
        db.delete(reader)
        db.commit()
        return {"detail": "Reader deleted successfully and loans removed"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# SELECT с несколькими условиями
@app.get("/books/search/", response_class=JSONResponse)
def search_books(author: str = Query(None), topic: str = Query(None), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(Book)
    if author:
        query = query.filter(Book.author == author)
    if topic:
        query = query.filter(Book.topic == topic)
    books = query.offset(skip).limit(limit).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found with given criteria")
    return books

# JOIN для получения деталей о займах
@app.get("/loans/details/", response_class=JSONResponse)
def get_loan_details(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    loans = db.query(Loan).join(Book, Loan.book_id == Book.id).join(Reader, Loan.reader_id == Reader.id).offset(skip).limit(limit).all()
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found")
    return loans

# UPDATE с нетривиальным условием для обновления издателя
@app.put("/books/update_publisher/")
def update_books_publisher(book_id: int, new_publisher: str, db: Session = Depends(get_db)):
    try:
        book_to_update = db.query(Book).filter(Book.id == book_id).first()
        if not book_to_update:
            raise HTTPException(status_code=404, detail="Book not found with the given ID")
        book_to_update.publisher = new_publisher
        db.commit()
        return {"detail": "Book updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# GROUP BY для подсчета количества книг по темам
@app.get("/books/count_by_topic/", response_class=JSONResponse)
def count_books_by_topic(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    count_by_topic = db.query(Book.topic, func.count(Book.id)).group_by(Book.topic).offset(skip).limit(limit).all()
    if not count_by_topic:
        raise HTTPException(status_code=404, detail="No books found")
    return count_by_topic

if __name__ == "__main__":
    uvicorn.run("library_rest_api:app", host="127.0.0.1", port=3000, reload=True)
