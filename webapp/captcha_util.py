"""简单数学验证码（不依赖 PIL/captcha 库）"""
import random
from flask import session


def generate_captcha() -> str:
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    session["_captcha_answer"] = str(a + b)
    return f"{a} + {b} = ?"


def verify_captcha(user_input: str) -> bool:
    answer = session.pop("_captcha_answer", None)
    if not answer:
        return False
    return user_input.strip() == answer
