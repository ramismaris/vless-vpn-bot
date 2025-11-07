from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    answer = State()
    day_correct = State()
    add_tariff_name = State()
    add_tariff_days = State()
    add_tariff_price = State()


class UserStates(StatesGroup):
    """Состояния для пользователей"""
    waiting_feedback = State()
    waiting_order_data = State() 