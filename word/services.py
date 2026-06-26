from typing import Optional
from django.db.models import QuerySet

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

    answer = user_answer.strip().lower()
    translation_check = Translation.objects.filter(word_id=word_id, text__iexact=answer).exists() 

    return translation_check 


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