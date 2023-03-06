from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = _('-empty-')
    list_display = ('name',)
    search_fields = ('name', 'description')


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ('genre',)
    min_num = 1


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person', )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', )
    list_filter = ('full_name',)
    search_fields = ('full_name',)


@admin.register(FilmWork)
class FilmworkAdmin(admin.ModelAdmin):
    empty_value_display = _('-empty-')
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = ('title', 'type', 'creation_date', 'rating',)
    list_filter = ('type', 'genres')
    search_fields = ('title', 'description', 'id')
