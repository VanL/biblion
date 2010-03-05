from django.conf import settings

DEFAULT_SECTION_CHOICES = [
        ("1", "business"),
        ("2", "technical"),
        ("3", "general"),
    ]


ALL_SECTION_NAME = getattr(settings, "BIBLION_ALL_SECTION_NAME", "all")
SECTIONS = getattr(settings, "BIBLION_SECTIONS", DEFAULT_SECTION_CHOICES)
FULLTEXT_FEED = getattr(settings, "BIBLION_FULLTEXT_FEED", True)


#~
