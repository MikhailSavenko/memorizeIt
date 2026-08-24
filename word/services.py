import json

from django.db.models import QuerySet, Q
from django.core.exceptions import ValidationError

from word.models import Word


def pull_out_words(words_ids: list[int]) -> QuerySet[Word]:
    """
    Получает набор объектов слов по списку их идентификаторов.

    Извлекает из базы данных записи слов, чьи уникальные идентификаторы 
    присутствуют в переданном списке сессии. Запрос автоматически 
    загружает связанные варианты переводов для каждого слова.

    Args:
        words_ids (list[int]): Список идентификаторов слов.

    Returns:
        QuerySet[Word]: Набор объектов Word со связанными переводами.
                        Возвращает пустой набор, если список ID пуст.
    """

    if not words_ids:
        return Word.objects.none()

    return Word.objects.filter(id__in=words_ids).prefetch_related("translation_set")

    
def get_available_words_count() -> int:
    """
    Возвращает общее количество слов, доступных для тренировки.
    
    В будущем сюда добавится фильтрация по конкретному пользователю:
    Word.objects.filter(user=user).count()
    """
    return Word.objects.count()


def get_all_word_ids() -> list[int]:
    """
    Возвращает ids всех слов для тренировки.
    
    В будущем сюда добавится фильтрация по конкретному пользователю:
    Word.objects.filter(user=user)...
    """

    return list(Word.objects.values_list("id", flat=True))


def get_range_word_ids(all_word_ids: list[int], first_num: int, second_num: int) -> list[int]:
    """
    Возвращает срез списка ID слов на основе диапазона пользовательских номеров.

    Автоматически определяет минимальную и максимальную границы диапазона
    и приводит их к индексам Python (с 0).

    Args:
        all_word_ids (list[int]): Полный исходный список идентификаторов.
        first_num (int): Первый номер диапазона.
        second_num (int): Второй номер диапазона.

    Returns:
        list[int]: Вырезанный список идентификаторов для сессии повторения.
    """
    from_num = min(first_num, second_num) - 1
    to_num = max(first_num, second_num)

    return all_word_ids[from_num: to_num]


def get_searched_word(text: str) -> QuerySet[Word]:
    """
    Возвращает оптимизированный набор слов по частичному совпадению с текстом или переводом.

    Ищет совпадения без учета регистра, исключает дубликаты записей Word 
    и подтягивает связанные переводы одной операцией для защиты от N+1.

    Args:
        text (str): Поисковый запрос пользователя.

    Returns:
        QuerySet[Word]: Набор отфильтрованных объектов Word со связанными переводами.

    В будущем сюда добавится фильтрация по конкретному пользователю:
        Word.objects.filter(user=user)
    """
    
    queryset = Word.objects.filter(Q(word__icontains=text)| Q(translation__text__icontains=text)).distinct()

    return queryset.prefetch_related("translation_set")


def calculate_target_page_and_id(search_query: str, paginate_by: int) -> tuple[int | None, int | None]:
    """
    Принимает поисковый запрос и лимит страниц.
    Ищет слово (по №, тексту или переводу) и рассчитывает страницу для прыжка.
    В будущем сюда добавится фильтрация по конкретному пользователю:
        Word.objects.filter(user=user)
    """
    
    word_id = None
    target_page = None

    if search_query.isdigit():
        target_index = int(search_query) - 1
        word_id = Word.objects.all().values_list("id", flat=True)[target_index: target_index+1].first()

    else:
        word_id = Word.objects.filter(Q(word__icontains=search_query)| Q(translation__text__icontains=search_query)).distinct().values_list("id", flat=True).first()

    if word_id:    
        position = Word.objects.filter(id__lt=word_id).count()
        target_page = (position // paginate_by) + 1

    return word_id, target_page


def parse_and_validate_word_ids_json(row_ids_data: str) -> list[int]:
    """Парсит JSON-строку с ID.

    Args:
        row_ids_data: Строка в формате JSON, содержащая массив идентификаторов.

    Raises:
        ValidationError: Если передан некорректный JSON или в массиве 
            отсутствуют валидные целочисленные ID.
    """
    try:
        parsed_data = json.loads(row_ids_data)

    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format for delete!")

    else:
        ids = [x for x in parsed_data if isinstance(x, int)]

        if not ids:
            raise ValidationError("No valid word IDs provided")

        return ids


def bulk_delete_words_by_ids(ids: list[int]) -> None:
    """Прямое каскадное удаление слов из базы данных по списку их идентификаторов.

    Args:
        ids: Список валидных целочисленных первичных ключей (ID) слов.
    """
    # Добавить user=request.user в фильтрацию
    Word.objects.filter(id__in=ids).delete()