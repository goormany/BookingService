from src.schemas.users import UserCreate, UserIn, UserResponse, UserCreate, UserRoleSchema, UserWithHashedPassword
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
    
    async def get_all(self) -> list[UserResponse]:
        return await self.db.users.get_all()
    
    async def change_user_role(self, user_id: int, role: UserRoleSchema) -> UserResponse:
        try:
            user = await self.db.users.edit(role, True, id=user_id)
        except BookingRoomsNotFoundObjException:
            raise UserNotFoundException
        await self.db.commit()
        return user
    
    async def soft_delete(self, user_id: int) -> UserResponse:
        try:
            user = await self.db.users.soft_delete(user_id)
        except BookingRoomsNotFoundObjException:
            raise UserNotFoundException
        await self.db.commit()
        return user

    async def hard_delete(self, user_id: int) -> UserResponse:
        try:
            user = await self.db.users.delete(id=user_id)
        except BookingRoomsNotFoundObjException:
            raise UserNotFoundException
        await self.db.commit()
        return user

    async def restore_user(self, user_id: int) -> UserResponse:
        try:
            user = await self.db.users.restore(user_id)
        except BookingRoomsNotFoundObjException:
            raise UserNotFoundException
        await self.db.commit()
        return user