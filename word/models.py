import secrets

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

PART_OF_SPEECH = [
    ("unknown", "Unknown"),
    ("noun", "Noun"),
    ("adjective", "Adjective"),
    ("verb", "Verb"),
    ("adverb", "Adverb"),
    ("phrase", "Phrase"),
    ("particle", "Particle"),
    ("preposition", "Preposition"),
    ("pronoun", "Pronoun"),
    ("conjunction", "Conjunction"),
    ("interjection", "Interjection"),
    ("idiom", "Idiom"),  
]


class Word(models.Model):
    word = models.CharField(max_length=255, verbose_name="English word", blank=False)
    part_of_speech = models.CharField(max_length=20, choices=PART_OF_SPEECH, verbose_name="Part of speech", default="unknown")
    transcription = models.CharField(max_length=150, verbose_name="Transcription", blank=True)

    slug = models.SlugField(blank=True, db_index=True, max_length=150, unique=True, verbose_name="Slug name")
    # translation = models.CharField(max_length=255, verbose_name="Translation", blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # В будущем будем подтягивать картинку отображающее слово, автоматически, будет как подсказка на повторении
    image_url = models.URLField(max_length=512, blank=True, null=True, verbose_name="Image URL")

    # Это полезно для реализации интервального повторения.
    difficulty_level = models.IntegerField(default=0, verbose_name="Difficulty level")

    class Meta:
        constraints = [
            # Добавить user для уникальности
            models.UniqueConstraint(fields=["word", "part_of_speech"], name="unique_word_part_of_speech")
        ]
        ordering = ["id"]

    def __str__(self):
        return self.word
    
    @property
    def translations_string(self) -> str:
        """
        Возвращает все варианты перевода слова одной строкой через запятую.

        Использует кэшированные данные в оперативной памяти, если для объекта 
        ранее была выполнена оптимизация запроса с prefetch_related. В противном 
        случае производит ленивое обращение к базе данных.

        Returns:
            str: Строка с перечислениями вариантов перевода, разделенными запятой 
                 и пробелом. Если переводы отсутствуют, возвращает пустую строку.
        """
        translations_all = [t.text for t in self.translation_set.all()] # type:ignore
        return ", ".join(translations_all)

    def save(self, *args, **kwargs) -> None:
        """Генерируем слаг при сохранении"""

        if not self.slug:

            base_slug = slugify(f"{self.word.lower()}-{self.part_of_speech.lower()}")

            if not base_slug:
                base_slug = "some-word-another"

            random_hash = secrets.token_hex(2)

            self.slug = f"{base_slug}-{random_hash}"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("word:word_detail", kwargs={"slug": self.slug})
    

class Translation(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=False, verbose_name="Translation variant")

    def __str__(self) -> str:
        return self.text