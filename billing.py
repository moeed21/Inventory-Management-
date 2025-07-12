from sysconfig import get_path
import time
import sqlite3
import os
import platform
import subprocess
from tkinter import *
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
def get_path():
    return "Inventory-Management-System/bill/123456.txt"

# Ensure the directory exists
os.makedirs('Inventory-Management-System/bill', exist_ok=True)

# Then write the file
with open(get_path(), 'w') as fp:

    ...

class billClass:
    def __init__(self, root):
        self.root = root
        self.root.title("Billing")
        self.root.geometry("800x600")

        # Variables
        self.var_cname = StringVar()
        self.var_contact = StringVar()
        self.invoice = int(time.strftime("%H%M%S"))  # Unique invoice number
        self.cart_list = []  # (pid, name, price, qty)
        self.bill_amnt = 0
        self.discount = 0
        self.net_pay = 0
        self.chk_print = 0

        # Optional: Callback to refresh stock from main app
        self.refresh_stock_callback = None

        # Bill area (optional visual)
        self.txt_bill_area = Text(self.root, font=("Arial", 12), bg="white")
        self.txt_bill_area.pack(expand=1, fill=BOTH)

    def bill_top(self):
        self.txt_bill_area.delete('1.0', END)
        self.txt_bill_area.insert(END, "\tWelcome to XYZ-Inventory\n")
        self.txt_bill_area.insert(END, f"\n Bill No: {self.invoice}")
        self.txt_bill_area.insert(END, f"\n Customer Name: {self.var_cname.get()}")
        self.txt_bill_area.insert(END, f"\n Phone No: {self.var_contact.get()}")
        self.txt_bill_area.insert(END, f"\n==========================================")
        self.txt_bill_area.insert(END, f"\n Product\t\tQTY\tPrice")
        self.txt_bill_area.insert(END, f"\n==========================================\n")

    def bill_middle(self):
        for row in self.cart_list:
            name = row[1]
            qty = row[3]
            price = float(row[2]) * int(qty)
            self.txt_bill_area.insert(END, f" {name}\t\t{qty}\t{price}\n")

    def bill_bottom(self):
        self.txt_bill_area.insert(END, f"\n==========================================")
        self.txt_bill_area.insert(END, f"\nBill Amount\t\t\tRs.{self.bill_amnt}")
        self.txt_bill_area.insert(END, f"\nDiscount\t\t\tRs.{self.discount}")
        self.txt_bill_area.insert(END, f"\nNet Pay\t\t\tRs.{self.net_pay}")
        self.txt_bill_area.insert(END, f"\n==========================================")

    def generate_invoice_pdf(self):
        pdf_file_path = f"Inventory-Management-System/bill/{str(self.invoice)}.pdf"
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter
        y = height - 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(200, y, "XYZ-Inventory")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(200, y, "Phone No. 9899459288 , Delhi-110053")
        y -= 30
        c.drawString(30, y, f"Customer Name: {self.var_cname.get()}")
        y -= 15
        c.drawString(30, y, f"Contact No: {self.var_contact.get()}")
        y -= 15
        c.drawString(30, y, f"Bill No: {str(self.invoice)}")
        c.drawString(300, y, f"Date: {str(time.strftime('%d/%m/%Y'))}")
        y -= 30

        c.setFont("Helvetica-Bold", 10)
        c.drawString(30, y, "Product Name")
        c.drawString(250, y, "Qty")
        c.drawString(350, y, "Price")
        y -= 20
        c.setFont("Helvetica", 10)

        for row in self.cart_list:
            name = row[1]
            qty = row[3]
            price = f"Rs.{float(row[2]) * int(row[3])}".strip()
            c.drawString(30, y, name)
            c.drawString(250, y, qty)
            c.drawString(350, y, price)
            y -= 15
            if y < 100:
                c.showPage()
                y = height - 40

        y -= 10
        c.line(30, y, 500, y)
        y -= 15

        c.drawString(30, y, f"Bill Amount: Rs.{self.bill_amnt}")
        y -= 15
        c.drawString(30, y, f"Discount: Rs.{self.discount}")
        y -= 15
        c.drawString(30, y, f"Net Pay: Rs.{self.net_pay}")

        c.save()
        return pdf_file_path

    def generate_bill(self):
        if self.var_cname.get() == "" or self.var_contact.get() == "":
            messagebox.showerror("Error", "Customer Details are required", parent=self.root)
        elif len(self.cart_list) == 0:
            messagebox.showerror("Error", "Please Add product to the Cart!!!", parent=self.root)
        else:
            self.bill_top()
            self.bill_middle()
            self.bill_bottom()

            # Save bill as .txt
            txt_path = f'Inventory-Management-System/bill/{str(self.invoice)}.txt'
            with open(txt_path, 'w') as fp:
                fp.write(self.txt_bill_area.get('1.0', END))

            # Save PDF and open print preview
            pdf_file_path = self.generate_invoice_pdf()
            try:
                if platform.system() == "Windows":
                    os.startfile(pdf_file_path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", pdf_file_path])
                else:
                    subprocess.run(["xdg-open", pdf_file_path])
            except Exception as e:
                print("Could not open PDF:", e)

            # Update stock in database
            con = sqlite3.connect(database='ims.db')
            cur = con.cursor()
            try:
                for item in self.cart_list:
                    pid = item[0]
                    qty_sold = int(item[3])
                    cur.execute("SELECT qty FROM product WHERE pid=?", (pid,))
                    result = cur.fetchone()
                    if result is not None:
                        current_qty = int(result[0])
                        if current_qty >= qty_sold:
                            new_qty = current_qty - qty_sold
                            cur.execute("UPDATE product SET qty=? WHERE pid=?", (new_qty, pid))
                        else:
                            messagebox.showerror("Error", f"Insufficient stock for product ID {pid}", parent=self.root)
                con.commit()
                con.close()
            except Exception as e:
                messagebox.showerror("Database Error", str(e), parent=self.root)

            # Call optional refresh function from main app
            try:
                if self.refresh_stock_callback:
                    self.refresh_stock_callback()
            except Exception as e:
                print("Could not refresh stock view:", e)

            messagebox.showinfo("Saved", "Bill has been generated", parent=self.root)
            self.chk_print = 1

# Optional test
if __name__ == "__main__":
    root = Tk()
    obj = billClass(root)

    # Dummy test data
    obj.var_cname.set("Moeed")
    obj.var_contact.set("9876543210")
    obj.cart_list = [(1, "Mouse", 400, 2), (2, "Keyboard", 600, 1)]
    obj.bill_amnt = 1400
    obj.discount = 100
    obj.net_pay = 1300

    obj.generate_bill()
    root.mainloop()
