from django.shortcuts import get_object_or_404
from word.models import Word


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
    word = get_object_or_404(Word, id=word_id)
    translation_check = word.translation_set.filter(text__iexact=answer).exists() # type: ignore

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