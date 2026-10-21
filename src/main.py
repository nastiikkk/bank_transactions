from src.reports import spending_by_weekday
from src.utils import read_excel_file
from src.views import main as get_main_page


def main() -> None:
    """Запускает приложение"""
    while True:
        print("=== Банковское приложение ===")
        print("1. Главная страница")
        print("2. Отчёт по дням недели")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            date = input("Введите дату (ДД.ММ.ГГГГ): ")
            period = input("Период (W - неделя, M - месяц, Y - год, ALL - всё): ")

            result = get_main_page(date, period)
            print(result)



        elif choice == "2":

            transactions = read_excel_file()

            choice_date = input(

                "Хотите указать дату, для которой рассчитать средние траты по дням недели? (да/нет): "

            ).lower()

            if choice_date == "да":

                date = input("Введите дату (ДД.ММ.ГГГГ): ")

                report = spending_by_weekday(transactions, date=date)

            else:

                report = spending_by_weekday(transactions)

            print(report.to_string(index=False))

        elif choice == "0":
            print("До встречи!")
            break

        else:
            print("Некорректный выбор. Попробуйте ещё раз.")


if __name__ == "__main__":
    main()
