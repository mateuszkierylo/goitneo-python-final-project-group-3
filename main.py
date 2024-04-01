from collections import UserDict
from datetime import datetime, timedelta
import pickle
from fuzzywuzzy import fuzz
import re

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

class Address(Field):
    def __init__(self, value):
        self.value = value

class Email(Field):
    def __init__(self, value):
        self.value = value

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True
        else:
            raise ValueError("Invalid email. Please provide a correct email address")
    
class Birthday(Field):
    def __init__(self, value):
        if self.validate_birthday(value):
            self.value = value
        else:
            raise ValueError("Invalid birthday: Date must be in the past and not more than 100 years ago, format DD.MM.YYYY required")

    def validate_birthday(self, birthday):
        try:
            birthday_date = datetime.strptime(birthday, "%d.%m.%Y")
            today = datetime.today()
            if birthday_date > today:
                return False
            if today - birthday_date > timedelta(days=100*365.25):
                return False
            return True
        except ValueError:
            return False
            
class Note(Field):

    def __init__(self, value, tags=None):
        super().__init__(value)
        self.tags = tags if tags else []

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
        else:
            print("Tag already exists.")

    def remove_tag(self, tag):
        try:
            self.tags.remove(tag)
        except ValueError:
            print("Tag not found.")

    def __str__(self):
        tags_str = ", ".join(self.tags) if self.tags else "No tags"
        return f"{self.value} [Tags: {tags_str}]"


