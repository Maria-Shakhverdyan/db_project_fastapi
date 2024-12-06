import requests
from faker import Faker

API_URL = "http://localhost:3000"

fake = Faker()

def create_books(num_books):
    """
    Create books using Faker and add them to the database via REST API.
    
    Args:
        num_books (int): Number of books to create.
    """
    for _ in range(num_books):
        book_data = {
            "title": fake.sentence(nb_words=3),
            "author": fake.name(),
            "publisher": fake.company(),
            "topic": fake.word()
        }
        response = requests.post(f"{API_URL}/books/", json=book_data)
        if response.status_code == 200:
            print(f"Book created: {response.json()}")
        else:
            print(f"Error creating book: {response.status_code}, {response.text}")

def create_readers(num_readers):
    """
    Create readers using Faker and add them to the database via REST API.
    
    Args:
        num_readers (int): Number of readers to create.
    """
    for _ in range(num_readers):
        reader_data = {
            "name": fake.name(),
            "address": fake.address(),
            "phone": fake.phone_number()
        }
        response = requests.post(f"{API_URL}/readers/", json=reader_data)
        if response.status_code == 200:
            print(f"Reader created: {response.json()}")
        else:
            print(f"Error creating reader: {response.status_code}, {response.text}")

def populate_database(num_books, num_readers):
    """
    Populate the database with the specified number of books and readers.
    
    Args:
        num_books (int): Number of books to create.
        num_readers (int): Number of readers to create.
    """
    create_books(num_books)
    create_readers(num_readers)

if __name__ == "__main__":
    NUM_BOOKS = 50
    NUM_READERS = 20

    populate_database(NUM_BOOKS, NUM_READERS)