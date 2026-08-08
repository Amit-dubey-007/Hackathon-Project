import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


def generate_qr(url):

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()

    img.save(
        buffer,
        format="PNG"
    )

    return ContentFile(
        buffer.getvalue(),
        "qr.png"
    )