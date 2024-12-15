import qrcode
import base64
from io import BytesIO

QR_CODE_PREFIX = "data:image/png;base64,"


def url_to_qr(url: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    return QR_CODE_PREFIX + base64.b64encode(buffered.getvalue()).decode("utf-8")
