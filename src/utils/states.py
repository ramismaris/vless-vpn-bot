from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Состояния для админ панели"""
    waiting_broadcast_message = State()
    waiting_user_id = State()


class UserStates(StatesGroup):
    """Состояния для пользователей"""
    waiting_feedback = State()
    waiting_order_data = State() 