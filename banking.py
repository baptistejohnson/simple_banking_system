import random
import sqlite3

new_card_number = ''
pin = ''
entered_card_number = ''
transfer_to = None


def create_account():
    create_account_details()
    print("Your card has been created\nYour card number:")
    print(new_card_number)
    print("Your card PIN:")
    print(pin)
    cur.execute("INSERT INTO card (number, pin, balance) VALUES(?, ?, ?)", (new_card_number, pin, 0))
    conn.commit()
    cur.execute('SELECT * FROM card;')
    print(cur.fetchall())
    # conn.commit()
    main_menu()


def log_in():
    global entered_card_number
    entered_card_number = input("Enter your card number:")
    entered_pin = input("Enter your PIN:")
    cur.execute('SELECT number, pin FROM card WHERE number = ?', (entered_card_number,))  # parameter must be tuple hence comma is necessary
    fetched_dets = cur.fetchone()
    conn.commit()
    if fetched_dets is None:
        print("Wrong card number or PIN!")
        main_menu()
    elif (entered_card_number == fetched_dets[0]) and (entered_pin == fetched_dets[1]):
        print("You have successfully logged in!")
        secondary_menu()
    else:
        print("Wrong card number or PIN!")
        main_menu()


def main_menu():
    print("1. Create an account\n2. Log into account\n0. Exit")
    dec = input()
    if dec == "1":
        create_account()
    elif dec == "2":
        log_in()
    else:
        exit_function()


def secondary_menu():
    print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
    dec1 = input()
    if dec1 == "1":
        cur.execute('SELECT balance FROM card WHERE number = ?', (entered_card_number,))  # parameter must be tuple hence comma is necessary
        conn.commit()
        fetched_balance = cur.fetchone()
        print("Balance:", fetched_balance[0])
        secondary_menu()
    elif dec1 == "2":
        add_income()
    elif dec1 == "3":
        transfer()
    elif dec1 == "4":
        close_account()
    elif dec1 == "5":
        print("You have successfully logged out!")
        main_menu()
    elif dec1 == "0":
        exit_function()


def exit_function():
    print("Bye!")


def sum_digits(n):
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s


def create_account_details():
    ii_number = "400000"
    customer_number = str(random.randint(0, 999999999))
    while len(customer_number) < 9:
        customer_number = "0" + customer_number
    card_num_min_checks = int(ii_number + customer_number)
    # make list of digits of card number excluding checksum
    list_of_digits = [int(i) for i in str(card_num_min_checks)]
    # we begin operation to calculate checksum for new number
    # multiply odd digits by 2
    for n, i in enumerate(list_of_digits):
        if n % 2 == 0:
            list_of_digits[n] = i * 2
    # subtract 9 to numbers over 9
    list_of_digits = [x - 9 if x > 9 else x for x in list_of_digits]
    # join list into integer
    dummy_card_num_min_checks = int("".join(str(e) for e in list_of_digits))
    # calculate checksum
    if sum_digits(dummy_card_num_min_checks) % 10 == 0:
        checksum = 0
    else:
        checksum = 10 - (sum_digits(dummy_card_num_min_checks) % 10)
    # putting this all together to get full card number
    global new_card_number
    global pin
    new_card_number = str(card_num_min_checks) + str(checksum)
    pin = str(random.randint(0, 9999))
    while len(pin) < 4:
        pin = "0" + pin


def add_income():
    money_added = int(input('Enter income:'))
    cur.execute('SELECT balance FROM card WHERE number = ?', (entered_card_number,))  # parameter must be tuple hence comma is necessary
    conn.commit()
    fetched_balance = cur.fetchone()
    # print(fetched_balance)
    cur.execute('UPDATE card SET balance = ? + ? WHERE number = ?', (fetched_balance[0], money_added, entered_card_number))
    conn.commit()
    print("Income was added!")
    # cur.execute('SELECT * FROM card;')
    # print(cur.fetchall())
    secondary_menu()


def close_account():
    cur.execute('DELETE FROM card WHERE number = ?', (entered_card_number,))
    conn.commit()
    print("The account has been closed!")
    cur.execute('SELECT * FROM card;')
    print(cur.fetchall())
    main_menu()


def transfer():
    global transfer_to
    transfer_to = int(input("Enter card number:"))
    check_luhn(transfer_to)


def check_luhn(n_):
    # check luhn algorithm
    card_minus_checksum = n_ // 10
    # print(card_minus_checksum)
    list_of_digits = [int(i) for i in str(card_minus_checksum)]
    # print(list_of_digits)
    for n, i in enumerate(list_of_digits):
        if n % 2 == 0:
            list_of_digits[n] = i * 2
    # print(list_of_digits)
    # subtract 9 to numbers over 9
    list_of_digits = [x - 9 if x > 9 else x for x in list_of_digits]
    # print(list_of_digits)
    checksum = n_ % 10
    # print(checksum)
    card_sum = sum(list_of_digits) + checksum
    # print(card_sum)
    if card_sum % 10 == 0 and len(str(n_)) == 16:
        check_num_against_db()
    else:
        print('Probably you made mistake in the card number. Please try again!')
        secondary_menu()


def check_num_against_db():
    cur.execute('SELECT number FROM card WHERE number = ?', (transfer_to,))  # parameter must be tuple hence comma is necessary
    conn.commit()
    fetched_numb = cur.fetchone()
    # print(fetched_numb)
    if fetched_numb is None:
        print("Such a card does not exist.")
        secondary_menu()
    elif fetched_numb[0] == entered_card_number:
        print("You can't transfer money to the same account!")
        secondary_menu()
    else:
        money_transfer(fetched_numb[0])


def money_transfer(n):
    amount_to_trans = int(input("Enter how much money you want to transfer:"))
    cur.execute('SELECT balance FROM card WHERE number = ?', (entered_card_number,))  # parameter must be tuple hence comma is necessary
    conn.commit()
    curr_balance_giv = cur.fetchone()[0]
    if amount_to_trans > curr_balance_giv:
        print("Not enough money!")
        secondary_menu()
    else:
        cur.execute('SELECT balance FROM card WHERE number = ?', (n,))  # parameter must be tuple hence comma is necessary
        conn.commit()
        curr_balance_rec = cur.fetchone()[0]  # curr.fetchone() is a tuple so index with [0] to get just the balance
        # print(curr_balance_rec)
        cur.execute('SELECT * FROM card;')
        # print(cur.fetchall())
        cur.execute('UPDATE card SET balance = ? + ? WHERE number = ?', (curr_balance_rec, amount_to_trans, n))
        conn.commit()
        # print(curr_balance_giv)
        cur.execute('UPDATE card SET balance = ? - ? WHERE number = ?', (curr_balance_giv, amount_to_trans, entered_card_number))
        conn.commit()
        # cur.execute('SELECT * FROM card;')
        # print(cur.fetchall())
        print("Success!")
        secondary_menu()


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS card (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      number TEXT,
                      pin TEXT,
                      balance INTEGER DEFAULT 0
     );""")
conn.commit()
# cur.execute('DELETE FROM card')
# conn.commit()

# cur.execute('DROP TABLE card;')
# conn.commit()

cur.execute('SELECT * FROM card;')
print(cur.fetchall())

conn.commit()

main_menu()
