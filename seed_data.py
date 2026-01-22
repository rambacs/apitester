import os
from enum import Enum
from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from passlib.context import CryptContext


class Base(DeclarativeBase):
    pass


class Status(Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    COMPLETE = "Complete"


class User(Base):
    __tablename__ = "profile"
    __table_args__ = (UniqueConstraint("username"),)
    id = mapped_column(Integer, primary_key=True)
    username: Mapped[str]
    hashed_password: Mapped[str]
    email: Mapped[Optional[str]]
    full_name: Mapped[Optional[str]]
    disabled: Mapped[Optional[bool]]
    tasks: Mapped[List["Task"]] = relationship()


class Task(Base):
    __tablename__ = "task"
    id = mapped_column(Integer, primary_key=True)
    description: Mapped[str]
    status: Mapped[Status]
    created_by: Mapped[int] = mapped_column(ForeignKey("profile.username"))


def create_password_hash(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def seed_database():
    uri = os.getenv("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Check if data already exists
    existing_users = db.scalars(select(User)).all()
    if existing_users:
        print(f"Database already has {len(existing_users)} users. Skipping seed.")
        db.close()
        return
    
    # Create test users
    users_data = [
        ("admin", "Admin User", "admin@example.com", "admin123"),
        ("johndoe", "John Doe", "john@example.com", "password123"),
        ("janedoe", "Jane Doe", "jane@example.com", "password123"),
        ("testuser", "Test User", "test@example.com", "test123"),
        ("qaengineer", "QA Engineer", "qa@example.com", "qa12345"),
    ]
    
    for username, full_name, email, password in users_data:
        user = User(
            username=username,
            hashed_password=create_password_hash(password),
            email=email,
            full_name=full_name,
            disabled=False,
        )
        db.add(user)
    
    db.commit()
    print(f"Created {len(users_data)} users")
    
    # Create test tasks
    tasks_data = [
        ("Set up test environment", Status.COMPLETE, "admin"),
        ("Write API test cases for GET endpoints", Status.COMPLETE, "johndoe"),
        ("Write API test cases for POST endpoints", Status.IN_PROGRESS, "johndoe"),
        ("Review authentication flow", Status.IN_PROGRESS, "janedoe"),
        ("Create Postman collection", Status.COMPLETE, "qaengineer"),
        ("Set up Newman for CI/CD", Status.IN_PROGRESS, "qaengineer"),
        ("Document API endpoints", Status.DRAFT, "admin"),
        ("Performance testing plan", Status.DRAFT, "janedoe"),
        ("Security testing checklist", Status.DRAFT, "testuser"),
        ("Bug fix: login validation", Status.IN_PROGRESS, "testuser"),
        ("Integrate with Jenkins", Status.DRAFT, "qaengineer"),
        ("Write negative test cases", Status.COMPLETE, "johndoe"),
    ]
    
    for description, status, created_by in tasks_data:
        task = Task(description=description, status=status, created_by=created_by)
        db.add(task)
    
    db.commit()
    print(f"Created {len(tasks_data)} tasks")
    
    db.close()
    print("Seed complete!")


if __name__ == "__main__":
    seed_database()
