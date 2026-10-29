"""Минимальная модель порядка проверок и обращений к записи."""

from collections import Counter
from collections.abc import Callable, Mapping, Sequence

WriteQuality = Callable[[str, str], None]
Assessment = Mapping[str, str]


def apply_sequentially(
    response: Sequence[Assessment], write_quality: WriteQuality
) -> None:
    """Проблемный порядок: каждая строка сразу передаётся на запись."""
    for row in response:
        write_quality(row["photo_id"], row["quality"])


def validate_response(
    expected_ids: Sequence[str], response: Sequence[Assessment]
) -> list[tuple[str, str]]:
    """Проверяет весь ответ до первого обращения к записи."""
    expected = set(expected_ids)
    if not expected or len(expected) != len(expected_ids):
        raise ValueError("Некорректный исходный набор фотографий")

    plan = []
    for row in response:
        photo_id = row.get("photo_id")
        quality = row.get("quality")
        if (
            not isinstance(photo_id, str)
            or not isinstance(quality, str)
            or quality not in {"GOOD", "RETAKE"}
        ):
            raise ValueError("Некорректная строка оценки")
        plan.append((photo_id, quality))

    counts = Counter(photo_id for photo_id, _ in plan)
    missing = expected - counts.keys()
    foreign = counts.keys() - expected
    duplicates = {photo_id for photo_id, count in counts.items() if count > 1}
    problems = []
    if missing:
        problems.append("пропущены: " + ", ".join(sorted(missing)))
    if foreign:
        problems.append("посторонние: " + ", ".join(sorted(foreign)))
    if duplicates:
        problems.append("повторены: " + ", ".join(sorted(duplicates)))
    if problems:
        raise ValueError("; ".join(problems))
    return plan


def apply_after_validation(
    expected_ids: Sequence[str],
    response: Sequence[Assessment],
    write_quality: WriteQuality,
) -> None:
    """Сначала готовит полный план; затем передаёт его на запись."""
    plan = validate_response(expected_ids, response)
    for photo_id, quality in plan:
        write_quality(photo_id, quality)
