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