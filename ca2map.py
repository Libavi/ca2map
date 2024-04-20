import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO

st.set_page_config(layout="wide", page_title="Capture Age to Map Image")

st.write("## Get a pretty Age of Empires II map image from a Capture Age screenshot.")
st.write(
    "Try uploading a screenshot to see the map image. Full quality images can be downloaded below the preview."
)
st.sidebar.write("## :gear: Settings")
center = st.sidebar.checkbox('Minimap is in the center')
grey_border = st.sidebar.checkbox('Add grey border')
st.sidebar.write("## ⬆️ Upload")

def crop_to_box(image):
    # cropping the image to the minimap
    height = 0.215*image.size[1]
    width = int(2*height)
    height = int(height)
    left = None
    if center:
        left = int(image.size[0]/2 - width/2)
    else:  # bottom right
        left = image.size[0] - width

    box = (left,
           image.size[1] - height,
           left+width,
           image.size[1])

    return image.crop(box)


def add_padding(image, padding):
    # adding the same pink padding on all sides of the image
    width = image.size[0] + 2*padding
    height = image.size[1] + 2*padding
    pink = (128, 0, 64)  # RGB color pink
    padded_image = Image.new(image.mode, (width, height), pink)
    padded_image.paste(image, (padding, padding))

    return padded_image


def get_diamond(width, height, offset, offset2=0):
    # getting the diamond as a tuple of tuples
    if height % 2:  # uneven
        left = [(1 + offset, int(height / 2))]
        right = [(width - 2 - offset, int(height / 2))]
    else:  # even
        left = [(1 + offset, height / 2),
                (1 + offset, height / 2 - 1)]
        right = [(width - 2 - offset, height / 2 - 1),
                 (width - 2 - offset, height / 2)]

    if width % 2:  # uneven
        top = [(int(width / 2), offset)]
        bottom = [(int(width / 2), height - 1 - offset)]
    else:  # even
        top = [(width / 2 - 1 - offset2, offset),
               (width / 2 + offset2, offset)]
        bottom = [(width / 2 + offset2, height - 1 - offset),
                  (width / 2 - 1 - offset2, height - 1 - offset)]

    return (*left, *top, *right, *bottom, *left)


def crop_to_diamond(image, padding):
    # cropping the image to a diamond
    width, height = image.size
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(get_diamond(width, height, 1+padding, offset2=1), fill=255)
    diamond_image = image.copy()
    diamond_image.putalpha(mask)

    return diamond_image


def add_border(image, padding, scale_factor):
    # adding a grey border to the image
    width, height = image.size
    border = Image.new("RGB", image.size, 0)
    border.putalpha(0)
    draw = ImageDraw.Draw(border)
    draw.line(get_diamond(width, height, padding+1-round(scale_factor)),
              width=round(3*scale_factor), fill=(50,50,50,), joint='round')
    border = border.filter(ImageFilter.GaussianBlur(1))
    final_image = image.copy()
    final_image.alpha_composite(border)

    return final_image


def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    return byte_im


def get_map_icon(upload):
    full_image = Image.open(upload)
    col1.write("### :camera: CA screenshot")
    col1.image(full_image)

    cropped_image = crop_to_box(full_image)
    if grey_border:
        scale_factor = full_image.size[1] / 1080
        padding = round(2 * scale_factor)
        padded_image = add_padding(cropped_image, padding)
        diamond_image = crop_to_diamond(padded_image, padding)
        final_image = add_border(diamond_image, padding, scale_factor)
    else:
        diamond_image = crop_to_diamond(cropped_image, 0)
        final_image = add_padding(diamond_image, -1)

    col2.write("### 🗺️ map image preview")
    col2.image(final_image)
    st.sidebar.markdown("\n")
    col2.download_button("⬇️ Download full quality map image", convert_image(final_image), "map.png", "image/png")

col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("In Capture Age, make sure to fully zoom out before taking the screenshot!",
                                     type=["png", "jpg", "jpeg"])

if my_upload is not None:
    get_map_icon(upload=my_upload)
else:
    get_map_icon("./example.png")
