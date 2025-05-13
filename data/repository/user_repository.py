from data.db_connection import DatabaseConnection
from data.models.user import User
from sqlalchemy import and_, func

db_connection = DatabaseConnection()

class UserRepository:
    def __init__(self):
        self.session = db_connection.engine_connection() 

    def user_create(self, user_create: User):
        self.session.add(user_create)
        self.session.commit()

    def get_user_by_email(self, email: str) -> User:
        return self.session.query(User).filter(and_(func.lower(User.Email) == func.lower(email), User.IsDeleted == False)).first()