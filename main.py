import os
import json
import csv
import html


class PriceMachine():

    def __init__(self):
        # Список для хранения данных из всех прайс-листов
        self.data = []

    # В каталоге price_list_analyzer находятся несколько файлов, содержащих прайс-листы от разных поставщиков.
    def load_prices(self, file_path='price_list_analyzer'):  # load_prices - сканирует каталог и загружает данные
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        """
        self.data = []
        for filename in os.listdir(file_path):
            # Количество и название файлов заранее неизвестно,
            # однако точно известно, что в названии файлов прайс-листов есть слово "price".
            if 'price' in filename.lower():
                path = os.path.join(file_path, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=',')
                    headers = next(reader)

                    # Определяем номера столбцов с нужными данными
                    # Порядок колонок в файле заранее неизвестен, но известно, что столбец с
                    # названием товара называется одним из вариантов: "название", "продукт", "товар", "наименование".
                    name_col = self._search_product_price_weight(headers, ["название",
                                                                           "продукт",
                                                                           "товар",
                                                                           "наименование"])
                    # Столбец с ценой может называться "цена" или "розница".
                    price_col = self._search_product_price_weight(headers, ["цена", "розница"])
                    # Столбец с весом имеет название "фасовка", "масса" или "вес" и всегда указывается в килограммах.
                    weight_col = self._search_product_price_weight(headers, ["фасовка", "масса", "вес"])

                    if name_col is not None and price_col is not None and weight_col is not None:
                        for row in reader:
                            try:
                                name = row[name_col].strip()
                                price = float(row[price_col].strip())
                                weight = float(row[weight_col].strip())
                                price_per_kg = price / weight

                                self.data.append({
                                    "name": name,
                                    "price": price,
                                    "weight": weight,
                                    "file": filename,
                                    "price_per_kg": price_per_kg
                                })
                            except ValueError:
                                # Пропуск строк с некорректными данными
                                pass

    def _search_product_price_weight(self, headers, possible_names):
        """
        Возвращает номера столбцов
        """
        for i, header in enumerate(headers):
            if header.lower().strip() in [name.lower() for name in possible_names]:
                return i
        return None

    # export_to_html - выгружает все данные в html файл
    def export_to_html(self, data, file_name='price_list_analyzer/all_data.html'):
        """
        Экспорт данных в HTML файл.
        """
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Позиции продуктов</title>
    <!--
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 5px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
    -->
</head>
<body>
    <table>
        <tr>
            <th>Номер</th>
            <th>Название</th>
            <th>Цена</th>
            <th>Фасовка</th>
            <th>Файл</th>
            <th>Цена за кг.</th>
        </tr>
''')

            for i, item in enumerate(sorted(data, key=lambda x: x["price_per_kg"])):
                f.write(f"<tr><td>{i + 1}</td><td>{html.escape(item['name'])}</td><td>{item['price']}</td>"
                        f"<td>{item['weight']}</td><td>{html.escape(item['file'])}</td>"
                        f"<td>{item['price_per_kg']:.2f}</td></tr>")

            f.write('</table></body></html>')

    # find_text - получает текст и возвращает список позиций, содержащий этот текст в названии продукта.
    def find_text(self, text):
        """
        Поиск товаров по текстовому фрагменту.
        """
        text = text.lower()
        result = [item for item in self.data if text in item['name'].lower()]
        result.sort(key=lambda x: x["price_per_kg"])
        return result


def main():
    pm = PriceMachine()
    pm.load_prices()

    # Интерфейс для поиска реализовать через консоль, циклически получая информацию от пользователя.
    while True:
        user_input = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        # Если введено слово "exit", то цикл обмена с пользователем завершается,
        # программа выводит сообщение о том, что работа закончена и завершает свою работу.
        # В противном случае введенный текст считается текстом для поиска.
        if user_input.lower() == 'exit':
            print("the end")
            break

        # Программа должна загрузить данные из всех прайс-листов и предоставить интерфейс
        # для поиска товара по фрагменту названия с сорторовкой по цене за килогорамм.
        results = pm.find_text(user_input)
        if results:
            # Программа должна вывести список найденных позиций в виде таблицы.
            print(f"{'№':<5}{'Наименование':<30}{'Цена':<10}{'Вес':<10}{'Файл':<15}{'Цена за кг.':<10}")
            for i, item in enumerate(results):
                print(f"{i + 1:<5}{item['name']:<30}{item['price']:<10}{item['weight']:<10}"
                      f"{item['file']:<15}{item['price_per_kg']:<10.2f}")

            # Экспорт найденных данных в HTML
            pm.export_to_html(results, file_name='price_list_analyzer/output.html')
            print("Результаты поиска экспортированы в output.html.")
        else:
            print("Ничего не найдено.")

    # Экспорт всех данных в HTML
    # pm.export_to_html(pm.data)
    # print("Все данные экспортированы в all_data.html.")
    # Не ясно, должна ли программа экспортировать все данные в файл output.html или только результаты поиска.
    # Данная реализация экспортирует в файл output.html результаты поиска.
    # Если программа должна экспортировать все данные в файл output.html то, необходимо
    # раскомментировать 149 и 150 строки кода. В 70 и 150 строке заменить all_data.html на output.html.
    # 143 и 144 строки кода в этом случае следует закомментировать.


if __name__ == "__main__":
    main()
