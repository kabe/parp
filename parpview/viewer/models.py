from django.db import models
from django.contrib import admin

# Create your models here.

class ViewParam(models.Model):
    """Viewer Parameters.
    """
    DB_TYPES = (
        ("sqlite3", "SQLite3"),
        ("postgres", "PostgreSQL"),
        )
    susp_thresh = models.FloatField()
    sqlite3_file = models.TextField()
    dbtype = models.CharField(max_length=15, choices=DB_TYPES)

admin.site.register(ViewParam)
