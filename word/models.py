from django.db import models

PART_OF_SPEECH = [
    ("noun", "Noun"),
    ("adjective", "Adjective"),
    ("verb", "Verb"),
    ("adverb", "Adverb"),
    ("phrase", "Phrase"),
    ("particle", "Particle"),
    ("preposition", "Preposition"),
    ("another", "Another")
]


class Word(models.Model):
    word = models.CharField(max_length=255, verbose_name="English word", blank=False)
    part_of_speech = models.CharField(max_length=255, choices=PART_OF_SPEECH, verbose_name="Part of speech", default="another", blank=True)
    transcription = models.CharField(max_length=255, verbose_name="Transcription", blank=True)
    translation = models.CharField(max_length=255, verbose_name="Translation", blank=False)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.word}--{self.translation}"