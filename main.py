import sqlite3
import random
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)  # colorama init

# Connect to DB
conn = sqlite3.connect('Account.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    no INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT UNIQUE,
    age INTEGER,
    login_pin TEXT,
    account_number TEXT UNIQUE,
    acc_balance REAL,
    transfer_pin TEXT,
    unique_id TEXT
)
""")
conn.commit()

print('                                              Console Banking')
print('''A. Open Login Account    
B. Create New Account    
C. Exit''')
choice = input('Choose(A/B/C): ').lower()


# ---------- helpers ----------
def generate_account_number():
    while True:
        acc_no = str(random.randint(10**9, (10**10) - 1))  # 10-digit number
        cursor.execute("SELECT account_number FROM accounts WHERE account_number = ?", (acc_no,))
        if cursor.fetchone() is None:
            return acc_no
        # otherwise, loop again


def generate_unique_id(account_no, Username, name):
    # get auto-increment id (no) for this account (safe fallback)
    cursor.execute("SELECT no FROM accounts WHERE account_number = ?", (account_no,))
    row = cursor.fetchone()
    user_no = row[0] if row else 0

    digit_sum = sum(int(z) for z in str(account_no))
    uname_len = len(Username)
    first_letter = name.strip()[0].upper()            # note (): upper()
    raw_val = user_no + uname_len + digit_sum
    unique_id = f"{first_letter}{raw_val % 100:02d}"
    return unique_id


def calculate_DOB():
    while True:
        dob_input = input('Date of Birth (DD-MM-YYYY) e.g 27-07-1982: ')
        try:
            dob = datetime.strptime(dob_input, '%d-%m-%Y')
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except ValueError:
            print(Fore.RED + "❌ Invalid format. Use DD-MM-YYYY. Try again.")


def create_login_pin():
    while True:
        pin = input('Login PIN: ')
        confirm_pin = input('Confirm Login PIN: ')
        if pin == confirm_pin:
            print(Fore.GREEN + '✅ Login PIN match')
            return pin
        else:
            print(Fore.RED + '❌ Login PIN does not match, please try again.')


def create_Transfer_pin():
    while True:
        Tpin = input('Transfer PIN: ')
        confirm_Tpin = input('Confirm Transfer PIN: ')
        if Tpin == confirm_Tpin:
            print(Fore.GREEN + '✅ Transfer PIN match')
            return Tpin
        else:
            print(Fore.RED + '❌ Transfer PIN does not match, please try again.')


def username():
    while True:
        uname = input('Username: ')
        cursor.execute("SELECT username FROM accounts WHERE username = ?", (uname,))
        if cursor.fetchone() is None:
            return uname
        else:
            print(Fore.YELLOW + '⚠️ Username taken — try another.')


def Display_Acc_Balance(account_no):
    cursor.execute('SELECT acc_balance FROM accounts WHERE account_number = ?', (account_no,))
    row = cursor.fetchone()
    if row is None:
        print(Fore.RED + "⚠️ Account not found.")
    else:
        balance = row[0] or 0.0
        print(Fore.CYAN + f"💵 Balance: ${balance:.2f}")


# ---------- transactions ----------
def deposit(account_no, transfer_pin):
    try:
        Amount = float(input('Enter Amount to Deposit: '))
    except ValueError:
        print(Fore.RED + "❌ Invalid amount.")
        return

    ask_confirm = input(f'Are you sure you want to deposit {Amount} (Y/N): ').lower()
    if ask_confirm != 'y':
        print("Cancelled.")
        return

    ask_transfer_pin = input('Enter Transfer PIN: ')
    if ask_transfer_pin != transfer_pin:
        print(Fore.RED + "❌ Wrong transfer PIN.")
        return

    cursor.execute("UPDATE accounts SET acc_balance = acc_balance + ? WHERE account_number = ?", (Amount, account_no))
    conn.commit()
    print(Fore.GREEN + f'✅ {Amount} deposited successfully!')
    Display_Acc_Balance(account_no)


def withdraw(account_no, transfer_pin):
    try:
        Amount = float(input('Enter Amount to Withdraw: '))
    except ValueError:
        print(Fore.RED + "❌ Invalid amount.")
        return

    ask_confirm = input(f'Are you sure you want to Withdraw {Amount} (Y/N): ').lower()
    if ask_confirm != 'y':
        print("Cancelled.")
        return

    ask_transfer_pin = input('Enter Transfer PIN: ')
    if ask_transfer_pin != transfer_pin:
        print(Fore.RED + "❌ Wrong transfer PIN.")
        return

    cursor.execute("SELECT acc_balance FROM accounts WHERE account_number = ?", (account_no,))
    row = cursor.fetchone()
    balance = row[0] or 0.0
    if Amount > balance:
        print(Fore.RED + "❌ Insufficient funds.")
        return

    cursor.execute("UPDATE accounts SET acc_balance = acc_balance - ? WHERE account_number = ?", (Amount, account_no))
    conn.commit()
    print(Fore.GREEN + f'✅ {Amount} withdrawn successfully!')
    Display_Acc_Balance(account_no)


# ---------- sign up (choice B) ----------
def choice_B():
    name = input('Full Name: ')
    age = calculate_DOB()
    print(f'Age: {age}')

    if age < 18:
        print(Fore.RED + '❌ You must be at least 18 years old to create an account.')
        return

    login_pin = create_login_pin()
    transfer_pin = create_Transfer_pin()
    account_no = generate_account_number()
    Username = username()

    # Insert with TEMP unique_id so we can fetch auto-increment no
    cursor.execute("""
        INSERT INTO accounts (name, username, age, login_pin, account_number, acc_balance, transfer_pin, unique_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, Username, age, login_pin, account_no, 0.0, transfer_pin, "TEMP"))
    conn.commit()

    unique = generate_unique_id(account_no, Username, name)
    cursor.execute("UPDATE accounts SET unique_id = ? WHERE account_number = ?", (unique, account_no))
    conn.commit()

    print(Fore.GREEN + f"✅ Account created successfully! Your account number is: {account_no}")
    print(f"Welcome {name}!")
    print(Fore.CYAN + "💳 Account Balance: $0.00")
    print(Fore.MAGENTA + f"🔐 Your Unique ID (save this safely — shown once): {unique}")
    print(Fore.YELLOW + "💡 Tip: store the Unique ID in a secure place. It's your recovery key.\n")

    # quick menu after signup
    menu = input('''MAIN MENU
choose an option:
 a. deposit cash
 b. Withdraw cash
 c. Exit
> ''').lower()
    if menu == 'a':
        deposit(account_no, transfer_pin)
    elif menu == 'b':
        withdraw(account_no, transfer_pin)
    elif menu == 'c':
        print("👋 Goodbye!")
        exit()
    else:
        print("Invalid choice.")


