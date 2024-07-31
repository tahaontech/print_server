from escpos.printer import Network
from PIL import Image, ImageDraw, ImageFont
import jdatetime

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple

app = FastAPI()

# Define a Pydantic model for the response
class Product(BaseModel):
    name: str
    quantity: int
    price: int

class RequestModel(BaseModel):
    products: List[Product]
    total: int
    table: int
    factor: int

class ResponseModel(BaseModel):
    message: str
    status: bool

# Replace with your printer's IP address
PRINTER_IP = "192.168.0.103"
PRINTER_PORT = 9100  # Default port for many network printers
LOGO_PATH = "logo.bmp"  # Path to your logo file

def draw_centered_text(draw, text, font, y_pos, image_width):
    text_width = draw.textbbox((0, 0), text, font=font)[2]
    x_pos = (image_width - text_width) / 2
    draw.text((x_pos, y_pos), text, font=font, fill="black")

def create_receipt_image(products, total,tableNumber,factorNumber, font, fontb):

    # Calculate the height of the image based on the number of products
    line_height = font.getbbox("A")[1] + 40  # Height of each line of text with padding
    header_height = 2 * line_height  # For the header and separator lines
    footer_height = 6 * line_height  # For the total and thank you lines
    product_lines_height = len(products) * line_height * 2 # Height for all product lines
    total_height = header_height + product_lines_height + footer_height
    
    # Create an image with dynamic height
    img = Image.new('RGB', (400, total_height), color='white')
    d = ImageDraw.Draw(img)


    # Print the centered Persian text on the image
    y_position = 10
    # Get the current Persian date and time
    current_persian_datetime = jdatetime.datetime.now()
    date_format = "%m/%d/%Y %H:%M:%S"
    persian_date = current_persian_datetime.strftime(date_format)
    draw_centered_text(d, persian_date, font, y_position, img.width)
    y_position += line_height

    draw_centered_text(d, f"شماره فاکتور:                       {factorNumber}", fontb, y_position, img.width)
    y_position += line_height

    draw_centered_text(d, f"شماره میز:                       {tableNumber}", fontb, y_position, img.width)
    y_position += line_height

    draw_centered_text(d, "کالا             تعداد  قیمت", font, y_position, img.width)
    y_position += line_height
    draw_centered_text(d, "ــــــــــــــــــــــــــــــــــــــ", fontb, y_position, img.width)

    # Add the custom product lines
    for product, quantity, price in products:
        y_position += line_height
        product_text = f"{product}             {quantity}      {price}"
        draw_centered_text(d, product_text, font, y_position, img.width)
        y_position += line_height
        draw_centered_text(d, "-------------------", font, y_position, img.width)

    y_position += line_height
    draw_centered_text(d, "ــــــــــــــــــــــــــــــــــــــ", fontb, y_position, img.width)

    y_position += line_height
    draw_centered_text(d, f"جمع کل:                {total:.2f}", font, y_position, img.width)

    y_position += line_height
    draw_centered_text(d, "🍹 در هُنَر لَحظه ای شآدی بنوش", font, y_position, img.width)

    # return the image
    return img




def print_bill(products, total, tableNumber,factorNumber, font_path="Vazirmatn-Regular.ttf", fontbold_path="Vazirmatn-Bold.ttf"):
    try:
        font = ImageFont.truetype(font_path, 24)
        fontb = ImageFont.truetype(fontbold_path, 32)
        # Connect to the network printer
        p = Network(PRINTER_IP, port=PRINTER_PORT)

        p.set(align='center', bold=True)
        
        img = create_receipt_image(products, total, tableNumber,factorNumber, font, fontb)
        
        # Convert the image to grayscale and print
        img = img.convert("L")
        p.image(img)

        p.text("\n")

        # Print the logo
        logo = Image.open(LOGO_PATH)
        p.image(logo)
        p.text("\n")

        img = Image.new('RGB', (384, 50), color='white')
        d = ImageDraw.Draw(img)

        draw_centered_text(d, "کافه رستوران هنر", font, 10, img.width)

        img = img.convert("L")
        p.image(img)

        p.text("\n")
        
        # Cut the paper
        p.cut()
        
        print("Bill printed successfully")
        
    except Exception as e:
        print(f"Failed to print bill: {e}")

@app.post("/print", response_model=ResponseModel)
async def get_data(request_data: RequestModel):
    products = [(x.name, x.quantity, x.price) for x in request_data.products]
    try:
        print_bill(products, request_data.total, request_data.table, request_data.factor)
        return ResponseModel(status=True, message="printed successfully"), 200
    except:
        return ResponseModel(status=False, message="error in printing"), 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

