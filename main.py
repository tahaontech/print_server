import subprocess
from PIL import Image, ImageDraw, ImageFont

def create_image(counts, items, table_number, output_path):
    # Create an image with white background
    img = Image.new('RGB', (400, 300), color='white')
    d = ImageDraw.Draw(img)

    # Set up fonts
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    # Add table number
    d.text((10, 10), f"Table Number: {table_number}", fill='black', font=font)

    # Add items and counts
    y_text = 50
    for count, item in zip(counts, items):
        d.text((10, y_text), f"{item}: {count}", fill='black', font=font)
        y_text += 30

    # Save the image
    img.save(output_path)

def print_image(image_path, printer_name):
    try:
        # Print the image using PrintUIEntry
        subprocess.run([
            'rundll32', 'printui.dll,PrintUIEntry',
            '/y',  # Set the printer as default
            f'/n{printer_name}'
        ], check=True)
        
        # Open the image with mspaint and print to the default printer
        subprocess.run(['mspaint', '/pt', image_path], check=True)
        
        print(f"Sent {image_path} to the printer {printer_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to print {image_path}: {e}")

# Example usage
counts = [3, 1, 2]
items = ["Pizza", "Coke", "Salad"]
table_number = 5
output_path = 'table_order.png'
create_image(counts, items, table_number, output_path)

printer_name = 'POS-80C'  # Replace with your actual printer name
print_image(output_path, printer_name)