# ---------- login & recovery (choice A) ----------
def choice_A():
    ask_Username = input('Enter Username: ')
    cursor.execute('SELECT username, login_pin, account_number, transfer_pin, unique_id, age FROM accounts WHERE username = ?', (ask_Username,))
    row = cursor.fetchone()

    if row is None:
        try_again = input('''Wrong Username! please provide correct username or Sign up instead
 a. Try Username again 
 b. Sign up / Create an Account
 c. Exit
> ''').lower()
        if try_again == 'a':
            return choice_A()
        elif try_again == 'b':
            return choice_B()
        elif try_again == 'c':
            print("👋 Goodbye!")
            exit()
        else:
            print('Invalid option')
            return

    stored_username, stored_pin, account_no, transfer_pin, unique_id, age = row

    ask_Login_pin = input('Enter Login PIN: ')
    if ask_Login_pin != stored_pin:
        print(Fore.RED + '❌ Wrong Login PIN!')
        try_again = input('''a. Try Login PIN again
b. Recover Login PIN using Unique ID
c. Back to main / Exit
> ''').lower()
        if try_again == 'a':
            return choice_A()
        elif try_again == 'b':
            knowname = input('What is your Fullname: ')
            cursor.execute('SELECT unique_id, login_pin FROM accounts WHERE name = ?', (knowname,))
            r = cursor.fetchone()
            if r is None:
                print(Fore.RED + '❌ No account found with that name.')
                return
            stored_unique, stored_lpin = r
            ask_id = input('What is your unique id: ')
            if ask_id != stored_unique:
                print(Fore.RED + '❌ Wrong unique_id.')
                return
            else:
                print(Fore.GREEN + f"✅ Your Login PIN is: {stored_lpin}")
                print("Please keep it safe. Goodbye!")
                exit()
        else:
            return

    # successful login
    print(Fore.GREEN + '✅ Login Successful!')
    print(f'Welcome back {ask_Username}!')

    if age > 60:
        print(Fore.YELLOW + "😂 You're seasoned — still with us in the digital age!")
    elif age < 25:
        print(Fore.YELLOW + "🔥 Young and hungry — let's build something great!")

    menu = input('''\nshow menu 
 a. deposit cash
 b. Withdraw cash
 c. Exit
> ''').lower()

    if menu == 'a':
        deposit(account_no, transfer_pin)
    elif menu == 'b':
        withdraw(account_no, transfer_pin)
    elif menu == 'c':
        print("👋 Goodbye!")
        exit()
    else:
        print("Invalid option.")


# ---------- entry ----------
if choice == 'b':
    choice_B()
elif choice == 'a':
    choice_A()
elif choice == 'c':
    print("👋 Goodbye!")
    exit()
else:
    print("Invalid choice.")
    exit()
