from sqlalchemy import select
from db.models import User

async def get_user_from_db(session, telegram_id):
    user_id = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user_id = user_id.scalar()
    return user_id