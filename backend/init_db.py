from database import Base, engine
from models.customer import Customer

Base.metadata.create_all(bind=engine)

print("Database created successfully.")