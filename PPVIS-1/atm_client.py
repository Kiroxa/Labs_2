from pydoc import cli
from bank import ATM, Bank
from user import User, Phone
from db_and_files import Server


class ATMClient:
    __attempts = 3

    def __init__(self, user: User, atm: ATM) -> None:
        self.__atm = atm 
        self.__user = user
        self.__session_phone_number = ""
        self.__session_phone_balance = 0
        # update phone balance
        self.__user.phone.balance = Bank.get_phone_balance(self.user.phone.number)

    @property
    def atm(self) -> ATM:
        return self.__atm

    @property
    def session_phone_number(self) -> str:
        return self.__session_phone_number

    @session_phone_number.setter
    def session_phone_number(self, number) -> None:
        self.__session_phone_number = number

    @property
    def session_phone_balance(self) -> int:
        return self.__session_phone_balance

    @session_phone_balance.setter
    def session_phone_balance(self, cash: int) -> None:
        self.__session_phone_balance += cash

    @property
    def user(self) -> User:
        return self.__user 

    @property
    def true_pin(self) -> str:
        return self.__true_pin

    @classmethod
    def check_attempts(cls) -> None:
        if cls.__attempts == 0:
            print("Card is blocked!")
            raise SystemExit

    def insert_card(self, settings) -> bool:
        ''' Check if inserting card is in the bank database, validate card pin and if all right start session '''
        
        for card_data in Bank.get_cards_data().keys():
            if self.user.card.number == card_data[0]:
                self.__true_pin = card_data[1]

                if self.valid(settings["pin"]):
                    self.session(settings)
                    return True

        print("Uncknown card number!")
        return False
    
    def show_menu(self) -> str:
        ''' User "interface" to provide a session '''
        
        menu_buttons = ['0', '1', '2', '3']
        print(
            "1 - Show balance",
            "2 - Withdraw cash",
            "3 - Phone payment",
            "0 - exit", 
            sep = "\n"
        )
        while True:
            try:
                operation = input("Enter: ")
                if operation not in menu_buttons:
                    raise ValueError
                return operation
            except ValueError as v:
                print("Incorrect button!") 
    
    def session(self, settings = None) -> None:
        ''' Process the input number of operation and call specific functions '''
        
        if settings["balance"]:
            balance = self.get_balance()
            print("Balance: ", balance)
            
        if settings["withdraw"]:
            self.withdraw_cash(settings["withdraw"])
            
        if settings["phone"]:
            self.phone_payment(settings["phone"])
            
        self.save_process(cli=True)
        if settings["save"]:
            print("Save process")
        return
            
        ''' operation = ''
        while operation != '0':
            operation = self.show_menu()

            if operation == '1':
                balance = self.get_balance()
                print("Balance: ", balance)
            elif operation == '2':
                self.withdraw_cash()
            elif operation == '3':
                self.phone_payment()

        # after the closing session, it saves in the json file
        self.save_process() ''' 

    def valid(self, cli_pin = None) -> bool:
        ''' Enter a pin to unlock your card '''
        
        if cli_pin:
            pin = cli_pin
            if not Bank.check_pin(pin, self.true_pin):
                print("Incorrect PIN!")
                exit()
        else:
            print("Enter PIN!")
            exit()
            pin = input("PIN: ")

        while not Bank.check_pin(pin, self.true_pin):
            ATMClient.__attempts -= 1
            ATMClient.check_attempts()
            pin = input("try again! PIN: ")

        # after success
        ATMClient.__attempts = 3
        return True

    def get_balance(self) -> int:
        return Bank.get_card_balance(self.get_card_data())

    def get_card_data(self) -> tuple:
        return (self.user.card.number, self.true_pin)    

    @staticmethod
    def enter_cash() -> int:
        while True:
            try:
                cash = int(input("Enter cash: "))
                break 
            except ValueError as v:
                print("Incorrect number!")
        return cash

    def withdraw_cash(self, cli_cash = None) -> bool:
        ''' Calculate a right cash that user want to withdraw '''
        
        if cli_cash:
            cash = int(cli_cash)
            a = Bank.get_all_sum(self.atm.storage.fund)
            if cash <= a and cash <= self.get_balance():
                money = self.atm.storage.get_money(cash)
                if money:
                    Bank.change_card_balance(self.get_card_data(), -cash)
                    # cash for user
                    self.user.wallet.store = self.atm.cash_out()
                    print("Succesful!")
                    print("Withdraw ", cash)
                    return True
            else:
                print("Not enought money!")
        
        if self.valid():
            while True:
                cash = ATMClient.enter_cash()
                a = Bank.get_all_sum(self.atm.storage.fund)
                # cash VS bank storage sum and cash VS card balance
                if cash <= a and cash <= self.get_balance():
                    money = self.atm.storage.get_money(cash)
                    if money:
                        Bank.change_card_balance(self.get_card_data(), -cash)
                        # cash for user
                        self.user.wallet.store = self.atm.cash_out()
                        print("Succesful!")
                        return True
                else:
                    print("Not enought money!")
                    return

    def phone_payment(self, cli_phone = None) -> bool:
        ''' Input a roght phone number for payment
            input a right cash for paument '''

        phone_number, cash = cli_phone[0], int(cli_phone[1])
            
        while True:
            while True:
                if not phone_number:
                    phone_number = input("Enter phone number: ")

                if Phone.check_phone_number(phone_number):
                    break
                else:
                    print("Incorrect phone number. You should print +375(xx)xxx-xx-xx !")
                    if cli_phone:
                        exit()
                
            self.session_phone_number = phone_number
            self.session_phone_balance = Bank.get_phone_balance(self.session_phone_number)

            if not cash:
                cash = ATMClient.enter_cash()
            card_balance = self.get_balance()

            if 0 < cash <= card_balance:
                Bank.change_card_balance(self.get_card_data(), -cash)
                
                self.session_phone_balance = cash

                if self.user.phone.number == self.session_phone_number:
                    self.user.phone.balance = cash

                print("Succesful!")
                print("Phone ", phone_number, " payment ", cash)
                return True      
            else:
                print("Not enought money or incorrect cash!")     
                return 

    def save_process(self, cli = None) -> None:
        ''' When the sesson is ending (enter - "0") 
            we save all balance changes in the file and database '''
            
        Server.update_bd(self.user.card.number, Bank.get_card_balance((self.user.card.number, self.true_pin)), \
                                                                self.session_phone_number, self.session_phone_balance)

        if Server.save_in_json_file(self):
            if not cli:
                print("Process are saved!")