class Record:
    
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = []
        self.birthday = None
        self.note = None
        self.address = []  

    def add_address(self, address):
        if self.address is None:
            self.address =[]
        self.address.append(Address(address))
    
    def remove_address(self, address):
        self.address = []
        print(f"All addressess removed from contact")
    
        
    def add_email(self,email):
        self.email.append(Email(email))
    
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

    def add_note(self, note, tags=None):
        self.note = Note(note, tags)

    def edit_note(self, note):
        if self.note:
            self.note.value = note
        else:
            print("No note to edit. Please add a note first")

    def remove_note(self):
        self.note = None

    def __str__(self):
        phone_str = "; ".join(str(phone) for phone in self.phones) if self.phones else "No phones"
        birthday_str = f", Birthday: {self.birthday.value}" if self.birthday else ""
        address_str = ", Addresses: " + ", ".join(str(address.value) for address in self.address) if self.address else ""
        note_str = f", Note: {self.note}" if self.note != "" else ""
        email_str = ", e-mail:" + ", ".join (str(email.value) for email in self.email) if self.email else ""
        return f"Contact name: {self.name.value}, Phones: {phone_str}{birthday_str}{address_str}{email_str}{note_str}"




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

    def search_by_tag(self, tag):
        matching_records = []
        for record in self.data.values():
            if record.note and tag in record.note.tags:
                matching_records.append(record)
        return matching_records

    def find_by_note(self, pattern):
        matching_contacts = []
        for name, record in self.data.items():
            try:
                if record.note and re.search(pattern, record.note.value, flags=re.IGNORECASE):
                    matching_contacts.append(name)
            except AttributeError:
                # Ignorujemy rekordy bez notatek, ale możemy też tutaj dodać logowanie lub inną obsługę.
                continue  # Kontynuujemy pętlę dla kolejnych rekordów
        return matching_contacts

    def find_by_item(self,item):
        matching_contacts = []
        for name, record in self.data.items():
            if name == item:
                matching_contacts.append(str(record))

            if record.birthday:
                if record.birthday.value == item:
                    matching_contacts.append(str(record))

            if record.email:
                for email in record.email:
                    if email.value == item:
                        matching_contacts.append(str(record))

            if record.phones:
                if record.find_phone(item):
                    matching_contacts.append(str(record))
        if matching_contacts:
            for i in matching_contacts:
                print(i)
  
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
def main():
    print ("-----------------------------------------------------------------------------")
    print("Welcome to Your personal address book. Please provide a command or type help.")
    print ("-----------------------------------------------------------------------------")
    while True:
        
        user_input = input("Enter command: ").strip()
        cmd, args = parse_input(user_input)
        
        if fuzz.ratio(cmd,"add")>66:
            
            if fuzz.ratio(cmd,"add")<100:
                is_ok = input("Did you mean to enter 'add [name] [phone]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"add")==100 or is_ok == "y":     
                try:
                    name, phone = args
                    record = Record(name)
                    record.add_phone(phone)
                    book.add_record(record)
                    print(f"Contact {name} added with phone number {phone}")

                except ValueError as e:
                    print(e)
                    print("Invalid command format. Use 'add [name] [phone]'")

        elif fuzz.ratio(cmd,"remove-phone")>91:
            
            if fuzz.ratio(cmd,"remove-phone")<100:
                is_ok = input("Did you mean to enter 'remove-phone [name] [phone]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"remove-phone")==100 or is_ok == "y":  
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

        elif fuzz.ratio(cmd,"change")>82:
            
            if fuzz.ratio(cmd,"change")<100:
                is_ok = input("Did you mean to enter 'change [name] [new phone]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"change")==100 or is_ok == "y":  
                try:
                    name, new_phone = args
                    record = book.find(name)
                    if record:
                        record.edit_phone(record.phones[0].value, new_phone)
                        print(f"Phone number changed for contact {name}")
                    else:
                        print("Contact not found")
                except ValueError as e:
                    print(e)
                    print("Invalid command format. Use 'change [name] [new phone]'")

        elif fuzz.ratio(cmd,"phone")>79:
            
            if fuzz.ratio(cmd,"phone")<100:
                is_ok = input("Did you mean to enter 'phone [name]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"phone")==100 or is_ok == "y": 
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

        elif fuzz.ratio(cmd,"all")>66:
            
            if fuzz.ratio(cmd,"all")<100:
                is_ok = input("Did you mean to enter 'all'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"all")==100 or is_ok == "y":
                if book.data:
                    print("All contacts:")
                    for record in book.data.values():
                        print(record)
                else:
                    print("No contacts in the address book.")

        elif fuzz.ratio(cmd,"add-birthday")>91:
            
            if fuzz.ratio(cmd,"add-birthday")<100:
                is_ok = input("Did you mean to enter 'add-birthday [name] [birth date]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"add-birthday")==100 or is_ok == "y":
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

        elif fuzz.ratio(cmd,"show-birthday")>91:
            
            if fuzz.ratio(cmd,"show-birthday")<100:
                is_ok = input("Did you mean to enter 'show-birthday [name]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"show-birthday")==100 or is_ok == "y":
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

        elif fuzz.ratio(cmd,"birthdays")>88:
            
            if fuzz.ratio(cmd,"birthdays")<100:
                is_ok = input("Did you mean to enter 'birthdays [int]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"birthdays")==100 or is_ok == "y":
                try:
                    if args:
                        threshold=int(args[0])
                        book.get_birthdays_per_week(threshold)
                    else:
                        book.get_birthdays_per_week()
                except ValueError as e:
                    print(e)
                    print("Invalid command format. Use 'birthdays [int]'")

        elif fuzz.ratio(cmd,"hello")>79:
            
            if fuzz.ratio(cmd,"hello")<100:
                is_ok = input("Did you mean to enter 'hello'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"hello")==100 or is_ok == "y":
                print("Hello!")

        elif fuzz.ratio(cmd,"all")>66:
            
            if fuzz.ratio(cmd,"all")<100:
                is_ok = input("Did you mean to enter 'all'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"all")==100 or is_ok == "y":
                if book.data:
                    print("All contacts:")
                    for record in book.data.values():
                        print(record)
                else:
                    print("No contacts in the address book.")

        elif fuzz.ratio(cmd,"add-birthday")>91:
            
            if fuzz.ratio(cmd,"add-birthday")<100:
                is_ok = input("Did you mean to enter 'add-birthday [name] [birth date]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"add-birthday")==100 or is_ok == "y":
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

        elif fuzz.ratio(cmd,"show-birthday")>91:
            
            if fuzz.ratio(cmd,"show-birthday")<100:
                is_ok = input("Did you mean to enter 'show-birthday [name]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"show-birthday")==100 or is_ok == "y":
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

        elif fuzz.ratio(cmd,"birthdays")>88:
            
            if fuzz.ratio(cmd,"birthdays")<100:
                is_ok = input("Did you mean to enter 'birthdays [int]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"birthdays")==100 or is_ok == "y":
                try:
                    if args:
                        threshold=int(args[0])
                        book.get_birthdays_per_week(threshold)
                    else:
                        book.get_birthdays_per_week()
                except ValueError as e:
                    print(e)
                    print("Invalid command format. Use 'birthdays [int]'")

        elif fuzz.ratio(cmd,"add-note")>91:
            
            if fuzz.ratio(cmd,"add-note")<100:
                is_ok = input("Did you mean to enter 'add-note [name] [note]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"add-note")==100 or is_ok == "y":    
            
                try:
                    name, *note = args
                    note = " ".join(note)
                    record = book.find(name)
                    if record:
                        record.add_note(note)
                        print(f"Note added for contact {name}")
                    else:
                        print(f"Contact {name} not found")

                except ValueError as e:
                    print(e)
                    print("Invalid command format. Use 'add-note [name] [note]'")

        elif fuzz.ratio(cmd,"edit-note")>91:
            
            if fuzz.ratio(cmd,"edit-note")<100:
                is_ok = input("Did you mean to enter 'edit-note [name] [note]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"edit-note")==100 or is_ok == "y":     
                try:
                    name, *note = args
                    note = " ".join(note)
                    record = book.find(name)
                    if record:
                        record.edit_note(note)
                        print(f"Note edited for contact {name}")
                    else:
                        print(f"Contact {name} not found")

                except ValueError as e:
                    
                    print("Invalid command format. Use 'edit-note [name] [new note]")

        elif fuzz.ratio(cmd,"remove-note")>91:
            
            if fuzz.ratio(cmd,"remove-note")<100:
                is_ok = input("Did you mean to enter 'remove-note [name] [note]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"remove-note")==100 or is_ok == "y": 
                try:
                    name = args[0]
                    record = book.find(name)
                    if record:
                        record.remove_note()
                        print(f"Note removed for contact {name}")
                    else:
                        print(f"Contact {name} not found")

                except ValueError as e:
                    
                    print("Invalid command format. Use 'remove-note [name]")

        elif fuzz.ratio(cmd,"find-by-note")>91:
            if fuzz.ratio(cmd,"find-by-note")<100:
                is_ok = input("Did you mean to enter 'find_by_note [pattern]'? (y/n): ").lower()

            if fuzz.ratio(cmd,"find-by-note")==100 or is_ok == "y": 
                if args:
                    pattern = " ".join(args)
                    try:
                        matching_contacts = book.find_by_note(pattern)
                        if matching_contacts:
                            print("Contacts with matching note content:")
                            for name in matching_contacts:
                                print(name)
                        else:
                            print("No contacts found with the given note content.")
                    except re.error as e:
                        print(f"Invalid regex pattern: {e}")
                else:
                    print("Invalid command format. Use 'find_by_note [regex pattern]'")
                    

        elif fuzz.ratio(cmd,"find-by-item")>91:
            if fuzz.ratio(cmd,"find-by-item")<100:
                is_ok = input("Did you mean to enter 'find_by_item [name/birthday/email/number]'? (y//n): ").lower()
                
            if fuzz.ratio(cmd,"find-by-item")==100 or is_ok == "y": 
                try:
                    item = args[0]
                    book.find_by_item(item)
                except IndexError as e:
                    
                    print("Invalid command format. Use 'find_by_item [name/birthday/email/number]'")


        elif fuzz.ratio(cmd,"add-address")>90:
            if fuzz.ratio(cmd,"add-address")<100:
                is_ok = input("Did you mean to enter 'add-address [name] [address]'? (y/n): ").lower()

            if fuzz.ratio(cmd,"add-address")==100 or is_ok == "y":        
                if len(args) < 2:
                    print("Invalid command format. Use 'add-address [name] [address]'.")
                else:
                    try:
                        name = args[0]
                        address = " ".join(args[1:])  
                        record = book.find(name)
                        if record:
                            record.add_address(address)
                            print(f"Address added to contact {name}")
                        else:
                            print(f"Contact {name} not found") 
                    except ValueError as e:
                        print(e)
                        print("Invalid command format. Use 'add-address [name] [address]'")


        elif fuzz.ratio(cmd,"remove-address")>66:

            if fuzz.ratio(cmd,"remove-address")<100:
                is_ok = input("Did you mean to enter 'remove-address'? (y//n): ").lower()

            if fuzz.ratio(cmd,"remove-address")==100 or is_ok == "y":
    
                try:
                    name, address = args
                    record = book.find(name)
                    if record:
                        record.remove_address(address)
                    else:
                        print(f"Contact {name} not found.")
                except ValueError as e:
                    
                    print("Invalid command format. Use 'remove-address [name] [address (you can provie first part of address).]'")

        elif fuzz.ratio(cmd,"add-email")>66:

            if fuzz.ratio(cmd,"add-email")<100:
                is_ok = input("Did you mean to enter 'add-email'? (y//n): ").lower()

            if fuzz.ratio(cmd,"add-email")==100 or is_ok == "y":

        
                try:
                    name, email = args 
                    record = book.find(name)
                    if record:
                        record.add_email(email)
                        print(f"e-mail added to contact {name}")
                    else:
                        print(f"Contact {name} not found")

                except ValueError as e:
                    print("Invalid command format. '")

        elif cmd == "close" or cmd == "exit":
            book.save_to_file('addressbook.dat')
            print("Saving address book and closing the app.")
            break
        
        elif cmd == "save":
            book.save_to_file('addressbook.dat')
            print("Saving your contact list")

        elif cmd == "help" or cmd == "?":
            print ("Avalible commands:")
            print ("1. add [name] [phone_number] - add user name and 10 digits phone number to address book.")
            print ("2. add-email [name] [email address] - adding email to user in adres book")
            print ("3. remove-phone [name] [phone] - removes phone from name")
            print ("4. change [name] [new_phomne] - change phone for specyfic name")
            print ("5. all - lists all record in phone book")
            print ("6. add-birthday [name] [birth_day in (DD.MM.YYYY)] - adding birthday to specyfic name")
            print ("7. show-birthday [name] - show birthday for user")
            print ("8. birhdays [number_days] - users who got birthdays from [number_days]")
            print ("9. NOTES: add-note [name], edit-note [name], remove-note [name] - adding, edit, remove notes from contact name")
            print ("10. find-by-item [item] - finding by item in address book")
            print ("11. add-address [name] - adding addres to user name")
            print ("12. save - saving data to file")
            print ("12. close or exit - exit and save results")

        else:
            print("Invalid command. Please try again")

if __name__ == "__main__":
    main()
