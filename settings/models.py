from django.db import models

class CompanySettings(models.Model):
    name = models.CharField(max_length=100, default="Manish Kala Kendra")
    since = models.CharField(max_length=10, default="1989")
    address = models.TextField(default="Karjat, Maharashtra")
    gst = models.CharField(max_length=20, default="27ABCDE1234F1Z5")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Company Settings"