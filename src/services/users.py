from src.schemas.users import UserCreate, UserIn, UserResponse, UserCreate, UserWithHashedPassword
from src.services.base import BaseServices
from src.services.auth import AuthServices
from src.utils.exceptions.exceptions import BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, UserNotFoundException, UsersUniquessException

class UserService(BaseServices):
    async def create_user(self, user_data: UserIn) -> UserResponse:
        hashed_password = AuthServices.get_password_hash(user_data.password)
        new_user_data = UserCreate(**user_data.model_dump(), hashed_password=hashed_password)
        
        try:
            user = await self.db.users.add(new_user_data)
        except BookingRoomsObjUniquessException:
            raise UsersUniquessException
        
        await self.db.commit()
        return user
    
    async def get_user_with_password(self, *args, **kwargs) -> UserWithHashedPassword:
        try:
            return await self.db.users.get_user_with_hashed_password(*args, **kwargs)
        except UserNotFoundException:
            raise UserNotFoundException
    
    async def get_user(self, *args, **kwargs) -> UserResponse:
        try:
            return await self.db.users.get_one(*args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise UserNotFoundException