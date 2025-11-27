import csv
from typing import List, Dict, Any
import argparse
from tabulate import tabulate


class ReportGenerator:
    """Базовый класс для генерации отчетов"""

    def generate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Генерирует отчет на основе данных"""
        pass


class PerformanceReport(ReportGenerator):
    """Отчет по эффективности сотрудников"""

    def generate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Генерирует отчет по эффективности

        Args:
            data: Список словарей с данными сотрудников

        Returns:
            Отсортированный список по средней эффективности по позициям
        """
        position_performance = {}
        position_count = {}

        for row in data:
            position = row['position']
            performance = float(row['performance'])

            if position not in position_performance:
                position_performance[position] = 0.0
                position_count[position] = 0

            position_performance[position] += performance
            position_count[position] += 1

        # Вычисляем среднюю эффективность по позициям
        report_data = []
        for position, total_perf in position_performance.items():
            avg_performance = total_perf / position_count[position]
            report_data.append({
                'position': position,
                'performance': round(avg_performance, 2)
            })

        # Сортируем по эффективности (по убыванию)
        report_data.sort(key=lambda x: x['performance'], reverse=True)

        return report_data


def read_csv_files(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Читает данные из CSV файлов

    Args:
        file_paths: Список путей к CSV файлам

    Returns:
        Объединенные данные из всех файлов
    """
    all_data = []

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    all_data.append(row)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла {file_path}: {str(e)}")

    return all_data


class ReportProcessor:
    """Обработчик отчетов"""

    def __init__(self):
        self.reports = {
            'performance': PerformanceReport()
        }

    def generate_report(self, report_name: str, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Генерирует указанный отчет

        Args:
            report_name: Название отчета
            file_paths: Список путей к файлам

        Returns:
            Данные отчета
        """
        if report_name not in self.reports:
            raise ValueError(f"Неизвестный отчет: {report_name}")

        data = read_csv_files(file_paths)
        return self.reports[report_name].generate(data)


def main():
    parser = argparse.ArgumentParser(description='Генератор отчетов из CSV файлов')
    parser.add_argument('--files', nargs='+', required=True,
                        help='Пути к CSV файлам с данными')
    parser.add_argument('--report', required=True,
                        help='Название отчета (performance)')

    args = parser.parse_args()

    processor = ReportProcessor()

    try:
        report_data = processor.generate_report(args.report, args.files)

        # Выводим отчет в виде таблицы
        if report_data:
            print(tabulate(report_data, headers='keys'))
        else:
            print("Нет данных для отображения")

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    main()