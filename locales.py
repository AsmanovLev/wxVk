"""
    All locales for the wxVk
"""

from locale import getdefaultlocale


def get_locale(language: str) -> dict:
    """ Returns locale dict based on given language. """
    if language in LOCALES:
        return LOCALES[language]
    return LOCALES[FALLBACK_LANGUAGE]


FALLBACK_LANGUAGE = "en_US"
LOCALES = {
    "en_US": {
        "quit": "Quit",
        "login": "Login",
        "password": "Password",
        "gettoken": "Get token",
        "token": "Token",
        "enter_credentials" : "Enter your credentials",
        "sumbit" : "Sumbit",
        '2fa' : "Enter 2FA code",
        "tryauth": "Trying to authorize...",
        "success" : "Success!",
        "error" : "Error",
        "badpass": "Wrong password",
        "savecreds": "Remember credentials",
        "loading": "Loading",
        "messages":"Messages"
    },
    "ru_RU": {
        "quit": "Выйти",
        "login": "Логин",
        "password": "Пароль",
        "gettoken": "Получить токен",
        "token": "Токен",
        "enter_credentials": "Введите учетные данные",
        "sumbit": "Подтвердить",
        "2fa": "Введите 2FA код",
        "tryauth": "Пытаюсь авторизоваться...",
        "success": "Успешно!",
        "error": "Ошибка",
        "badpass": "Неверный пароль",
        "savecreds": "Запомнить учетные данные",
        "loading": "Загрузка",
        "messages": "Сообщения"
    }
}

_OSLANGUAGE, _ = getdefaultlocale()
locale = get_locale(_OSLANGUAGE)
del getdefaultlocale