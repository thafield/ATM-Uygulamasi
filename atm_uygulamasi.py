import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import datetime

class ATM:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Uygulaması")

        # Veritabanı bağlantısı
        self.conn = sqlite3.connect('atm.db')  # SQLite veritabanı dosyası 'atm.db' olarak oluşturuldu
        self.c = self.conn.cursor()

        # users tablosunu oluşturma
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         username TEXT UNIQUE, 
                         password TEXT,
                         balance REAL)''')

        # Admin kullanıcıyı veritabanına ekle
        self.add_admin()

        # Log dosyasını oluşturma ve açma
        self.log_file = open('atm_log.txt', 'a')  # Log dosyası 'atm_log.txt' olarak oluşturuldu ve 'a' modunda açıldı (mevcut veriye eklemek için)

        # Kullanıcı giriş ekranı
        self.create_login_frame()

    def add_admin(self):
        # Eğer admin kullanıcı yoksa, admin kullanıcıyı oluştur
        self.c.execute("SELECT * FROM users WHERE username=?", ('admin',))
        admin = self.c.fetchone()
        if not admin:
            self.c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", ('admin', 'admin123', 0))
            self.conn.commit()  # Değişiklikler veritabanına kaydedildi

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Kullanıcı Adı:").grid(row=0, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.login_frame, text="Şifre:").grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self.login_frame, text="Giriş", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(self.login_frame, text="Yeni Kullanıcı Oluştur", command=self.show_create_account).grid(row=3, column=0, columnspan=2, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.c.fetchone()
        if user:
            if username == 'admin':
                self.logged_in_username = username
                self.log(f"{username} kullanıcısı giriş yaptı")  # Giriş yapan kullanıcı log kaydı
                self.show_admin_menu()
            else:
                self.logged_in_username = username
                self.log(f"{username} kullanıcısı giriş yaptı")  # Giriş yapan kullanıcı log kaydı
                self.show_menu()
        else:
            self.log("Geçersiz kullanıcı adı veya şifre girişi")  # Geçersiz giriş denemesi log kaydı
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre!")

    def show_menu(self):
        self.login_frame.destroy()

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=20)

        tk.Button(self.menu_frame, text="Bakiye Sorgula", command=self.check_balance).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(self.menu_frame, text="Para Yükle", command=self.deposit).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.menu_frame, text="Para Çek", command=self.withdraw).grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        tk.Button(self.menu_frame, text="Çıkış", command=self.logout).grid(row=2, column=0, columnspan=2, pady=10)

    def show_admin_menu(self):
        self.login_frame.destroy()

        self.admin_menu_frame = tk.Frame(self.root)
        self.admin_menu_frame.pack(pady=20)

        tk.Button(self.admin_menu_frame, text="Kullanıcıları Listele", command=self.list_users).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(self.admin_menu_frame, text="Logları Görüntüle", command=self.view_logs).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.admin_menu_frame, text="Kullanıcı Ekle", command=self.add_user).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(self.admin_menu_frame, text="Kullanıcı Sil", command=self.delete_user).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.admin_menu_frame, text="Başka Kullanıcının Bakiyesini Sorgula", command=self.check_other_balance).grid(row=2, column=0, padx=10, pady=5)
        tk.Button(self.admin_menu_frame, text="Başka Kullanıcı Adı ve Şifresini Görüntüle", command=self.view_other_user).grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self.admin_menu_frame, text="Logları Sil", command=self.clear_logs).grid(row=3, column=0, padx=10, pady=5)
        tk.Button(self.admin_menu_frame, text="Çıkış", command=self.logout).grid(row=3, column=1, padx=10, pady=5)

    def show_create_account(self):
        self.login_frame.destroy()

        self.create_account_frame = tk.Frame(self.root)
        self.create_account_frame.pack(pady=20)

        tk.Label(self.create_account_frame, text="Yeni Kullanıcı Adı:").grid(row=0, column=0, padx=10, pady=5)
        self.new_username_entry = tk.Entry(self.create_account_frame)
        self.new_username_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.create_account_frame, text="Yeni Şifre:").grid(row=1, column=0, padx=10, pady=5)
        self.new_password_entry = tk.Entry(self.create_account_frame, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self.create_account_frame, text="Oluştur", command=self.create_account).grid(row=2, column=0, columnspan=2, pady=10)

    def create_account(self):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()

        if len(new_password) != 6:
            messagebox.showerror("Hata", "Şifre 6 karakter olmalıdır!")
            return

        self.c.execute("SELECT * FROM users WHERE username=?", (new_username,))
        existing_user = self.c.fetchone()
        if existing_user:
            messagebox.showerror("Hata", "Kullanıcı adı zaten mevcut!")
        else:
            self.c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (new_username, new_password, 0))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Kullanıcı oluşturuldu!")
            self.show_login_frame()

    def check_balance(self):
        self.c.execute("SELECT balance FROM users WHERE username=?", (self.logged_in_username,))
        balance = self.c.fetchone()
        messagebox.showinfo("Bakiye Sorgulama", f"Bakiyeniz: {balance[0]}")
        self.log(f"{self.logged_in_username} kullanıcısı bakiyesini sorguladı")

    def deposit(self):
        amount = simpledialog.askfloat("Para Yükle", "Yüklenecek miktar:")
        if amount is not None:
            if amount > 0:
                self.c.execute("UPDATE users SET balance = balance + ? WHERE username=?", (amount, self.logged_in_username))
                self.conn.commit()
                messagebox.showinfo("Para Yükleme", f"{amount} TL yüklendi.")
                self.log(f"{self.logged_in_username} kullanıcısı {amount} TL yükledi")
            else:
                messagebox.showerror("Hata", "Geçersiz miktar!")

    def withdraw(self):
        amount = simpledialog.askfloat("Para Çek", "Çekilecek miktar:")
        if amount is not None:
            self.c.execute("SELECT balance FROM users WHERE username=?", (self.logged_in_username,))
            balance = self.c.fetchone()[0]
            if amount > 0 and amount <= balance:
                self.c.execute("UPDATE users SET balance = balance - ? WHERE username=?", (amount, self.logged_in_username))
                self.conn.commit()
                messagebox.showinfo("Para Çekme", f"{amount} TL çekildi.")
                self.log(f"{self.logged_in_username} kullanıcısı {amount} TL çekti")
            else:
                messagebox.showerror("Hata", "Yetersiz bakiye veya geçersiz miktar!")

    def logout(self):
        self.logged_in_username = None
        self.log("Çıkış yapıldı")
        self.show_login_frame()

    def show_login_frame(self):
        if hasattr(self, 'menu_frame'):
            self.menu_frame.destroy()
        if hasattr(self, 'admin_menu_frame'):
            self.admin_menu_frame.destroy()
        if hasattr(self, 'create_account_frame'):
            self.create_account_frame.destroy()

        self.create_login_frame()

    def list_users(self):
        self.c.execute("SELECT * FROM users")
        users = self.c.fetchall()
        user_list = "\n".join([f"ID: {user[0]}, Kullanıcı Adı: {user[1]}" for user in users])
        messagebox.showinfo("Kullanıcılar", user_list)
        self.log("Kullanıcılar listelendi")

    def view_logs(self):
        with open('atm_log.txt', 'r') as log_file:
            logs = log_file.read()
            messagebox.showinfo("Loglar", logs)
            self.log("Loglar görüntülendi")

    def add_user(self):
        new_username = simpledialog.askstring("Yeni Kullanıcı Ekle", "Yeni kullanıcı adı:")
        if new_username:
            new_password = simpledialog.askstring("Yeni Kullanıcı Ekle", "Yeni şifre:")
            if new_password:
                if len(new_password) != 6:
                    messagebox.showerror("Hata", "Şifre 6 karakter olmalıdır!")
                    return

                self.c.execute("SELECT * FROM users WHERE username=?", (new_username,))
                existing_user = self.c.fetchone()
                if existing_user:
                    messagebox.showerror("Hata", "Kullanıcı adı zaten mevcut!")
                else:
                    self.c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (new_username, new_password, 0))
                    self.conn.commit()
                    messagebox.showinfo("Başarılı", "Kullanıcı oluşturuldu!")
                    self.log(f"{new_username} kullanıcısı eklendi")

    def delete_user(self):
        username_to_delete = simpledialog.askstring("Kullanıcı Sil", "Silinecek kullanıcı adı:")
        if username_to_delete:
            self.c.execute("DELETE FROM users WHERE username=?", (username_to_delete,))
            self.conn.commit()
            messagebox.showinfo("Başarılı", f"{username_to_delete} kullanıcısı silindi!")
            self.log(f"{username_to_delete} kullanıcısı silindi")

    def clear_logs(self):
        if messagebox.askyesno("Logları Sil", "Tüm logları silmek istediğinizden emin misiniz?"):
            open('atm_log.txt', 'w').close()
            messagebox.showinfo("Başarılı", "Loglar temizlendi!")
            self.log("Loglar silindi")

    def check_other_balance(self):
        other_username = simpledialog.askstring("Başka Kullanıcının Bakiyesini Sorgula", "Kullanıcı adını girin:")
        if other_username:
            self.c.execute("SELECT balance FROM users WHERE username=?", (other_username,))
            balance = self.c.fetchone()
            if balance:
                messagebox.showinfo("Bakiye Sorgulama", f"{other_username} kullanıcısının bakiyesi: {balance[0]}")
                self.log(f"{self.logged_in_username} kullanıcısı {other_username} kullanıcısının bakiyesini sorguladı")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı!")

    def view_other_user(self):
        other_username = simpledialog.askstring("Başka Kullanıcı Adı ve Şifre", "Kullanıcı adını girin:")
        if other_username:
            self.c.execute("SELECT username, password FROM users WHERE username=?", (other_username,))
            user_info = self.c.fetchone()
            if user_info:
                messagebox.showinfo("Kullanıcı Bilgileri", f"Kullanıcı Adı: {user_info[0]}\nŞifre: {user_info[1]}")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı!")

    def log(self, message):
        now = datetime.datetime.now()
        log_message = f"{now}: {message}\n"
        self.log_file.write(log_message)  # Log mesajı dosyaya yazıldı
        self.log_file.flush()  # Veriyi disk'e hemen yazmak için buffer boşaltıldı

if __name__ == "__main__":
    root = tk.Tk()
    app = ATM(root)
    root.mainloop()