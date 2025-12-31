import os
from fpdf import FPDF
from PIL import Image


def create_pdf(image_paths: list[str], output_path: str):
    """
    Stitches a list of image paths into a single PDF.
    """
    if not image_paths:
        print("No images to compile.")
        return

    # Initialize PDF
    # We'll set unit to points for precise sizing if strictly needed,
    # but default mm is usually fine. We'll use variable page size.
    pdf = FPDF(unit="pt")

    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"Warning: Image not found {img_path}")
            continue

        try:
            with Image.open(img_path) as img:
                width, height = img.size

                # Add a page with the same dimensions as the image
                pdf.add_page(format=(width, height))

                # Insert image filling the page
                pdf.image(img_path, x=0, y=0, w=width, h=height)
        except Exception as e:
            print(f"Failed to process image {img_path}: {e}")

    try:
        pdf.output(output_path)
        print(f"Successfully created PDF: {output_path}")
    except Exception as e:
        print(f"Failed to save PDF: {e}")
