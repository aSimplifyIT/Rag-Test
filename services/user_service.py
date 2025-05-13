from data.repository.user_repository import UserRepository
from data.models.user import User
from common.Requests.user_create import UserCreate
from common.Responses.user_read import UserRead
from common.utils import Utils
from automapper import mapper
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from uuid import UUID
import jwt
import os

load_dotenv()

user_repository = UserRepository()
utils = Utils()

class UserService:
    def user_create(self, user_create_request: UserCreate) -> UserRead:
        user_model = mapper.to(User).map(user_create_request)
        user_model = User(
            FirstName = user_create_request.first_name,
            LastName = user_create_request.last_name,
            PasswordHash = utils.password_secure(user_create_request.password),
            Email = user_create_request.email
        )
        user_repository.user_create(user_model)
        user_read = UserRead(
            id = user_model.Id,
            first_name = user_model.FirstName,
            last_name = user_model.LastName,
            email = user_model.Email
        )
        return user_read

    def check_user_exist(self, email: str) -> bool:
        user = user_repository.get_user_by_email(email)
        return user is not None

    def get_user_by_email(self, email: str) -> User:
        return user_repository.get_user_by_email(email)

    def verify_login_user(self, user: User, password: str) -> bool:
        if user is None:
            return False
        else:
            return utils.password_verify(password, user.PasswordHash)

    def generate_jwt_token(self, user_id: UUID, email: str, first_name: str, last_name: str) -> str:
        try:
            SECRET_KEY = os.getenv("SECRET")  
            ALGORITHM = os.getenv("ALGORITHM")
            payload = {
                'user_id': str(user_id),
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'exp': datetime.now(timezone.utc) + timedelta(days=int(os.getenv("EXPIRE")))
                }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            return token
        
        except Exception as e:
            print("JWT Encoding Error:", str(e))
            return None
        