from PIL import Image
import PIL.ImageFile
from io import BytesIO
from pathlib import Path
from django.core.files import File
from django.utils import timezone
from datetime import timedelta


PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True


AVERAGE_CHARACTERS_PER_WORD = 4.7


def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency
    # (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (
            im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL
        # (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im


def image_resize(image, width, height, transparency_remove=True,
                 fit_in_center=False):
    """
    https://blog.soards.me/posts/resize-image-on-save-in-django-before-sending-to-amazon-s3/
    """

    # Open the image using Pillow
    img = Image.open(image)
    img = img.convert("RGBA")
    # check if either the width or height is greater than the max
    if img.width > width or img.height > height:
        output_size = (width, height)
        # Create a new resized “thumbnail” version of the image with Pillow
        img.thumbnail(output_size)
        if fit_in_center:
            new_image = Image.new(
                "RGBA",
                (width, height),
                (255, 255, 255),
            )
            new_image.paste(
                img,
                ((width - img.width) // 2,
                 (height - img.height) // 2),
            )
            img = new_image
        if transparency_remove:
            img = remove_transparency(img)
        # Find the file name of the image
        img_filename = Path(image.file.name).name
        # Save the resized image into the buffer, noting the correct file type
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        # Wrap the buffer in File object
        file_object = File(buffer)
        # Save the new resized file as usual, which will save to S3 using
        # django-storages
        image.save(img_filename, file_object)


def seven_days_from_now():
    return timezone.now() + timedelta(days=7)
