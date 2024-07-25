import subprocess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def create_image(counts, items, table_number, output_path):
    # Create an image with white backg
    img_width = 502
    img_height = 1000 + 100 * len(items)  # Base height + 30 pixels per item

    # Create an image with white background
    img = Image.new('RGB', (img_width, img_height), color='white')
    d = ImageDraw.Draw(img)

    # Set up fonts
    try:
        font = ImageFont.truetype("Vazirmatn-Regular.ttf", 48)
    except IOError:
        font = ImageFont.load_default()

    # Add table number
    d.text((100, 10), f"کافه هنر", fill='black', font=font)
    d.text((10, 100), f"شماره میز: {table_number}", fill='black', font=font)

    # Add items and counts
    y_text = 200
    for count, item in zip(counts, items):
        d.text((10, y_text), f"{item}: {count}", fill='black', font=font)
        y_text += 80

    # Save the image
    img.save(output_path)

def print_image(image_path, printer_name):
    try:
        # Print the image using PrintUIEntry
        subprocess.run([
            'rundll32', 'printui.dll,PrintUIEntry',
            '/orientation', 'landscape',
            '/y',  # Set the printer as default
            f'/n{printer_name}'
        ], check=True)
        
        # Open the image with mspaint and print to the default printer
        subprocess.run(['mspaint', '/orientation', 'landscape', '/pt', image_path], check=True)
        
        print(f"Sent {image_path} to the printer {printer_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to print {image_path}: {e}")

def factorer(items, tnumber):
    # Calculate totals
    subtotal = sum(quantity * price for _, quantity, price in items)
    tax = subtotal * 0.1  # Assuming a 10% tax rate
    total = subtotal + tax

    # Create an image
    width, height = 400, 300 + len(items) * 30
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype("Vazirmatn-Regular.ttf", 20)

    # Define positions
    y_position = 10
    line_height = 30

    # Add header
    draw.text((10, y_position), f"Store Receipt table: {tnumber}", fill='black', font=font)
    y_position += line_height
    draw.text((10, y_position), f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='black', font=font)
    y_position += line_height

    # Add items
    draw.line((10, y_position, width-10, y_position), fill='black')
    y_position += line_height
    for item, quantity, price in items:
        total_price = quantity * price
        draw.text((10, y_position), f"{item:<20} {quantity:>3} x {price:>6.2f} = {total_price:>8.2f}", fill='black', font=font)
        y_position += line_height

    # Add totals
    draw.line((10, y_position, width-10, y_position), fill='black')
    y_position += line_height
    draw.text((10, y_position), f"{'Subtotal':<30} {subtotal:>8.2f}", fill='black', font=font)
    y_position += line_height
    draw.text((10, y_position), f"{'Tax':<30} {tax:>8.2f}", fill='black', font=font)
    y_position += line_height
    draw.text((10, y_position), f"{'Total':<30} {total:>8.2f}", fill='black', font=font)
    y_position += line_height
    draw.line((10, y_position, width-10, y_position), fill='black')
    y_position += line_height

    # Add footer
    draw.text((10, y_position), "Thank you for shopping with us!", fill='black', font=font)

    # Save the image
    image.save('table_order.png')


# Define static input data
items = [
    ("سیب", 2, 0.5),
    ("موز", 5, 0.2),
    ("آب پرتغال", 1, 3.0),
    ("نون", 1, 2.5)
]

# Example usage
# counts = [3, 1, 2]
# # items = ["پیتزا", "نوشابه", "سالاد"]
table_number = 5
output_path = 'table_order.png'
# create_image(counts, items, table_number, output_path)
factorer(items, table_number)

printer_name = 'POS-80C'  # Replace with your actual printer name
print_image(output_path, printer_name)