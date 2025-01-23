import tkinter as tk
from tkinter import messagebox
import customtkinter
from PIL import ImageTk, Image
import connection
import mysql


conn = connection.conn
def create_new_window(parent):
    reg_win = customtkinter.CTkToplevel(parent)
    reg_win.title("User Registration")
    form_width = 440
    form_height = 600
    screen_width = reg_win.winfo_screenwidth()
    screen_height = reg_win.winfo_screenheight()
    x = (screen_width/2) - (form_width/2)
    y = (screen_height/2) - (form_height/2)
    reg_win.geometry('%dx%d+%d+%d' % (form_width, form_height, x, y))
    
    img1 = Image.open('pic1.jpg')
    resized_img = img1.resize((form_width, form_height))
    img1 = ImageTk.PhotoImage(resized_img)
    #img1 = ImageTk.PhotoImage(Image.open('pic1.jpg'))
    l2 = customtkinter.CTkLabel(master=reg_win, image=img1)
    l2.pack()
    frame=customtkinter.CTkFrame (master=l2, width=320, height=360, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def register_user():
        fullname = txt_fullname.get()
        email = txt_email.get()
        username = txt_username.get()
        password = txt_password.get()

        # Basic input validation
        if not all([fullname, email, username, password]):
            messagebox.showinfo("Error", "Please fill in all fields.")
            return

        try:
            # Check connection outside the try block
            if not connection.conn.is_connected():
                messagebox.showerror("Error", "Database connection failed.")
                return

            # Database insertion
            cursor = connection.conn.cursor()
            sql_query = "INSERT INTO test_user_info (fullname, email, username, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_query, (fullname, email, username, password))
            connection.conn.commit()  # Commit the changes

            messagebox.showinfo("Success", "Registration successful!")
            reg_win.destroy()  # Close registration window
            parent.deiconify()  # Show the login window again
        except mysql.connector.Error as err:  # Catch specific MySQL errors
            messagebox.showerror("Error", f"Registration failed: {err}")

    def go_back():
        reg_win.destroy()  # Close the registration window
        parent.deiconify()  # Show the login window again

    label2=customtkinter.CTkLabel(master=frame, text="Enter your information",font=('Century Gothic',20))
    label2.place(x=50, y=35)

    txt_fullname = customtkinter.CTkEntry(master=frame, width=220, placeholder_text='Enter your Full Name:')
    txt_fullname.place(x=50, y=70)
    txt_email = customtkinter.CTkEntry(master=frame, width=220, placeholder_text='Enter your Email:')
    txt_email.place(x=50, y=120)
    txt_username = customtkinter.CTkEntry(master=frame, width=220, placeholder_text='Enter your Username:')
    txt_username.place(x=50, y=170)
    txt_password = customtkinter.CTkEntry(master=frame, width=220, placeholder_text='Enter your Password:', show="*")
    txt_password.place(x=50, y=220)

    button1 = customtkinter.CTkButton(master=frame, width=220, text="Register", command=register_user, corner_radius=6)
    button1.place(x=50, y=260)

    l3=customtkinter.CTkLabel(master=frame, text="Already have an account?",font=('Century Gothic',12))
    l3.place(x=50, y=290)

    button2 = customtkinter.CTkButton(master=frame, width=5, text="Login", command=go_back, corner_radius=6, fg_color="#2B2B2B", text_color="white", hover_color="#106A43", font=('Century Gothic', 12) )
    button2.place(x = 215, y = 290)

