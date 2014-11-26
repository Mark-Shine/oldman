#encoding=utf-8
from __future__ import unicode_literals,absolute_import, division
from future.builtins import int, open, str


from collections import defaultdict

from django.core.urlresolvers import reverse
from django.template.defaultfilters import linebreaksbr, urlize
from django import forms


from hashlib import md5
from json import loads
import os
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode, quote, unquote
except ImportError:
    from urllib import urlopen, urlencode, quote, unquote

from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse, resolve, NoReverseMatch
from django.db.models import Model, get_model
from django.template import (Context, Node, TextNode, Template,
    TemplateSyntaxError, TOKEN_TEXT, TOKEN_VAR, TOKEN_COMMENT, TOKEN_BLOCK)
from django.template.defaultfilters import escape
from django.template.loader import get_template
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.text import capfirst
from django import template

from django.conf import settings
# from mezzanine.conf import settings
# from mezzanine.core.fields import RichTextField
# from mezzanine.core.forms import get_edit_form
# from mezzanine.utils.cache import nevercache_token, cache_installed
# from mezzanine.utils.html import decode_entities
# from mezzanine.utils.importing import import_dotted_path
# from mezzanine.utils.sites import current_site_id, has_site_permission
# from mezzanine.utils.urls import admin_url
# from mezzanine.utils.views import is_editable
# from mezzanine import template
register = template.Library()


@register.simple_tag
def resize_thumbnail(image_url, width, height,
              quality=95, left=.5, top=.5, padding=False):
    """
    Given the URL to an image, resizes the image using the given width and
    height on the first time it is requested, and returns the URL to the new
    resized image. if width or height are zero then original ratio is
    maintained.
    """

    if not image_url:
        return ""
    try:
        from PIL import Image, ImageFile, ImageOps
    except ImportError:
        return ""


    image_url = unquote(str(image_url)).split("?")[0]
    if image_url.startswith(settings.MEDIA_URL):
        image_url = image_url.replace(settings.MEDIA_URL, "", 1)
    image_dir, image_name = os.path.split(image_url)
    image_prefix, image_ext = os.path.splitext(image_name)
    filetype = {".png": "PNG", ".gif": "GIF"}.get(image_ext, "JPEG")
    thumb_name = "%s-%sx%s" % (image_prefix, width, height)
    if left != .5 or top != .5:
        left = min(1, max(0, left))
        top = min(1, max(0, top))
        thumb_name = "%s-%sx%s" % (thumb_name, left, top)
    thumb_name += "-padded" if padding else ""
    thumb_name = "%s%s" % (thumb_name, image_ext)

    thumb_dir_name = "thumbs-%s" % image_name
    thumb_dir_path = os.path.join(settings.MEDIA_ROOT, image_dir,
                                  settings.THUMBNAILS_DIR_NAME, thumb_dir_name)
    if not os.path.exists(thumb_dir_path):
        print (thumb_dir_path)
        os.makedirs(thumb_dir_path)
    thumb_path = os.path.join(thumb_dir_path, thumb_name)
    thumb_url = "%s/%s/%s" % (settings.THUMBNAILS_DIR_NAME,
                              quote(thumb_dir_name.encode("utf-8")),
                              quote(thumb_name.encode("utf-8")))
    image_url_path = os.path.dirname(image_url)
    if image_url_path:
        thumb_url = "%s/%s" % (image_url_path, thumb_url)

    try:
        thumb_exists = os.path.exists(thumb_path)
    except UnicodeEncodeError:
        # The image that was saved to a filesystem with utf-8 support,
        # but somehow the locale has changed and the filesystem does not
        # support utf-8.
        from mezzanine.core.exceptions import FileSystemEncodingChanged
        raise FileSystemEncodingChanged()
    if thumb_exists:
        # Thumbnail exists, don't generate it.
        return thumb_url
    elif not default_storage.exists(image_url):
        # Requested image does not exist, just return its URL.
        return image_url

    f = default_storage.open(image_url)
    try:
        image = Image.open(f)
    except:
        # Invalid image format
        return image_url

    image_info = image.info
    to_width = int(width)
    to_height = int(height)
    from_width = image.size[0]
    from_height = image.size[1]

    # If already right size, don't do anything.
    if to_width == from_width and to_height == from_height:
        return image_url
    # Set dimensions.
    if to_width == 0:
        to_width = from_width * to_height // from_height
    elif to_height == 0:
        to_height = from_height * to_width // from_width
    if image.mode not in ("P", "L", "RGBA"):
        image = image.convert("RGBA")
    # Required for progressive jpgs.
    ImageFile.MAXBLOCK = 2 * (max(image.size) ** 2)

    # Padding.
    if padding and to_width and to_height:
        from_ratio = from_width / from_height
        to_ratio = to_width / to_height
        pad_size = None
        if to_ratio < from_ratio:
            pad_size = (from_width, int(to_height * (from_width / to_width)))
            pad_top = (pad_size[1] - from_height) // 2
            pad_left = 0
        elif to_ratio > from_ratio:
            pad_size = (int(to_width * (from_height / to_height)), from_height)
            pad_top = 0
            pad_left = (pad_size[0] - from_width) // 2
        if pad_size is not None:
            pad_container = Image.new("RGBA", pad_size)
            pad_container.paste(image, (pad_left, pad_top))
            image = pad_container

    def resize(w, h, w_box, h_box, pil_image):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        '''
        f1 = 1.0*w_box/w  # 1.0 forces float division in Python2
        f2 = 1.0*h_box/h
        factor = min([f1, f2])
        #print(f1, f2, factor)  # test
        # use best down-sizing filter
        width = int(w*factor)
        height = int(h*factor)
        return pil_image.resize((width, height), Image.ANTIALIAS)

    # Create the thumbnail.
    to_size = (to_width, to_height)
    to_pos = (left, top)
    try:
        image = resize(from_width, from_height, to_width, to_height, image)
        image = image.save(thumb_path, filetype, quality=quality, **image_info)
        # Push a remote copy of the thumbnail if MEDIA_URL is
        # absolute.
        if "://" in settings.MEDIA_URL:
            with open(thumb_path, "rb") as f:
                default_storage.save(thumb_url, File(f))
    except Exception:
        # If an error occurred, a corrupted image may have been saved,
        # so remove it, otherwise the check for it existing will just
        # return the corrupted image next time it's requested.
        try:
            os.remove(thumb_path)
        except Exception:
            pass
        return image_url
    return thumb_url