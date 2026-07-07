from typing import Optional
from django.db.models import QuerySet, Q

from word.models import Word, Translation


def check_word_translation(user_answer: str, word_id: int) -> bool:
    """
    Проверяет ответ пользователя на совпадение с сохраненными переводами слова.

    Берет объект слова из базы данных по его идентификатору и сравнивает
    введенный пользователем текст со всеми связанными вариантами перевода
    в модели Translation. Сравнение производится без учета регистра.

    Args:
        user_answer (str): Строка с ответом (переводом), введенная пользователем.
        word_id (int): Идентификатор проверяемого слова в модели Word.
        
    Returns:
        bool: True, если ответ совпал хотя бы с одним корректным переводом,
              иначе False.
    """
    # Доработать приемку от пользователя нескольких переводов иностранного слова
    answer = user_answer.strip().lower()
    translation_check = Translation.objects.filter(word_id=word_id, text__iexact=answer).exists() 

    return translation_check 


def check_word_answer(user_answer: str, word_id: int) -> bool:
    """
    Проверяет ответ пользователя на совпадение с оригинальным изучаемым словом.

    Ищет в базе данных запись с указанным идентификатором и проверяет,
    совпадает ли введенный пользователем текст с полем оригинального 
    иностранного слова. Сравнение производится без учета регистра.

    Args:
        user_answer (str): Строка с ответом (изучаемым словом), введенная пользователем.
        word_id (int): Идентификатор проверяемого слова в модели Word.

    Returns:
        bool: True, если ответ совпал с оригинальным словом, иначе False.
    """

    answer = user_answer.strip()
    word_check = Word.objects.filter(id=word_id, word__iexact=answer).exists()
    
    return word_check


def remove_word_from_session(session: dict, word_id: int) -> list:
    """
    Удаляет идентификатор слова из списка текущей сессии тренировки.

    Ищет переданный word_id в массиве идентификаторов слов, закрепленных
    за текущим раундом повторения в сессии пользователя. Если ID найден,
    удаляет его из списка, чтобы слово больше не выводилось в текущей комнате.

    Args:
        session (dict): Словарь текущей сессии Django (request.session).
        word_id (int): Идентификатор угаданного слова в модели Word.

    Returns:
        list[int]: Обновленный список идентификаторов слов, оставшихся
                   для повторения в текущей сессии.
    """
    words_ids = session.get("words_ids", [])
        
    if word_id in words_ids:
        words_ids.remove(word_id)
    
    return words_ids


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


def get_next_practice_word(words_ids: list[int]) -> Optional[Word]:
    """
    Извлекает объект следующего слова для текущей сессии тренировки.

    Берет идентификатор последнего элемента из списка слов сессии и выполняет
    точечный запрос к базе данных. Если слово успешно найдено, возвращает его
    экземпляр для отображения в интерфейсе тренировочной комнаты.

    Args:
        words_ids (list[int]): Список идентификаторов слов, оставшихся
                               для повторения в текущей сессии.

    Returns:
        Optional[Word]: Объект Word, если он успешно найден в базе данных.
                        Возвращает None, если список ID пуст или запись 
                        была удалена из базы.
    """
    
    if not words_ids:
        return None
    
    next_word_id = words_ids[-1]

    try:
        # можно модорнезировать и тянуть только нужные поля в будущем
        return Word.objects.get(id=next_word_id)
    except Word.DoesNotExist:
        return None
    

def get_next_practice_word_with_translations(words_ids: list[int]) -> Optional[Word]:
    """
    Извлекает объект следующего слова вместе с его вариантами перевода.

    Args:
        words_ids (list[int]): Список уникальных идентификаторов слов, 
                               оставшихся в текущей сессии повторения.

    Returns:
        Optional[Word]: Объект Word со связанными переводами в случае успеха.
                        Возвращает None, если список пуст или слово удалено.
    """
    if not words_ids:
        return None
    
    next_word_id = words_ids[-1]

    try:
        return Word.objects.prefetch_related("translation_set").get(id=next_word_id)
    except Word.DoesNotExist:
        return None
    

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
    """
    
    queryset = Word.objects.filter(Q(word__icontains=text)| Q(translation__text__icontains=text)).distinct()

    return queryset.prefetch_related("translation_set")

