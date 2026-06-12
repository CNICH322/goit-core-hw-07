from collections import UserDict
from datetime import datetime, date, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен містити 10 цифр")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError(
                "Неправильний формат дати. Використовуйте ДД.ММ.РРРР"
            )


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        return next(
            (p for p in self.phones if p.value == phone),
            None
        )

    def remove_phone(self, phone):
        found = self.find_phone(phone)

        if found:
            self.phones.remove(found)

    def edit_phone(self, old_phone, new_phone):
        found = self.find_phone(old_phone)

        if not found:
            raise ValueError("Телефон не знайдено")

        found.value = Phone(new_phone).value

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(
            phone.value for phone in self.phones
        )

        birthday = (
            self.birthday.value
            if self.birthday
            else "не вказано"
        )

        return (
            f"Ім'я: {self.name.value}, "
            f"Телефони: {phones}, "
            f"День народження: {birthday}"
        )


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name, None)

    def get_upcoming_birthdays(self):
        today = date.today()
        result = []

        for record in self.data.values():

            if not record.birthday:
                continue

            birthday = datetime.strptime(
                record.birthday.value,
                "%d.%m.%Y"
            ).date()

            birthday_this_year = birthday.replace(
                year=today.year
            )

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1
                )

            days_left = (
                birthday_this_year - today
            ).days

            if 0 <= days_left <= 7:

                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)

                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                result.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime(
                        "%d.%m.%Y"
                    )
                })

        return result

    def __str__(self):
        if not self.data:
            return "Адресна книга порожня."

        return "\n".join(
            str(record)
            for record in self.data.values()
        )


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError as error:
            return str(error)

        except IndexError:
            return "Недостатньо аргументів."

        except AttributeError:
            return "Контакт не знайдено."

    return inner


@input_error
def add_contact(args, book):
    name, phone = args

    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)

    record.add_phone(phone)

    return "Контакт успішно додано."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args

    record = book.find(name)
    record.edit_phone(old_phone, new_phone)

    return "Контакт успішно оновлено."


@input_error
def show_phone(args, book):
    record = book.find(args[0])

    return "; ".join(
        phone.value
        for phone in record.phones
    )


@input_error
def add_birthday(args, book):
    name, birthday = args

    record = book.find(name)
    record.add_birthday(birthday)

    return "День народження додано."


@input_error
def show_birthday(args, book):
    record = book.find(args[0])

    if not record.birthday:
        return "Для цього контакту день народження не вказано."

    return record.birthday.value


@input_error
def birthdays(args, book):
    users = book.get_upcoming_birthdays()

    if not users:
        return (
            "Найближчими 7 днями "
            "днів народження немає."
        )

    return "\n".join(
        f"{user['name']} — привітати {user['birthday']}"
        for user in users
    )


def show_all(book):
    return str(book)


def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.lower(), args


def main():
    book = AddressBook()

    print("Ласкаво просимо до бота-помічника!")

    while True:
        user_input = input("\nВведіть команду: ")

        if not user_input.strip():
            print("Невідома команда.")
            continue

        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("До побачення!")
            break

        elif command == "hello":
            print("Чим можу допомогти?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Невідома команда.")


if __name__ == "__main__":
    main()