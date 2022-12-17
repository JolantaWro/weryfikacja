from django.db import models


class Document(models.Model):
    file_name = models.FileField()


