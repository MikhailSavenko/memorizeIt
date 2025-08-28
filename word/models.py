from django.db import models

PART_OF_SPEECH = [
    ("noun", "Noun/Существительное"),
    ("adjective", "Adjective/Прилагательное"),
    ("verb", "Verb/Глагол"),
    ("adverb", "Adverb/Наречие"),
    ("phrase", "Phrase/Фраза"),
    ("particle", "Particle/Частица"),
    ("preposition", "Preposition/Предлог"),
    ("pronoun", "Pronoun/Местоимение"),
    ("another", "Another/Другое(Когда не знаешь)")
]


class Word(models.Model):
    word = models.CharField(max_length=255, verbose_name="English word", blank=False)
    part_of_speech = models.CharField(max_length=255, choices=PART_OF_SPEECH, verbose_name="Part of speech", default="another", blank=True)
    transcription = models.CharField(max_length=255, verbose_name="Transcription", blank=True, null=True)
    translation = models.CharField(max_length=255, verbose_name="Translation", blank=False)

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["word", "part_of_speech"], name="unique_word_part_of_speech")
        ]

    def __str__(self):
        return f"{self.word}--{self.translation}"
    
