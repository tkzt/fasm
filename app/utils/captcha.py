import base64
from captcha.image import ImageCaptcha

CAPTCHA_PREFIX = "data:image/png;base64,"


def gen_captcha(chars: str):
    image_captcha = ImageCaptcha()
    return CAPTCHA_PREFIX + base64.b64encode(
        image_captcha.generate(chars).read()
    ).decode("utf-8")
