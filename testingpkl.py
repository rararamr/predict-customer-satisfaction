import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from predict_ratings import predict_customer_rating
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('green')

class PredictionDashboard:
    def __init__(self, root):
    
        self.root = root
        self.root.title("Customer Rating Predictor")
        
        # Set minimum window size
        self.root.minsize(1250, 1000)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (1250/2)
        y = (screen_height/2) - (1000/2)
        self.root.geometry('%dx%d+%d+%d' % (1250, 1000, x, y))
        
        
        self.models = {
            'Decision Tree': 'decision_tree.pkl',
            'Random Forest': 'random_forest.pkl'
        }
        self.current_model = 'Decision Tree'
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.pack(fill='both', expand=True)

        
        # Add exit button to main_frame
        exit_button = ctk.CTkButton(self.main_frame, text="Exit", command=self.root.destroy)
        exit_button.pack(pady=10, padx=20, side='bottom')
        
        # Initialize CTkTabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(pady=40, padx=40, fill='both', expand=True)

        # Add tabs
        self.tabview.add("Single Prediction")
        self.tabview.add("Batch Prediction")
        self.tabview.add("Model Analysis")

        # Create frames for each tab
        self.single_frame = ctk.CTkFrame(self.tabview.tab("Single Prediction"))
        self.single_frame.pack(pady=40, padx=40, fill='both', expand=True)

        self.batch_frame = ctk.CTkFrame(self.tabview.tab("Batch Prediction"))
        self.batch_frame.pack(pady=40, padx=40, fill='both', expand=True)

        self.viz_frame = ctk.CTkFrame(self.tabview.tab("Model Analysis"))
        self.viz_frame.pack(pady=40, padx=40, fill='both', expand=True)
        
        self.create_single_prediction_tab()
        self.create_batch_prediction_tab()  
        self.create_visualization_tab()
        
    def extract_rating(self, text):
        try:
            match = re.search(r'Predicted Rating:\s*(\d+)', str(text))
            if match:
                rating = int(match.group(1))
                return rating if 1 <= rating <= 5 else None
            return None
        except:
            return None

    def validate_data(self, dt_data, rf_data):
        required_cols = ['Predicted Rating']
        for df in [dt_data, rf_data]:
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
        
    def create_batch_prediction_tab(self):
        # Model selector frame
        model_frame = ctk.CTkFrame(self.batch_frame)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(model_frame, text="Select Model:").pack(side="left", padx=5)
        self.batch_model_var = ctk.StringVar(value='Decision Tree')
        model_selector = ctk.CTkOptionMenu(
            model_frame,
            variable=self.batch_model_var,
            values=list(self.models.keys())
        )
        model_selector.pack(side="left", padx=5)

        # Upload frame
        upload_frame = ctk.CTkFrame(self.batch_frame)
        upload_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            upload_frame, 
            text="Load CSV", 
            command=self.load_csv
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            upload_frame, 
            text="Clear Results", 
            command=self.clear_batch
        ).pack(side="left", padx=5)

        # Results table
        # Note: Since CTk doesn't have a direct Treeview equivalent, 
        # we'll keep ttk.Treeview but style it to match
        style = ttk.Style()
        # Configure Treeview with minimal custom settings
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        fieldbackground="white",
                        rowheight=25)

        # Configure headings
        style.configure("Treeview.Heading",
                        relief="raised",
                        font=('Helvetica', 10, 'bold'))

        # Configure selection colors
        style.map('Treeview',
                background=[('selected', '#0078D7')],
                foreground=[('selected', 'white')])

        # Results table with model column
        self.tree = ttk.Treeview(self.batch_frame, columns=("model", "shopid", "orderid", "itemid", "userid", "date", "predicted_rating"), show='headings')
        self.tree.heading("model", text="Model Used")
        self.tree.heading("shopid", text="Shop ID")
        self.tree.heading("orderid", text="Order ID")
        self.tree.heading("itemid", text="Item ID")
        self.tree.heading("userid", text="User ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("predicted_rating", text="Predicted Rating")
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Set column widths
        for col in ("model", "shopid", "orderid", "itemid", "userid", "date", "predicted_rating"):
            self.tree.column(col, width=100, stretch=True)

        # Export button
        ctk.CTkButton(
            self.batch_frame, 
            text="Export Results", 
            command=self.export_results
        ).pack(pady=5)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                required_columns = ['shopid', 'orderid', 'itemid', 'userid', 'date']
                
                if not all(col in df.columns for col in required_columns):
                    messagebox.showerror("Error", "CSV must contain: shopid, orderid, itemid, userid, date")
                    return
                
                # Clear existing items
                self.clear_batch()
                
                # Process each row with selected model
                for _, row in df.iterrows():
                    timestamp = int(datetime.strptime(row['date'], '%d/%m/%Y %H:%M').timestamp())
                    prediction = predict_customer_rating(
                        int(row['shopid']),
                        int(row['orderid']),
                        int(row['itemid']),
                        int(row['userid']),
                        timestamp,
                        model_name=self.batch_model_var.get()
                    )
                    
                    self.tree.insert("", "end", values=(
                        self.batch_model_var.get(),
                        row['shopid'],
                        row['orderid'],
                        row['itemid'],
                        row['userid'],
                        row['date'],
                        prediction
                    ))
                    
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_batch(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def export_results(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        
        if file_path:
            data = []
            for item in self.tree.get_children():
                data.append(self.tree.item(item)['values'])
                
            df = pd.DataFrame(data, columns=["Model", "Shop ID", "Order ID", "Item ID", "User ID", "Date", "Predicted Rating"])
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", "Results exported successfully")
        
    def create_single_prediction_tab(self):
        # Input frame
        input_frame = ctk.CTkFrame(self.single_frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Add title label
        ctk.CTkLabel(input_frame, text="Input Data", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Model selector frame
        model_frame = ctk.CTkFrame(input_frame)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(model_frame, text="Select Model:").pack(side="left", padx=5)
        self.model_var = ctk.StringVar(value='Decision Tree')
        model_selector = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=list(self.models.keys())
        )
        model_selector.pack(side="left", padx=5)
        
        # Input fields frame
        fields_frame = ctk.CTkFrame(input_frame)
        fields_frame.pack(fill="x", padx=10, pady=5)
        
        # Create input fields
        self.entries = {}
        labels = ['Shop ID:', 'Order ID:', 'Item ID:', 'User ID:', 'Date:']
        
        for i, label in enumerate(labels):
            ctk.CTkLabel(fields_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            self.entries[label] = ctk.CTkEntry(fields_frame)
            self.entries[label].grid(row=i, column=1, padx=5, pady=5)
        
        # Default date
        self.entries['Date:'].insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Button frame
        button_frame = ctk.CTkFrame(self.single_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="Predict", 
            command=self.predict_single
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="Clear", 
            command=self.clear_fields
        ).pack(side="left", padx=5)
        
        # Result frame
        result_frame = ctk.CTkFrame(self.single_frame)
        result_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(result_frame, text="Prediction Result", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.result_label = ctk.CTkLabel(
            result_frame, 
            text="", 
            font=("Arial", 12)
        )
        self.result_label.pack(pady=10)

       
    def predict_single(self):
        try:
            
            # Get values from entries
            shopid = int(self.entries['Shop ID:'].get())
            orderid = int(self.entries['Order ID:'].get())
            itemid = int(self.entries['Item ID:'].get())
            userid = int(self.entries['User ID:'].get())
            
            # Convert date to timestamp
            date_str = self.entries['Date:'].get()
            timestamp = int(datetime.strptime(date_str, '%Y-%m-%d').timestamp())
            
            # Get prediction using selected model
            prediction, explanation = predict_customer_rating(
                shopid, orderid, itemid, userid, timestamp,
                model_name=self.model_var.get()
            )
            
            # Display result with model name
            self.result_label.configure(
                text=f"Predicted Rating ({self.model_var.get()}): {prediction} stars"
            )
            
             # Update result display
            self.result_label.configure(text=explanation)
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.entries['Date:'].insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.result_label.configure(text="")

    def create_visualization_tab(self):
        # Title label
        title_label = ctk.CTkLabel(self.viz_frame, text="Model Feature Importance Analysis", 
                            font=('Helvetica', 12, 'bold'))
        title_label.pack(pady=10)

        # File selection frame
        file_frame = ctk.CTkFrame(self.viz_frame)
        file_frame.pack(fill='x', padx=5, pady=5)
        
        self.viz_file_path = ctk.StringVar()
        ctk.CTkLabel(file_frame, text="CSV File:").pack(side='left')
        ctk.CTkEntry(file_frame, textvariable=self.viz_file_path, width=300).pack(side='left', padx=5)
        ctk.CTkButton(file_frame, text="Browse", command=self.load_visualization_data).pack(side='left')
        ctk.CTkButton(file_frame, text="Clear Plot", command=self.clear_feature_plot).pack(side='left', padx=5)

        # Plot frame
        self.feature_frame = ctk.CTkFrame(self.viz_frame)
        self.feature_frame.pack(fill='both', expand=True, padx=10, pady=5)

    def load_visualization_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.viz_file_path.set(file_path)
            self.update_feature_plot()

    def clear_feature_plot(self):
        # Clear previous plot
        for widget in self.feature_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
        self.viz_file_path.set('')  # Clear file path

    def update_feature_plot(self):
        try:
            # Clear previous plot
            for widget in self.feature_frame.winfo_children():
                if isinstance(widget, tk.Canvas):
                    widget.destroy()

            # Load prediction data
            dt_data = pd.read_csv(self.viz_file_path.get())
            
            def extract_features(text):
                features = {}
                lines = str(text).split('\n')
                for line in lines:
                    if '(Impact:' in line:
                        try:
                            feature = line.split(':')[0].strip('• ')
                            impact_str = line.split('Impact: ')[1].strip(')')
                            if 'median' in impact_str.lower():
                                impact = 0.0
                            else:
                                impact = float(impact_str)
                            features[feature] = impact
                        except (ValueError, IndexError):
                            continue
                return features
            
            for pred in dt_data['Predicted Rating']:
                if pd.notna(pred):
                    features = extract_features(pred)
                    break
            else:
                raise ValueError("No valid predictions found")

            sorted_features = dict(sorted(
                [(k,v) for k,v in features.items() if v is not None], 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            if not sorted_features:
                raise ValueError("No valid feature importance values found")

            fig, ax = plt.subplots(figsize=(10, 6))
            features = list(sorted_features.keys())
            importance = list(sorted_features.values())
            
            bars = ax.barh(features, importance)
            ax.set_xlabel('Feature Importance')
            ax.set_title('Model Feature Importance')
            
            for rect in bars:
                width = rect.get_width()
                ax.text(width, rect.get_y() + rect.get_height()/2,
                    f'{width:.3f}',
                    ha='left', va='center', fontweight='bold')
            
            canvas = FigureCanvasTkAgg(fig, self.feature_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            ttk.Label(self.feature_frame, 
                    text=f"Error creating visualization: {str(e)}\n\nPlease ensure CSV contains valid prediction data").pack(pady=20)
    
    
def create_new_window2(parent):
    try:
        new_window = tk.Toplevel()
        dashboard = PredictionDashboard(new_window)
        new_window.deiconify()  # Ensure window is visible
        return dashboard
    except Exception as e:
        print(f"Debug - Error in create_new_window2: {str(e)}")
        raise

if __name__ == "__main__":
    ctk.set_appearance_mode('dark')
    root = ctk.CTk()
    dashboard = PredictionDashboard(root)
    root.mainloop()