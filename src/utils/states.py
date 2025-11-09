from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    answer = State()
    day_correct = State()
    add_tariff_name = State()
    add_tariff_days = State()
    add_tariff_price = State()
    tariff_edit_values = State()


class UserStates(StatesGroup):
    pay_sum = State()
    waiting_order_data = State() 