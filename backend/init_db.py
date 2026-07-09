from app.database import engine, Base
from app.models import HCP, Interaction

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")

if __name__ == "__main__":
    init_database()