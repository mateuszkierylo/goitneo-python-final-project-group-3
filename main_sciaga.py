from collections import UserDict
from datetime import datetime, timedelta
import pickle



#Classes
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
 


class Name(Field):
    def __init__(self, value):
        if value:  
            self.value = value
        else:
            raise ValueError("Name field is required")

class Phone(Field):
    def __init__(self, value):
        if self.validate_phone(value):
            self.value = value
        else:
            raise ValueError("Invalid phone number: must be 10 digits")
    
    def validate_phone(self, phone):
        return len(str(phone)) == 10
    
class Birthday(Field):
    def __init__(self, value):
        if self.validate_birthday(value):
            self.value = value
        else:
            raise ValueError("Invalid birthday format. DD.MM.YYYY required")

    def validate_birthday(self, birthday):
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)

    def __str__(self):
        phone_str = "; ".join(str(phone) for phone in self.phones)
        birthday_str = f", Birthday: {self.birthday.value}" if self.birthday else ""
        email_str = f", Email: {self.email.value}" if self.email else ""
        return f"Contact name: {self.name.value}, phones: {phone_str}{birthday_str}{email_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)

    def remove_phone(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Contact {name} deleted.")
        else:
            print("Contact not found.")

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def get_birthdays_per_week(self,threshold=7):
        birthday_dict = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}
        today = datetime.today().date()

        for name, record in self.data.items():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                day_of_week = (today + timedelta(days=delta_days)).strftime("%A") if 0 <= delta_days < threshold else None

                if day_of_week in ["Saturday", "Sunday"]:
                    day_of_week = "Monday"

                if day_of_week:
                    birthday_dict[day_of_week].append(name)

        if any(birthday_dict.values()):
            print(f"Birthdays in the next {threshold} days:")
            for day, names in birthday_dict.items():
                if names:
                    print(f"{day}: {', '.join(names)}")
        else:
            print(f"No birthdays in the {threshold} days.")


#Function to load the address book from file
def load_address_book_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        address_book = AddressBook()
        address_book.data = data
        return address_book
    except (FileNotFoundError, EOFError):
        return AddressBook()


#Function to parse user input
def parse_input(user_input):
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, args
    except ValueError:
        return None, None
    

 #Load address book from file   
book = load_address_book_from_file('addressbook.dat')


#BOT

while True:
    user_input = input("Enter command: ").strip()
    cmd, args = parse_input(user_input)

    if cmd == "add":
        try:
            name, phone = args
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            print(f"Contact {name} added with phone number {phone}")

        except ValueError as e:
            print(e)
            print("Invalid command format. Use 'add [name] [phone]'")

    
    elif cmd == "remove_phone":
        try:
            name, phone = args
            record = book.find(name)
            if record:
                phone_found = record.find_phone(phone)
                if phone_found:
                    record.remove_phone(phone)
                    print(f"Phone number {phone} removed for contact {name}.")
                else:
                    print(f"Phone number {phone} not found for contact {name}.")
            else:
                print(f"Contact {name} not found.")

        except ValueError as e:
            print(e)
            print("Invalid command format. Use 'remove-phone [name] [phone]'")


    elif cmd == "change":
        try:
            name, new_phone = args
            record = book.find(name)
            if record:
                record.edit_phone(record.phones[0].value, new_phone)
                print(f"Phone number changed for contact {name}")
            else:
                print(f"Contact not found")
        except ValueError as e:
            print(e)
            print("Invalid command format. Use 'change [name] [new phone]'")

    elif cmd == "phone":
        try:
            name = args[0]
            record = book.find(name)
            if record:
                print(f"Phone number for {name}: {record.phones[0]}")
            else:
                print(f"Contact {name} not found.")
        except IndexError as e:
            print(e)
            print("Invalid command format. Use 'phone [name]'")

    elif cmd == "all":
        if book.data:
            print("All contacts:")
            for record in book.data.values():
                print(record)
        else:
            print("No contacts in the address book.")

    elif cmd == "add-birthday":
        try:
            name, birthday = args
            record = book.find(name)
            if record:
                record.add_birthday(birthday)
                print(f"Birthday added for contact {name}")
            else:
                print(f"Contact {name} not found")
                
        except ValueError as e:
            print(e)
            print("Invalid command format. Use 'add-birthday [name] [birth date]'")

    elif cmd == "show-birthday":
        try:
            name = args[0]
            record = book.find(name)
            if record and record.birthday:
                print(f"Birthday for {name}: {record.birthday}")
            elif record and not record.birthday:
                print(f"No birthday set for {name}")
            else: 
                print(f"Contact {name} not found.")
        except IndexError as e:
            print(e)
            print("Invalid command format. Use 'show-birthday [name]'")

    elif cmd == "birthdays":
        try:
            if args:
                threshold=int(args[0])
                book.get_birthdays_per_week(threshold)
            else:
                book.get_birthdays_per_week()
        except ValueError as e:
            print(e)
            print("Invalid command format. Use 'birthdays [int]'")

    elif cmd == "hello":
        print("Hello!")
    
    elif cmd == "close" or cmd == "exit":
        book.save_to_file('addressbook.dat')
        print("Saving address book and closing the app.")
        break

    else:
        print("Invalid command. Please try again")
