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
        ("g", "грамм"),
        ("kg", "килограмм"),
        ("ml", "миллилитры"),
        ("pcs", "штуки"),
        ("tbsp", "столовые ложки"),
        ("pinch", "щепотки"),
        ("to_taste", "по вкусу"),
    ]

    name = models.CharField(
        verbose_name="Название", unique=True, max_length=20)
    measurement_unit = models.CharField(max_length=10, choices=UNITS)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name
