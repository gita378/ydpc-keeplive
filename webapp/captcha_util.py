"""图形验证码"""
import random
import string
import io
import base64
from flask import session

try:
    from captcha.image import ImageCaptcha
    HAS_IMAGE_CAPTCHA = True
except ImportError:
    HAS_IMAGE_CAPTCHA = False


def generate_captcha() -> dict:
    """生成验证码，返回 {"text": "提示文字", "image": "base64 data URI 或 None"}"""
    chars = "".join(random.choices(string.digits, k=4))
    session["_captcha_answer"] = chars

    if HAS_IMAGE_CAPTCHA:
        gen = ImageCaptcha(width=160, height=60)
        buf = io.BytesIO()
        gen.write(chars, buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return {"text": None, "image": f"data:image/png;base64,{b64}"}
    else:
        # 降级为数学题
        a, b = random.randint(1, 20), random.randint(1, 20)
        session["_captcha_answer"] = str(a + b)
        return {"text": f"{a} + {b} = ?", "image": None}


def verify_captcha(user_input: str) -> bool:
    answer = session.pop("_captcha_answer", None)
    if not answer:
        return False
    return user_input.strip() == answer
