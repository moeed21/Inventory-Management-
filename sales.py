from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import os
from reportlab.pdfgen import canvas

class salesClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.title("Inventory Management System | Nishant Gupta")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        self.blll_list = []

        # Title
        lbl_title = Label(self.root, text="View Customer Bills", font=("goudy old style", 30),
                          bg="#184a45", fg="white", bd=3, relief=RIDGE)
        lbl_title.pack(side=TOP, fill=X, padx=10, pady=20)

        # Bill list
        sales_Frame = Frame(self.root, bd=3, relief=RIDGE)
        sales_Frame.place(x=50, y=100, width=200, height=370)

        scrolly = Scrollbar(sales_Frame, orient=VERTICAL)
        self.Sales_List = Listbox(sales_Frame, font=("goudy old style", 15), bg="white", yscrollcommand=scrolly.set)
        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=self.Sales_List.yview)
        self.Sales_List.pack(fill=BOTH, expand=1)
        self.Sales_List.bind("<ButtonRelease-1>", self.get_data)

        # Bill display area
        bill_Frame = Frame(self.root, bd=3, relief=RIDGE)
        bill_Frame.place(x=280, y=100, width=410, height=370)

        lbl_title2 = Label(bill_Frame, text="Customer Bill Area", font=("goudy old style", 20), bg="orange")
        lbl_title2.pack(side=TOP, fill=X)

        scrolly2 = Scrollbar(bill_Frame, orient=VERTICAL)
        self.bill_area = Text(bill_Frame, bg="lightyellow", yscrollcommand=scrolly2.set)
        scrolly2.pack(side=RIGHT, fill=Y)
        scrolly2.config(command=self.bill_area.yview)
        self.bill_area.pack(fill=BOTH, expand=1)

        # Export to PDF button
        btn_pdf = Button(self.root, text="Export as PDF", command=self.export_pdf,
                         font=("times new roman", 15, "bold"), bg="#4CAF50", fg="white", cursor="hand2")
        btn_pdf.place(x=280, y=480, width=410, height=30)

        # Bill image
        try:
            self.bill_photo = Image.open("Inventory-Management-System/images/cat2.jpg")
            self.bill_photo = self.bill_photo.resize((450, 300))
            self.bill_photo = ImageTk.PhotoImage(self.bill_photo)
            lbl_image = Label(self.root, image=self.bill_photo, bd=0)
            lbl_image.place(x=700, y=110)
        except:
            pass  # If image not found, skip

        self.show()

    def show(self):
        del self.blll_list[:]
        self.Sales_List.delete(0, END)
        for i in os.listdir('Inventory-Management-System/bill'):
            if i.endswith('.txt'):
                self.Sales_List.insert(END, i)
                self.blll_list.append(i.split('.')[0])

    def get_data(self, ev):
        index_ = self.Sales_List.curselection()
        file_name = self.Sales_List.get(index_)
        self.selected_file = f'Inventory-Management-System/bill/{file_name}'
        self.bill_area.delete('1.0', END)
        with open(self.selected_file, 'r') as fp:
            for line in fp:
                self.bill_area.insert(END, line)

    def export_pdf(self):
        try:
            if not hasattr(self, 'selected_file'):
                messagebox.showerror("Error", "No bill selected", parent=self.root)
                return

            pdf_file = self.selected_file.replace('.txt', '.pdf')
            with open(self.selected_file, 'r') as f:
                lines = f.readlines()

            c = canvas.Canvas(pdf_file)
            c.setFont("Helvetica", 12)
            y = 800
            for line in lines:
                c.drawString(40, y, line.strip())
                y -= 18
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 800
            c.save()

            messagebox.showinfo("PDF Created", f"Invoice exported as:\n{pdf_file}", parent=self.root)

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

if __name__ == "__main__":
    root = Tk()
    obj = salesClass(root)
    root.mainloop()
