import pytest
import os, sys
from main import ReportProcessor, PerformanceReport, read_csv_files, main


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными"""
    return [
        {
            'name': 'Alex Ivanov',
            'position': 'Backend Developer',
            'completed_tasks': '45',
            'performance': '4.8',
            'skills': 'Python, Django, PostgreSQL, Docker',
            'team': 'API Team',
            'experience_years': '5'
        },
        {
            'name': 'Maria Petrova',
            'position': 'Frontend Developer',
            'completed_tasks': '38',
            'performance': '4.7',
            'skills': 'React, TypeScript, Redux, CSS',
            'team': 'Web Team',
            'experience_years': '4'
        },
        {
            'name': 'John Smith',
            'position': 'Backend Developer',
            'completed_tasks': '29',
            'performance': '4.6',
            'skills': 'Python, ML, SQL, Pandas',
            'team': 'AI Team',
            'experience_years': '3'
        },
        {
            'name': 'Anna Lee',
            'position': 'DevOps Engineer',
            'completed_tasks': '52',
            'performance': '4.9',
            'skills': 'AWS, Kubernetes, Terraform, Ansible',
            'team': 'Infrastructure Team',
            'experience_years': '6'
        }
    ]


class TestPerformanceReport:
    """Тесты для отчета по эффективности"""

    def test_generate_report(self, sample_data):
        """Тест генерации отчета по эффективности"""
        report_generator = PerformanceReport()
        result = report_generator.generate(sample_data)

        # Проверяем структуру результата
        assert len(result) == 3  # 3 уникальные позиции

        # Проверяем вычисление средней эффективности
        backend_devs = [r for r in result if r['position'] == 'Backend Developer'][0]
        expected_avg = (4.8 + 4.6) / 2
        assert backend_devs['performance'] == round(expected_avg, 2)

        # Проверяем сортировку (по убыванию эффективности)
        performances = [r['performance'] for r in result]
        assert performances == sorted(performances, reverse=True)

    def test_empty_data(self):
        """Тест с пустыми данными"""
        report_generator = PerformanceReport()
        result = report_generator.generate([])
        assert result == []


class TestReportProcessor:
    """Тесты для обработчика отчетов"""

    def test_read_csv_files(self):
        """Тест чтения CSV файлов из директории"""
        processor = ReportProcessor()

        # Проверяем существование тестовых файлов
        file1 = 'employees1.csv'
        file2 = 'employees2.csv'

        if not os.path.exists(file1) or not os.path.exists(file2):
            pytest.skip("Тестовые файлы employees1.csv и employees2.csv не найдены")

        data = read_csv_files([file1, file2])

        # Проверяем, что данные прочитаны
        assert len(data) > 0
        assert all(key in data[0] for key in ['name', 'position', 'performance'])

    def test_generate_performance_report(self):
        """Тест генерации отчета performance из реальных файлов"""
        processor = ReportProcessor()

        file1 = 'employees1.csv'
        file2 = 'employees2.csv'

        if not os.path.exists(file1) or not os.path.exists(file2):
            pytest.skip("Тестовые файлы employees1.csv и employees2.csv не найдены")

        result = processor.generate_report('performance', [file1, file2])

        # Проверяем структуру отчета
        assert len(result) > 0
        assert all('position' in row for row in result)
        assert all('performance' in row for row in result)

        # Проверяем, что средняя эффективность вычислена корректно
        for row in result:
            assert isinstance(row['performance'], float)
            assert 0 <= row['performance'] <= 5  # performance обычно в этом диапазоне

    def test_unknown_report(self):
        """Тест с неизвестным отчетом"""
        processor = ReportProcessor()

        file1 = 'employees1.csv'
        if not os.path.exists(file1):
            pytest.skip("Тестовый файл employees1.csv не найден")

        with pytest.raises(ValueError, match="Неизвестный отчет"):
            processor.generate_report('unknown_report', [file1])

    def test_file_not_found(self):
        """Тест с несуществующим файлом"""
        with pytest.raises(FileNotFoundError):
            read_csv_files(['nonexistent_file.csv'])

    def test_single_file(self):
        """Тест с одним файлом"""
        processor = ReportProcessor()

        file1 = 'employees1.csv'
        if not os.path.exists(file1):
            pytest.skip("Тестовый файл employees1.csv не найден")

        data = read_csv_files([file1])
        assert len(data) > 0

        result = processor.generate_report('performance', [file1])
        assert len(result) > 0


class TestMainFunction:
    """Тесты для основной функции main"""

    def test_main_success(self, capsys):
        """Тест успешного запуска main функции"""
        # Сохраняем оригинальные аргументы
        original_argv = sys.argv

        try:
            # Устанавливаем тестовые аргументы
            sys.argv = [
                "main.py",
                "--files", "employees1.csv", "employees2.csv",
                "--report", "performance"
            ]

            # Проверяем существование файлов
            if not os.path.exists("employees1.csv") or not os.path.exists("employees2.csv"):
                pytest.skip("Тестовые файлы employees1.csv и employees2.csv не найдены")

            # Запускаем main
            exit_code = main()

            # Проверяем результат
            captured = capsys.readouterr()
            assert exit_code == 0
            assert "position" in captured.out
            assert "performance" in captured.out

        finally:
            # Восстанавливаем оригинальные аргументы
            sys.argv = original_argv

    def test_main_file_not_found(self, capsys):
        """Тест main с ошибкой файла не найден"""
        original_argv = sys.argv

        try:
            sys.argv = [
                "main.py",
                "--files", "nonexistent_file.csv",
                "--report", "performance"
            ]

            exit_code = main()

            captured = capsys.readouterr()
            assert exit_code == 1
            assert "Ошибка:" in captured.out

        finally:
            sys.argv = original_argv

    def test_main_unknown_report(self, capsys):
        """Тест main с неизвестным отчетом"""
        original_argv = sys.argv

        try:
            sys.argv = [
                "main.py",
                "--files", "employees1.csv",
                "--report", "unknown_report"
            ]

            if not os.path.exists("employees1.csv"):
                pytest.skip("Тестовый файл employees1.csv не найден")

            exit_code = main()

            captured = capsys.readouterr()
            assert exit_code == 1
            assert "Ошибка:" in captured.out

        finally:
            sys.argv = original_argv
