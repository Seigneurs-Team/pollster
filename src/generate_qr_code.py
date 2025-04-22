import base64

import segno
import io


def generate_qr_code_of_link(url: str):
    qr_code = segno.make_qr(url)
    buffer_of_qr_code = io.BytesIO()
    qr_code.save(buffer_of_qr_code, kind='png', scale=8, border=7, dark="#05437c")
    qr_code_in_bytes = buffer_of_qr_code.getvalue()
    buffer_of_qr_code.close()

    return base64.b64encode(qr_code_in_bytes).decode()

