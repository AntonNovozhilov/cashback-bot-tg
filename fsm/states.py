# fsm/states.py

from aiogram.fsm.state import StatesGroup, State

class Post(StatesGroup):
    post_type = State()          # resume / vacancy
    role = State()               # кто ты или кого ищешь
    contact_choice = State()     # выбор — свой username или ввести вручную
    contact_custom = State()     # ручной ввод контакта

    # Для резюме:
    about_you = State()          # о себе
    services = State()           # описание услуг
    cases = State()              # кейсы/преимущества

    # Для вакансии:
    about_company = State()      # о компании
    position = State()           # описание должности
    requirements = State()       # требования

    photo = State()              # фотографии (или skip)
    confirm = State()            # подтверждение перед отправкой
