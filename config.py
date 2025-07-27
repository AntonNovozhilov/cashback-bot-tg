from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List

ADMIN_IDS = [448888074, 6446030996]

KANAL = -1002870140259 # Чат для общения с клиентами 
CHANNEL_ID_CASH = -1002083919862 # Канал с постром прайса кешбек
PRICE_MESSAGE_ID_CASH = 7 # Номер поста прайса кешбек
CHANNEL_ID_BARTER = -1002189663330 # Канал с постром прайса бартер
PRICE_MESSAGE_ID_BARTER = 3 # Номер поста прайса бартер
CHAT_ID = -1002650883546 # Айди чата в котором будет переписка
CHANNEL_INFO_MESSAGE = 178 # Айди сообщения про каналы
CHANNEL_ID_OFFER = -1002761328389 # Айди чата в котором будет пост для прайса вакансий
PRICE_MESSAGE_ID_OFFER = 4 # Айди сообщения про прайс вакансий



kb_price_text = '💲 Прайс'
kb_create_post_text = '🖊️ Создать пост'
kb_cannals_text = '📢 Наши каналы'
kb_faq_text = '❓ FAQ'
kb_requis_text = '🧾 Реквизиты'
kb_admin_text = '👩🏽‍💻 Админ'
kb_admin_pannel_text = 'Админка'
news = 'Сделать рассылку'

count_users_in_admin = 'Кол-во пользователей'
count_price_in_admin = 'Кол-во запросов прайса'
home = 'Выйти из меню админа'
TINKOFF = 5536913896706237
SBER = 2202206355968657

class Settings(BaseSettings):
    bot_token: str = Field(..., env='BOT_TOKEN')
    database_url: str = Field(..., env='DATABASE_URL')
    admin_ids: List[int] = Field(default_factory=list, env='ADMIN_IDS')
    POSTGRES_USER: str = Field(..., env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(..., env='POSTGRES_PASSWORD')
    POSTGRES_DATABASE: str = Field(..., env='POSTGRES_DATABASE')

    @field_validator("admin_ids", mode="before")
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(i.strip()) for i in v.split(",") if i.strip().isdigit()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Settings()



