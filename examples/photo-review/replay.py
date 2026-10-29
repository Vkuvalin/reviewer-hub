"""Локальный прогон примера: считает обращения к записи, не использует БД."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "repository"))
from quality import apply_after_validation, apply_sequentially

EXPECTED_IDS = ("front", "back", "mark")
CASES = (
    ("Полный набор в другом порядке", ("mark", "front", "back"), 3, 3),
    ("Пропущена фотография", ("front", "back"), 2, 0),
    ("Повторный ID", ("front", "back", "front"), 3, 0),
    ("Посторонний ID", ("front", "back", "other"), 3, 0),
)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    print("Ожидаемый набор: " + ", ".join(EXPECTED_IDS))
    print("Считаются вызовы write_quality в локальной модели.")
    print()
    print("| Ответ AI | Строк | Поэлементно | После проверки набора |")
    print("|---|---:|---:|---:|")
    rejected = []
    for name, returned_ids, expected_sequential, expected_validated in CASES:
        response = [
            {"photo_id": photo_id, "quality": "GOOD"}
            for photo_id in returned_ids
        ]
        sequential_writes = []
        apply_sequentially(
            response,
            lambda photo_id, quality: sequential_writes.append((photo_id, quality)),
        )
        validated_writes = []
        rejection = None
        try:
            apply_after_validation(
                EXPECTED_IDS,
                response,
                lambda photo_id, quality: validated_writes.append((photo_id, quality)),
            )
        except ValueError as error:
            rejection = str(error)
            rejected.append((name, rejection))
        assert len(sequential_writes) == expected_sequential, name
        assert len(validated_writes) == expected_validated, name
        assert (rejection is not None) == (expected_validated == 0), name
        print(
            f"| {name} | {len(response)} | {len(sequential_writes)} "
            f"| {len(validated_writes)} |"
        )
    print()
    for name, reason in rejected:
        print(f"{name}: {reason}")
    print()
    print("Итог: невалидный ответ отклонён до первого вызова записи.")
    print("Граница транзакции реального хранилища в этом стенде не моделируется.")


if __name__ == "__main__":
    main()
