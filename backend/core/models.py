from django.db import models


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название", unique=True, max_length=15)
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    UNITS = [
        ("грамм", "г"),
        ("килограмм", "кг"),
        ("миллилитры", "мл"),
        ("штуки", "шт"),
        ("столовые ложки", "сл"),
        ("щепотки", "щп"),
        ("по вкусу", "пв"),
    ]

    name = models.CharField(
        verbose_name="Название", unique=True, max_length=20)
    measurement_unit = models.CharField(max_length=20, choices=UNITS)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name
