import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import datetime
import os
from tkinter import filedialog

class MedicalStoreManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Store Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.init_db()
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_medicines()
        self.update_stock_warning()
        
    def init_db(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect('medical_store.db')
        self.cursor = self.conn.cursor()
        
        # Create medicines table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                med_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                category TEXT,
                purchase_price REAL,
                sale_price REAL,
                quantity INTEGER,
                expiry_date TEXT
            )
        ''')
        
        # Create sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                med_id INTEGER,
                med_name TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                sale_date TEXT,
                FOREIGN KEY (med_id) REFERENCES medicines(med_id)
            )
        ''')
        
        # Create bills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                total_amount REAL,
                bill_date TEXT
            )
        ''')
        
        self.conn.commit()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Medical Store Management System", 
                              font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sidebar
        sidebar = tk.Frame(main_container, bg='#34495e', width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Main content area
        self.main_content = tk.Frame(main_container, bg='white')
        self.main_content.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        # Sidebar buttons
        buttons = [
            ("🏥 Medicine Management", self.show_medicine_management),
            ("💰 Rate Update", self.show_rate_update),
            ("📦 Stock Management", self.show_stock_management),
            ("🛒 Billing System", self.show_billing_system),
            ("📊 Sales Report", self.show_sales_report),
            ("💊 Medicine List", self.show_medicine_list)
        ]
        
        for text, command in buttons:
            btn = tk.Button(sidebar, text=text, font=('Arial', 11), 
                           bg='#34495e', fg='white', bd=0, padx=20, pady=15,
                           anchor='w', command=command, cursor='hand2')
            btn.pack(fill='x')
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#1abc9c'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#34495e'))
        
        # Show default page
        self.show_medicine_management()
    
    def clear_content(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_medicine_management(self):
        """Show medicine management page"""
        self.clear_content()
        
        # Title
        title = tk.Label(self.main_content, text="Medicine Management", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(self.main_content, bg='white')
        form_frame.pack(pady=10, padx=20, fill='x')
        
        # Form fields
        fields = ["Medicine Name", "Company Name", "Category", 
                  "Purchase Price", "Sale Price", "Stock Quantity", "Expiry Date (YYYY-MM-DD)"]
        self.medicine_entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(form_frame, text=field + ":", font=('Arial', 11), 
                    bg='white').grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = tk.Entry(form_frame, font=('Arial', 11), width=30)
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.medicine_entries[field] = entry
        
        # Buttons frame
        btn_frame = tk.Frame(self.main_content, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Add Medicine", bg='#3498db', fg='white',
                 font=('Arial', 11), padx=20, pady=10, command=self.add_medicine).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Update Selected", bg='#2ecc71', fg='white',
                 font=('Arial', 11), padx=20, pady=10, command=self.update_medicine).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete Selected", bg='#e74c3c', fg='white',
                 font=('Arial', 11), padx=20, pady=10, command=self.delete_medicine).pack(side='left', padx=5)
    
    def show_rate_update(self):
        """Show rate update page"""
        self.clear_content()
        
        title = tk.Label(self.main_content, text="Update Medicine Rates", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Rate update frame
        update_frame = tk.Frame(self.main_content, bg='white')
        update_frame.pack(pady=10, padx=20)
        
        tk.Label(update_frame, text="Select Medicine:", font=('Arial', 11), 
                bg='white').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        
        # Medicine combobox
        self.rate_med_var = tk.StringVar()
        self.rate_combobox = ttk.Combobox(update_frame, textvariable=self.rate_med_var, 
                                         font=('Arial', 11), width=30, state='readonly')
        self.rate_combobox.grid(row=0, column=1, pady=5, padx=5)
        
        # Load medicines for combobox
        self.cursor.execute("SELECT med_id, name FROM medicines")
        medicines = self.cursor.fetchall()
        self.rate_combobox['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
        
        tk.Label(update_frame, text="New Sale Price:", font=('Arial', 11), 
                bg='white').grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.new_price_entry = tk.Entry(update_frame, font=('Arial', 11), width=30)
        self.new_price_entry.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Button(update_frame, text="Update Rate", bg='#3498db', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.update_rate).grid(row=2, column=1, pady=10)
    
    def show_stock_management(self):
        """Show stock management page"""
        self.clear_content()
        
        title = tk.Label(self.main_content, text="Stock Management", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Stock treeview
        stock_frame = tk.Frame(self.main_content, bg='white')
        stock_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ("ID", "Medicine Name", "Company", "Category", "Quantity", "Expiry Date")
        self.stock_tree = ttk.Treeview(stock_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(stock_frame, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load stock data
        self.load_stock_data()
        
        # Warning label
        self.warning_label = tk.Label(self.main_content, text="", font=('Arial', 11), 
                                     bg='white', fg='red')
        self.warning_label.pack(pady=5)
    
    def show_billing_system(self):
        """Show billing system page"""
        self.clear_content()
        
        title = tk.Label(self.main_content, text="Billing System", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Billing container
        billing_container = tk.Frame(self.main_content, bg='white')
        billing_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left frame - Medicine selection
        left_frame = tk.Frame(billing_container, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Select Medicine:", font=('Arial', 11), 
                bg='white').pack(anchor='w', pady=5)
        
        self.bill_med_var = tk.StringVar()
        self.bill_combobox = ttk.Combobox(left_frame, textvariable=self.bill_med_var, 
                                         font=('Arial', 11), state='readonly')
        self.bill_combobox.pack(fill='x', pady=5)
        
        tk.Label(left_frame, text="Quantity:", font=('Arial', 11), 
                bg='white').pack(anchor='w', pady=5)
        self.quantity_entry = tk.Entry(left_frame, font=('Arial', 11))
        self.quantity_entry.pack(fill='x', pady=5)
        
        tk.Button(left_frame, text="Add to Bill", bg='#3498db', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.add_to_bill).pack(pady=10)
        
        # Right frame - Bill details
        right_frame = tk.Frame(billing_container, bg='white')
        right_frame.pack(side='right', fill='both', expand=True)
        
        tk.Label(right_frame, text="Bill Details:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=5)
        
        self.bill_text = scrolledtext.ScrolledText(right_frame, width=40, height=15,
                                                  font=('Courier', 10))
        self.bill_text.pack(fill='both', expand=True, pady=5)
        
        # Customer name
        tk.Label(right_frame, text="Customer Name:", font=('Arial', 11), 
                bg='white').pack(anchor='w', pady=5)
        self.customer_entry = tk.Entry(right_frame, font=('Arial', 11))
        self.customer_entry.pack(fill='x', pady=5)
        
        # Total and buttons
        total_frame = tk.Frame(right_frame, bg='white')
        total_frame.pack(fill='x', pady=10)
        
        tk.Label(total_frame, text="Total Amount:", font=('Arial', 12, 'bold'), 
                bg='white').pack(side='left')
        self.total_label = tk.Label(total_frame, text="₹0.00", font=('Arial', 12, 'bold'), 
                                   bg='white', fg='green')
        self.total_label.pack(side='left', padx=10)
        
        btn_frame = tk.Frame(right_frame, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Generate Bill", bg='#2ecc71', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.generate_bill).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Print Bill", bg='#3498db', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.print_bill).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Clear Bill", bg='#e74c3c', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.clear_bill).pack(side='left', padx=5)
        
        # Initialize billing variables
        self.bill_items = []
        self.total_amount = 0.0
        
        # Load medicines for billing
        self.load_billing_medicines()
    
    def show_sales_report(self):
        """Show sales report page"""
        self.clear_content()
        
        title = tk.Label(self.main_content, text="Sales Report", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Date selection
        date_frame = tk.Frame(self.main_content, bg='white')
        date_frame.pack(pady=10)
        
        tk.Label(date_frame, text="From Date (YYYY-MM-DD):", font=('Arial', 11), 
                bg='white').pack(side='left', padx=5)
        self.from_date = tk.Entry(date_frame, font=('Arial', 11), width=15)
        self.from_date.pack(side='left', padx=5)
        
        tk.Label(date_frame, text="To Date (YYYY-MM-DD):", font=('Arial', 11), 
                bg='white').pack(side='left', padx=5)
        self.to_date = tk.Entry(date_frame, font=('Arial', 11), width=15)
        self.to_date.pack(side='left', padx=5)
        
        tk.Button(date_frame, text="Filter", bg='#3498db', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.filter_sales).pack(side='left', padx=10)
        
        # Sales treeview
        sales_frame = tk.Frame(self.main_content, bg='white')
        sales_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ("Sale ID", "Medicine", "Quantity", "Price", "Total", "Date")
        self.sales_tree = ttk.Treeview(sales_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(sales_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load sales data
        self.load_sales_data()
        
        # Total sales label
        self.sales_total_label = tk.Label(self.main_content, text="", font=('Arial', 12, 'bold'), 
                                         bg='white', fg='blue')
        self.sales_total_label.pack(pady=5)
    
    def show_medicine_list(self):
        """Show medicine list page"""
        self.clear_content()
        
        title = tk.Label(self.main_content, text="Medicine List", 
                        font=('Arial', 20, 'bold'), bg='white')
        title.pack(pady=10)
        
        # Search frame
        search_frame = tk.Frame(self.main_content, bg='white')
        search_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(search_frame, text="Search:", font=('Arial', 11), 
                bg='white').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, font=('Arial', 11), width=30)
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(search_frame, text="Search", bg='#3498db', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.search_medicines).pack(side='left', padx=5)
        tk.Button(search_frame, text="Export CSV", bg='#2ecc71', fg='white',
                 font=('Arial', 11), padx=20, pady=5, command=self.export_csv).pack(side='left', padx=5)
        
        # Medicine treeview
        med_frame = tk.Frame(self.main_content, bg='white')
        med_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Company", "Category", "Purchase", "Sale", "Stock", "Expiry")
        self.med_tree = ttk.Treeview(med_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.med_tree.heading(col, text=col)
            self.med_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(med_frame, orient="vertical", command=self.med_tree.yview)
        self.med_tree.configure(yscrollcommand=scrollbar.set)
        
        self.med_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load medicine data
        self.load_medicine_data()
    
    # Database operations
    def add_medicine(self):
        """Add new medicine to database"""
        try:
            values = [self.medicine_entries[field].get() for field in 
                     ["Medicine Name", "Company Name", "Category", 
                      "Purchase Price", "Sale Price", "Stock Quantity", "Expiry Date (YYYY-MM-DD)"]]
            
            # Validate required fields
            if not values[0]:
                messagebox.showerror("Error", "Medicine Name is required!")
                return
            
            # Insert into database
            self.cursor.execute('''
                INSERT INTO medicines (name, company, category, purchase_price, 
                                     sale_price, quantity, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', values)
            self.conn.commit()
            
            messagebox.showinfo("Success", "Medicine added successfully!")
            
            # Clear form
            for entry in self.medicine_entries.values():
                entry.delete(0, tk.END)
            
            # Refresh medicine list
            self.load_medicines()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")
    
    def load_medicines(self):
        """Load medicines for comboboxes"""
        self.cursor.execute("SELECT med_id, name FROM medicines")
        medicines = self.cursor.fetchall()
        med_list = [f"{m[0]} - {m[1]}" for m in medicines]
        
        # Update comboboxes if they exist
        if hasattr(self, 'rate_combobox'):
            self.rate_combobox['values'] = med_list
        if hasattr(self, 'bill_combobox'):
            self.bill_combobox['values'] = med_list
    
    def update_medicine(self):
        """Update selected medicine"""
        # Implementation for update medicine
        messagebox.showinfo("Info", "Update medicine functionality")
    
    def delete_medicine(self):
        """Delete selected medicine"""
        # Implementation for delete medicine
        messagebox.showinfo("Info", "Delete medicine functionality")
    
    def update_rate(self):
        """Update medicine sale price"""
        try:
            med_str = self.rate_med_var.get()
            new_price = self.new_price_entry.get()
            
            if not med_str or not new_price:
                messagebox.showerror("Error", "Please select medicine and enter new price!")
                return
            
            med_id = med_str.split(" - ")[0]
            
            # Get old price
            self.cursor.execute("SELECT sale_price FROM medicines WHERE med_id = ?", (med_id,))
            old_price = self.cursor.fetchone()[0]
            
            # Update price
            self.cursor.execute("UPDATE medicines SET sale_price = ? WHERE med_id = ?", 
                              (float(new_price), med_id))
            self.conn.commit()
            
            messagebox.showinfo("Success", 
                              f"Price updated!\nOld Price: ₹{old_price}\nNew Price: ₹{new_price}")
            
            self.new_price_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update rate: {str(e)}")
    
    def load_stock_data(self):
        """Load stock data into treeview"""
        # Clear existing items
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        self.cursor.execute('''
            SELECT med_id, name, company, category, quantity, expiry_date 
            FROM medicines ORDER BY quantity ASC
        ''')
        
        for row in self.cursor.fetchall():
            self.stock_tree.insert("", "end", values=row)
    
    def update_stock_warning(self):
        """Update low stock warning"""
        self.cursor.execute("SELECT name FROM medicines WHERE quantity < 10")
        low_stock = self.cursor.fetchall()
        
        if low_stock:
            warning_text = "⚠️ Low Stock Warning: " + ", ".join([m[0] for m in low_stock])
            if hasattr(self, 'warning_label'):
                self.warning_label.config(text=warning_text)
        elif hasattr(self, 'warning_label'):
            self.warning_label.config(text="")
    
    def load_billing_medicines(self):
        """Load medicines for billing combobox"""
        self.cursor.execute("SELECT med_id, name, sale_price, quantity FROM medicines WHERE quantity > 0")
        medicines = self.cursor.fetchall()
        med_list = [f"{m[0]} - {m[1]} (₹{m[2]}, Stock: {m[3]})" for m in medicines]
        
        if hasattr(self, 'bill_combobox'):
            self.bill_combobox['values'] = med_list
    
    def add_to_bill(self):
        """Add selected medicine to bill"""
        try:
            med_str = self.bill_med_var.get()
            quantity = self.quantity_entry.get()
            
            if not med_str or not quantity:
                messagebox.showerror("Error", "Please select medicine and enter quantity!")
                return
            
            med_id = med_str.split(" - ")[0]
            quantity = int(quantity)
            
            # Check stock availability
            self.cursor.execute("SELECT name, sale_price, quantity FROM medicines WHERE med_id = ?", (med_id,))
            med_data = self.cursor.fetchone()
            
            if not med_data:
                messagebox.showerror("Error", "Medicine not found!")
                return
            
            if quantity > med_data[2]:
                messagebox.showerror("Error", f"Insufficient stock! Available: {med_data[2]}")
                return
            
            # Calculate total
            total = med_data[1] * quantity
            
            # Add to bill items
            self.bill_items.append({
                'med_id': med_id,
                'name': med_data[0],
                'price': med_data[1],
                'quantity': quantity,
                'total': total
            })
            
            # Update bill display
            self.update_bill_display()
            
            # Clear inputs
            self.quantity_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to bill: {str(e)}")
    
    def update_bill_display(self):
        """Update the bill display text"""
        self.bill_text.delete(1.0, tk.END)
        
        bill_text = "=" * 40 + "\n"
        bill_text += "MEDICAL STORE BILL\n"
        bill_text += "=" * 40 + "\n"
        bill_text += f"{'Item':<20} {'Qty':<6} {'Price':<8} {'Total':<8}\n"
        bill_text += "-" * 40 + "\n"
        
        self.total_amount = 0
        
        for item in self.bill_items:
            bill_text += f"{item['name'][:20]:<20} {item['quantity']:<6} "
            bill_text += f"₹{item['price']:<7} ₹{item['total']:<7}\n"
            self.total_amount += item['total']
        
        bill_text += "=" * 40 + "\n"
        bill_text += f"{'TOTAL AMOUNT:':<32} ₹{self.total_amount:.2f}\n"
        bill_text += "=" * 40 + "\n"
        
        self.bill_text.insert(1.0, bill_text)
        self.total_label.config(text=f"₹{self.total_amount:.2f}")
    
    def generate_bill(self):
        """Generate and save bill"""
        if not self.bill_items:
            messagebox.showerror("Error", "No items in the bill!")
            return
        
        try:
            customer_name = self.customer_entry.get() or "Walk-in Customer"
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save bill to database
            self.cursor.execute('''
                INSERT INTO bills (customer_name, total_amount, bill_date)
                VALUES (?, ?, ?)
            ''', (customer_name, self.total_amount, current_date))
            
            bill_id = self.cursor.lastrowid
            
            # Save bill items and update stock
            for item in self.bill_items:
                # Save sale record
                self.cursor.execute('''
                    INSERT INTO sales (med_id, med_name, quantity, price, total, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item['med_id'], item['name'], item['quantity'], 
                     item['price'], item['total'], current_date))
                
                # Update stock
                self.cursor.execute('''
                    UPDATE medicines 
                    SET quantity = quantity - ? 
                    WHERE med_id = ?
                ''', (item['quantity'], item['med_id']))
            
            self.conn.commit()
            
            # Update bill display with bill ID
            self.bill_text.insert(tk.END, f"\nBill ID: {bill_id}\n")
            self.bill_text.insert(tk.END, f"Customer: {customer_name}\n")
            self.bill_text.insert(tk.END, f"Date: {current_date}\n")
            
            messagebox.showinfo("Success", f"Bill generated successfully!\nBill ID: {bill_id}")
            
            # Refresh data
            self.load_billing_medicines()
            self.update_stock_warning()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
    
    def print_bill(self):
        """Print bill to file"""
        try:
            bill_content = self.bill_text.get(1.0, tk.END)
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(bill_content)
                
                messagebox.showinfo("Success", f"Bill saved to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
    
    def clear_bill(self):
        """Clear current bill"""
        self.bill_items = []
        self.total_amount = 0
        self.bill_text.delete(1.0, tk.END)
        self.total_label.config(text="₹0.00")
        self.customer_entry.delete(0, tk.END)
    
    def load_sales_data(self):
        """Load sales data into treeview"""
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        self.cursor.execute('''
            SELECT sale_id, med_name, quantity, price, total, sale_date 
            FROM sales ORDER BY sale_date DESC LIMIT 100
        ''')
        
        total_sales = 0
        
        for row in self.cursor.fetchall():
            self.sales_tree.insert("", "end", values=row)
            total_sales += row[4]
        
        if hasattr(self, 'sales_total_label'):
            self.sales_total_label.config(text=f"Total Sales: ₹{total_sales:.2f}")
    
    def filter_sales(self):
        """Filter sales by date range"""
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        
        query = "SELECT sale_id, med_name, quantity, price, total, sale_date FROM sales WHERE 1=1"
        params = []
        
        if from_date:
            query += " AND DATE(sale_date) >= ?"
            params.append(from_date)
        
        if to_date:
            query += " AND DATE(sale_date) <= ?"
            params.append(to_date)
        
        query += " ORDER BY sale_date DESC"
        
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        self.cursor.execute(query, params)
        
        total_sales = 0
        
        for row in self.cursor.fetchall():
            self.sales_tree.insert("", "end", values=row)
            total_sales += row[4]
        
        if hasattr(self, 'sales_total_label'):
            self.sales_total_label.config(text=f"Total Filtered Sales: ₹{total_sales:.2f}")
    
    def load_medicine_data(self):
        """Load medicine data into treeview"""
        # Clear existing items
        if hasattr(self, 'med_tree'):
            for item in self.med_tree.get_children():
                self.med_tree.delete(item)
        
        self.cursor.execute('''
            SELECT med_id, name, company, category, purchase_price, 
                   sale_price, quantity, expiry_date 
            FROM medicines ORDER BY name
        ''')
        
        for row in self.cursor.fetchall():
            if hasattr(self, 'med_tree'):
                self.med_tree.insert("", "end", values=row)
    
    def search_medicines(self):
        """Search medicines by name or category"""
        search_term = self.search_entry.get()
        
        if hasattr(self, 'med_tree'):
            for item in self.med_tree.get_children():
                self.med_tree.delete(item)
        
        if search_term:
            query = '''
                SELECT med_id, name, company, category, purchase_price, 
                       sale_price, quantity, expiry_date 
                FROM medicines 
                WHERE name LIKE ? OR category LIKE ?
                ORDER BY name
            '''
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            self.cursor.execute('''
                SELECT med_id, name, company, category, purchase_price, 
                       sale_price, quantity, expiry_date 
                FROM medicines ORDER BY name
            ''')
        
        for row in self.cursor.fetchall():
            if hasattr(self, 'med_tree'):
                self.med_tree.insert("", "end", values=row)
    
    def export_csv(self):
        """Export medicine list to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="medicine_list.csv"
            )
            
            if filename:
                self.cursor.execute('''
                    SELECT name, company, category, purchase_price, 
                           sale_price, quantity, expiry_date 
                    FROM medicines ORDER BY name
                ''')
                
                with open(filename, 'w') as f:
                    # Write header
                    f.write("Name,Company,Category,Purchase Price,Sale Price,Quantity,Expiry Date\n")
                    
                    # Write data
                    for row in self.cursor.fetchall():
                        f.write(",".join(str(item) for item in row) + "\n")
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def on_closing(self):
        """Close database connection on exit"""
        self.conn.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MedicalStoreManagement(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()