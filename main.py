import subprocess

def generate_receipt(order, prices, tax_rate=0.07, filename="receipt.rpt"):
    """
    Generates a receipt for a cafe order and saves it to a file.
    
    Parameters:
    order (dict): A dictionary with item names as keys and quantities as values.
    prices (dict): A dictionary with item names as keys and prices as values.
    tax_rate (float): The tax rate to apply on the total amount (default is 7%).
    filename (str): The name of the file to save the receipt (default is 'receipt.rpt').
    
    Returns:
    None
    """
    lines = []
    lines.append("به کافه دیلایت خوش آمدید\n")
    lines.append("======================\n")
    total = 0

    for item, quantity in order.items():
        if item in prices:
            item_total = prices[item] * quantity
            total += item_total
            lines.append(f"{item} x{quantity}: ${item_total:.2f}\n")
        else:
            lines.append(f"{item} موجود نیست\n")

    tax = total * tax_rate
    grand_total = total + tax

    lines.append("----------------------\n")
    lines.append(f"جمع کل: ${total:.2f}\n")
    lines.append(f"مالیات: ${tax:.2f}\n")
    lines.append(f"مجموع: ${grand_total:.2f}\n")
    lines.append("======================\n")
    lines.append("از بازدید شما از کافه دیلایت سپاسگزاریم!\n")
    lines.append("======================\n")

    # Write the receipt to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(lines)

# Example usage
order = {
    "قهوه": 2,
    "چایی": 1,
    "ساندویچ": 2
}

prices = {
    "قهوه": 3.50,
    "چایی": 2.75,
    "ساندویچ": 5.00,
    "کیک": 4.00
}

generate_receipt(order, prices)



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



# printer_name = 'POS-80C'  # Replace with your actual printer name
# print_image(output_path, printer_name)