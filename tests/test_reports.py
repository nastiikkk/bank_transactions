from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.reports import save_report, spending_by_weekday


@pytest.fixture
def transactions() -> pd.DataFrame:
    """Тестовые транзакции"""
    return pd.DataFrame(
        {
            "Дата операции": [
                "19.10.2026 12:00:00",
                "19.10.2026 15:00:00",
                "20.10.2026 12:00:00",
                "21.10.2026 12:00:00",
                "18.10.2026 12:00:00",
            ],
            "Сумма операции": [-100, -300, -50, -75, -200],
        }
    )


def test_spending_by_weekday(transactions: pd.DataFrame, tmp_path: Path) -> None:
    """Проверяет расчёт средних трат по дням недели"""
    with patch("src.reports.__file__", str(tmp_path / "src" / "reports.py")):
        result = spending_by_weekday(
            transactions,
            date="21.10.2026",
        )

    assert list(result.columns) == ["День недели", "Средние траты"]

    actual = dict(zip(result["День недели"], result["Средние траты"]))

    assert actual["Понедельник"] == pytest.approx(200.0)
    assert actual["Вторник"] == pytest.approx(50.0)
    assert actual["Среда"] == pytest.approx(75.0)


def test_save_report_default_filename(tmp_path: Path) -> None:
    """Проверяет сохранение отчёта с именем по умолчанию"""

    expected = pd.DataFrame({"День": ["Понедельник"], "Траты": [200.0]})

    with patch("src.reports.__file__", str(tmp_path / "src" / "reports.py")):

        @save_report
        def make_report() -> pd.DataFrame:
            return expected

        result = make_report()

    assert result is expected

    saved_file = tmp_path / "reports" / "weekday_report.csv"
    assert saved_file.exists()

    saved_result = pd.read_csv(saved_file)
    pd.testing.assert_frame_equal(saved_result, expected)


def test_save_report_custom_filename(tmp_path: Path) -> None:
    """Проверяет сохранение отчёта с указанным именем файла"""
    expected = pd.DataFrame({"День": ["Вторник"], "Траты": [50.0]})

    with patch("src.reports.__file__", str(tmp_path / "src" / "reports.py")):

        @save_report(filename="custom_report.csv")
        def make_report() -> pd.DataFrame:
            return expected

        result = make_report()

    assert result is expected

    saved_file = tmp_path / "reports" / "custom_report.csv"
    assert saved_file.exists()

    saved_result = pd.read_csv(saved_file)
    pd.testing.assert_frame_equal(saved_result, expected)


def test_save_report_calls_original_function(tmp_path: Path) -> None:
    """Проверяет, что декоратор вызывает исходную функцию"""
    expected = pd.DataFrame({"Траты": [100.0]})
    mock_func: Mock = Mock(return_value=expected)

    with patch("src.reports.__file__", str(tmp_path / "src" / "reports.py")):
        decorated_func = save_report(mock_func)
        result = decorated_func()

    mock_func.assert_called_once_with()
    assert result is expected
