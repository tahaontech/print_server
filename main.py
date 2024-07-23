from PIL import Image, ImageDraw, ImageFont
import win32print
import win32ui
from PIL import ImageWin

def create_and_print_image(counts, items, table_number, printer_name = None):
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

    
    if not printer_name:
        printer_name = win32print.GetDefaultPrinter()

    # Open the printer
    hprinter = win32print.OpenPrinter(printer_name)
    hdc = win32ui.CreateDC("WINSPOOL", printer_name, None)

    # Create a device context from a file handle
    hdc.StartDoc("Printing Image")
    hdc.StartPage()

    # Convert the PIL image to a format suitable for printing
    dib = ImageWin.Dib(img)
    dib.draw(hdc.GetHandleOutput(), (0, 0, img.size[0], img.size[1]))

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()

# Example usage
counts = [3, 1, 2]
items = ["Pizza", "Coke", "Salad"]
table_number = 5
printer_name = 'table_order.png'
create_and_print_image(counts, items, table_number, printer_name)
