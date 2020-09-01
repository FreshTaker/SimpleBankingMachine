# This project was developed following Hyperskill.org's "Simple Banking System" project.
# Additional functionality has been added.

import random
import sqlite3
random.seed(1)


class BankMachine:
    accounts = {}
    power = ''

    def activate(self):
        self.power = 'ON'
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute('''DROP TABLE card''')  # Comment out if not debugging.
        self.conn.commit()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS card(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        number TEXT, 
                        pin TEXT, 
                        balance INTEGER DEFAULT 0)''')
        self.conn.commit()

        while self.power == 'ON':
            main_menu = ('''1. Create an account
2. Log into account
0. Exit''')
            print(main_menu)
            menu_input = input()

            if menu_input == '1':  # Create an account
                self.create_account()

            if menu_input == '2':  # Log into account
                self.login()

            if menu_input == '0':  # exit
                print('Bye!')
                self.power == 'OFF'
                # Comment out the following three lines if not debugging.
                #self.cur.execute('SELECT * FROM card')
                #query = self.cur.fetchall()
                #print(query)
                self.conn.close()
                break

    def luhn_checksum(self, number):
        """ Outputs the checksum following the luhn algorithm. """
        sum_num = 0
        counter = 1
        for num in list(number):  # ['4','0',...]
            num = int(num)
            if (counter % 2) != 0:  # If odd digit
                num = num * 2
                if num > 9:
                    num = num - 9
            sum_num += num
            counter += 1
        if sum_num % 10 == 0:
            checksum = '0'
        else:
            checksum = str(10 - (sum_num % 10))
        return checksum

    def create_account(self):
        """ Create an account number and pin """
        # Generate an account number and Pin:
        #  IIN = '400000'  # Not used
        account_id = str(random.randint(400_000_000_000_000, 400_000_999_999_999))
        checksum = self.luhn_checksum(account_id)
        account_number = account_id + checksum
        pin = ''
        for i in range(4):
            pin = str(random.randint(0, 9)) + pin

        # Check to see if this account number already exists:
        self.cur.execute('''SELECT * FROM card WHERE (number = ?)''',
                         [account_number])
        query = self.cur.fetchone()
        if query:
            self.create_account()
        else:
            self.cur.execute("INSERT INTO card(number, pin) VALUES (?,?)", [account_number, pin])
            self.conn.commit()
            print('Your card has been created')
            print('Your card number:')
            print(account_number)
            print('Your card PIN:')
            print(pin)

    def loggedin(self, query):
        """ See balance once logged in """
        loggedin_menu = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit"""

        while True:
            print(loggedin_menu)
            input_lg = input()

            if input_lg == '1':  # Balance
                print('Balance: {}'.format(str(query[3])))

            if input_lg == '2':  # Add income
                print('Enter income:')
                input_income = input()
                self.cur.execute("UPDATE card SET balance = ? WHERE id = ?",
                                 [(float(query[3]) + float(input_income)), query[0]])
                self.conn.commit()
                self.cur.execute('''SELECT * FROM card WHERE id = ?''',
                                 [query[0]])
                query = self.cur.fetchone()
                print('Income was added!')

            if input_lg == '3':  # Do transfer
                print('Enter card number:')
                input_number = input()
                # Check card length:
                if (len(input_number) == 16) and (input_number != query[1]):
                    # check card number for luhn:
                    account_number = input_number[:-1]  # Grabs all but last digit
                    checksum_check = self.luhn_checksum(account_number)
                    if checksum_check == input_number[-1]:
                        # check card number in DB
                        self.cur.execute('''SELECT * FROM card WHERE number = ?''',
                                         [input_number])
                        transfer_to = self.cur.fetchone()
                        if not transfer_to:
                            print('Such a card does not exist.')
                        else:
                            print('Enter how much money you want to transfer:')
                            input_amount = input()
                            # Check if there is enough money:
                            if query[3] < float(input_amount):
                                print('Not enough money!')
                            else:
                                self.cur.executemany('''UPDATE card set balance = ? where number = ?''',
                                                     [(query[3]-float(input_amount), query[1]),
                                                      (float(input_amount), input_number)])
                                self.conn.commit()
                                self.cur.execute('''SELECT * FROM card WHERE id = ?''',
                                                 [query[0]])
                                query = self.cur.fetchone()
                                print('Success!')
                    else:
                        print('Probably you made a mistake in the card number. Please try again!')

            if input_lg == '4':  # Close account
                # Delete account from DB
                self.cur.execute('''DELETE from card WHERE id = ?''', [query[0]])
                self.conn.commit()
                print('The account has been closed')
                break

            if input_lg == '5':  # Log Out
                print('You have successfully logged out!')
                break

            if input_lg == '0':  # Exit
                print('You have successfully logged out!')
                self.power = 'OFF'
                break

    def login(self):
        """ Try to login """
        # Get inputs
        print('Enter your card number:')
        account_input = input()
        print('Enter your PIN:')
        pin_input = input()

        # Test Inputs
        success = 'no'
        self.cur.execute('''SELECT * FROM card WHERE (number = ?) AND (pin = ?)''',
                         [str(account_input), str(pin_input)])
        query = self.cur.fetchone()

        if query:
            success = 'yes'
            print('You have successfully logged in!')
            self.loggedin(query)

        if success == 'no':
            print('Wrong card number or PIN!')


ATM = BankMachine()
ATM.activate()
