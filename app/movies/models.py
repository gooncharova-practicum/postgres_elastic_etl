import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255, unique=True)
    description = models.TextField(_('description'), null=True, blank=True)

    class Meta:
        db_table = "content\".\"genre"
        indexes = [
            models.Index(fields=['name'], name='genre_name_idx'),
        ]
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        indexes = [
            models.Index(fields=['full_name'], name='person_full_name_idx'),
        ]
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class FilmWork(UUIDMixin, TimeStampedMixin):

    TV_SHOW = 'TV'
    MOVIE = 'MV'
    TYPES = [
        (TV_SHOW, _('tv_show')),
        (MOVIE, _('movie')),
    ]

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateField(_('creation_date'), null=True)
    rating = models.FloatField(
        _('raiting'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    type = models.CharField(_('type'), choices=TYPES, max_length=255)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    class Meta:
        db_table = "content\".\"film_work"
        indexes = [
            models.Index(fields=['creation_date'],
                         name='film_work_creation_date_idx'),
        ]
        verbose_name = _('Film work')
        verbose_name_plural = _('Film works')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        'FilmWork', verbose_name=_('filmwork'), on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        'Genre', verbose_name=_('genre'), on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('Film work genre')
        verbose_name_plural = _('Film work genres')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'genre'],
                                    name='unique genre_filmwork')
        ]


class PersonFilmwork(UUIDMixin):

    ACTOR = 'actor'
    DIRECTOR = 'director'
    WRITER = 'writer'
    TYPES = [
        (ACTOR, _('actor')),
        (DIRECTOR, _('director')),
        (WRITER, _('writer')),
    ]

    film_work = models.ForeignKey(
        'Filmwork', verbose_name=_('filmwork'), on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        'Person', verbose_name=_('person'), on_delete=models.CASCADE
    )
    role = models.TextField(_('role'), choices=TYPES, max_length=255)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('Person in filmwork')
        verbose_name_plural = _('Persons in filmworks')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'],
                                    name='unique filmwork_person_role')
        ]
