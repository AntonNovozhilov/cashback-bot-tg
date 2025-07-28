from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    username = State()


class BaseSellerTitle(StatesGroup):
    """Базовый класс с продавцом и заголовком."""

    seller = State()
    title = State()
    photo = State()


class Post(StatesGroup):
    """Пост."""

    post_type = State()
    role = State()
    contact_choice = State()
    contact_custom = State()
    about_you = State()
    services = State()
    cases = State()
    about_company = State()
    position = State()
    requirements = State()
    photo = State()
    confirm = State()


class PostBarter(BaseSellerTitle):
    """Класс для составления поста в бартере."""

    money = State()
    web = State()
    descriptions = State()


class PostCachback(BaseSellerTitle):
    """Класс для составления поста в кешбеке."""

    market = State()
    price_before = State()
    price_after = State()
    discount = State()


class NewsPost(StatesGroup):
    """Пост для рассылки."""

    text = State()
    confirm = State()
