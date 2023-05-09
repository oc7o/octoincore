import random
import string
import typing
import uuid
from io import BytesIO

import strawberry
from captcha.image import ImageCaptcha
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Captcha

# # generate the image of the given text
# data = image.generate(captcha_text)

# # write the image on the given file and save it
# image.write(captcha_text, "CAPTCHA.png")


def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


@strawberry.django.type(model=Captcha)
class CaptchaType:
    web_id: str
    image: str


@strawberry.type
class CaptchaMutation:
    @strawberry.mutation
    def create_captcha(self, info) -> CaptchaType:
        web_id = uuid.uuid4().hex[:16]

        image = ImageCaptcha(width=280, height=90)
        captcha_text = randomword(6)
        data = image.generate_image(captcha_text)
        buffer = BytesIO()
        data.save(fp=buffer, format="PNG")
        image_file = ContentFile(buffer.getvalue())
        # image_file = File(name=f"{captcha_text}.png", file=ContentFile(buffer.getvalue()))

        obj = Captcha.objects.create(
            web_id=web_id,
            captcha=captcha_text,
            image=InMemoryUploadedFile(
                image_file,
                None,
                f"{web_id}.png",
                "image/png",
                image_file.size,
                None,
            ),
        )

        return CaptchaType(
            web_id=obj.web_id,
            image=info.context.request.build_absolute_uri(obj.image.url),
        )

    @strawberry.mutation
    def submit_captcha(self, info, web_id: str, captcha_text: str) -> bool:
        captcha = Captcha.objects.get(web_id=web_id)
        submit = True
        if captcha.captcha != captcha_text:
            return False
        captcha.delete()

        return submit
