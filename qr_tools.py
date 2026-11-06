
import os
import qrcode

from PIL import Image, ImageDraw, ImageFont


QR_FOLDER = "qr_codes"


def create_qr_folder():
    """Create the QR code storage folder if needed."""
    os.makedirs(QR_FOLDER, exist_ok=True)


def generate_box_qr(unit_id, location=None):
    """Generate a QR code with a large Unit ID displayed above it."""

    create_qr_folder()

    # Information stored inside the QR code
    if location:
        qr_data = (
            f"Herbarium Twin\n"
            f"Unit ID: {unit_id}\n"
            f"Location: {location}"
        )
    else:
        qr_data = f"Herbarium Twin\nUnit ID: {unit_id}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    # Create space above QR code for Unit ID
    padding = 20
    heading_height = 100

    final_width = qr_img.width + (padding * 2)

    final_img = Image.new(
        "RGB",
        (
            final_width,
            qr_img.height + heading_height + padding
        ),
        "white"
    )

    draw = ImageDraw.Draw(final_img)

    # Load a large font and automatically scale it
    text = unit_id
    target_width = final_width * 0.80

    font_size = 80

    try:
        font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        font = ImageFont.load_default()

    # Increase or decrease font size to fit the target width
    while True:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width >= target_width or font_size <= 10:
            break

        font_size += 2

        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            break

    # Center Unit ID above QR code
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (final_width - text_width) // 2
    text_y = (heading_height - text_height) // 2 - bbox[1]

    draw.text(
        (text_x, text_y),
        text,
        fill="black",
        font=font
    )

    # Place QR code below heading
    final_img.paste(
        qr_img,
        (padding, heading_height)
    )

    # Save QR code using Unit ID
    filepath = os.path.join(
        QR_FOLDER,
        f"{unit_id}.png"
    )

    final_img.save(filepath)

    return filepath
