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

    # Use 'point' unit for compatibility with pixel dimensions if needed,
    # though standard FPDF flow usually works fine.
    pdf = FPDF(unit="pt")

    # Disable auto page break to handle full-page images manually
    pdf.set_auto_page_break(False)

    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"Warning: Image not found {img_path}")
            continue

        try:
            # Open image to get dimensions
            with Image.open(img_path) as img:
                width, height = img.size

                # Add page matching image size
                pdf.add_page(format=(width, height))

                # Place image at 0,0
                pdf.image(img_path, x=0, y=0, w=width, h=height)
        except Exception as e:
            print(f"Failed to process image {img_path}: {e}")

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        pdf.output(output_path)
        print(f"Successfully created PDF: {output_path}")
    except Exception as e:
        print(f"Failed to save PDF: {e}")
