from database import Database

# Инициализация базы данных
db = Database('database.db')

def create_referral(user_id):
    # Сохранение кода в базе данных для пользователя
    referral_code = user_id  # Используем user_id как реферальный код  

    # Возвращение кода для использования в ссылке
    return referral_code

def get_referral_link(user_id):
    referral_link = f"https://t.me/AnonymousAsksBot?start={user_id}"
    return referral_link

def get_referral(referral_code):
    # Получение пользователя по реферальному коду (в данном случае это user_id)
    return db.get_user_by_id(referral_code)
