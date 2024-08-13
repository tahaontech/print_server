import json
from escpos.printer import Network
from PIL import Image, ImageDraw, ImageFont
from fastapi.staticfiles import StaticFiles
import jdatetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
from sqlite3 import Error
import socket

from bidi.algorithm import get_display
import arabic_reshaper

import os
import sys


# Replace with your printer's IP address
PRINTER_IP = "192.168.0.103"
PRINTER_PORT = 9100  # Default port for many network printers
LOGO_PATH = "logo.bmp"  # Path to your logo file

# Connect to the network printer
printer = Network(PRINTER_IP, port=PRINTER_PORT, timeout=120)

def restart_process():
    # The executable is the Python interpreter
    executable = sys.executable
    # Re-run the current script with the same arguments
    os.execv(executable, ['python'] + sys.argv)

def _get_printer():
    print(printer.is_online())
    if printer.is_online():
        return printer
    else:
        restart_process()
    
def get_local_ip():
    try:
        # Create a socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external address (e.g., Google DNS) to determine the local IP
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        local_ip = s.getsockname()[0]
    except Exception as e:
        print(f"Error: {e}")
        local_ip = None
    finally:
        s.close()
    
    return local_ip

print("Server address : http://" + get_local_ip() + ":8000")

app = FastAPI()

# Database connection function
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

# Create a new SQLite database (or connect to an existing one)
database = "example.db"
conn = create_connection(database)

# Create a table
def create_table():
    try:
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS orders (
                                        id INTEGER PRIMARY KEY,
                                        products TEXT NOT NULL,
                                        table_number INTEGER NOT NULL,
                                        factor_number INTEGER NOT NULL,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                                    ); """
        c = conn.cursor()
        c.execute(sql_create_users_table)
    except Error as e:
        print(e)

create_table()

app = FastAPI()


# Define a Pydantic model for the response
class Product(BaseModel):
    name: str
    quantity: int
    price: int

class RequestModel(BaseModel):
    products: List[Product]
    table: int

class ResponseModel(BaseModel):
    message: str
    status: bool



global factor_num
factor_num = 1

def reshape_persian_text(text):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)



def draw_centered_text(draw, text, font, y_pos, image_width):
    reshaped_text = reshape_persian_text(text)
    text_width = draw.textbbox((0, 0), reshaped_text, font=font)[2]
    x_pos = (image_width - text_width) / 2
    draw.text((x_pos, y_pos), reshaped_text, font=font, fill="black")

def create_receipt_image(products, total,tableNumber,factorNumber, font, fontb):

    # Calculate the height of the image based on the number of products
    line_height = font.getbbox("A")[1] + 50  # Height of each line of text with padding
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
    draw_centered_text(d, "🍹 در هُنَر لَحظه ای شآدی بنوش", fontb, y_position, img.width)

    # return the image
    return img




def print_bill(p, products, total, tableNumber,factorNumber, font_path="Vazirmatn-Regular.ttf", fontbold_path="Vazirmatn-Bold.ttf"):
    
    font = ImageFont.truetype(fontbold_path, 28)
    fontb = ImageFont.truetype(fontbold_path, 32)
    

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
        

def insert_to_db(products, factor, table):
    productsj = [{"name": x.name, "quantity": x.quantity, "price": x.price} for x in products]
    products_string = json.dumps(productsj)
    sql = ''' INSERT INTO orders(products, table_number, factor_number)
                VALUES(?, ?, ?) '''
    cur = conn.cursor()
    
    cur.execute(sql, (products_string, table, factor))
    conn.commit()

@app.post("/print", response_model=ResponseModel)
async def get_data(request_data: RequestModel):
    products = [(x.name, x.quantity, x.price) for x in request_data.products]
    total = 0
    for x in request_data.products:
        total += x.quantity * x.price
    global factor_num 
    
    try:
        insert_to_db(request_data.products, factor_num, request_data.table)
        p = _get_printer()
        if not p:
            raise HTTPException(status_code=404, detail="printer is not connected")
        print_bill(printer, products, total, request_data.table, factor_num)
        factor_num += 1
        return ResponseModel(status=True, message="printed successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error -> {e}")

app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    _get_printer()
    # print_bill([('لاته', 10, 10), ('اسپرسو', 1, 10000)], 100, 8, 1)
    # font = ImageFont.truetype("Vazirmatn-Regular.ttf", 28)
    # fontb = ImageFont.truetype("Vazirmatn-Bold.ttf", 32)
    # img = create_receipt_image([('لاته', 10, 10), ('اسپرسو', 1, 10000)], 100, 8, 1, font, fontb)
    # img.show()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

