from aiogram.fsm.state import State, StatesGroup

class AddProductState(StatesGroup):
    category = State()
    image = State()
    name = State()
    description = State()
    price = State()
    stock = State()

class EditStockState(StatesGroup):
    product_id = State()
    new_stock = State()

class EditPriceState(StatesGroup):
    product_id = State()
    new_price = State()

class CheckoutState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()
    waiting_for_receipt = State()

class AddCategoryState(StatesGroup):
    name = State()

class BroadcastState(StatesGroup):
    waiting_for_message = State()
