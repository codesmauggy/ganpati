from django.db import models
from django.core.validators import MinValueValidator

class Worker(models.Model):
    CATEGORY_CHOICES = (
        ('Production', 'Production'),
        ('Painter', 'Painter'),
    )
    ATTENDANCE_CHOICES = (
        ('Present', 'Present'),
        ('Half Day', 'Half Day'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    )
    worker_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    operation = models.CharField(max_length=50, blank=True)
    piece_rate = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    today_production = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    monthly_production = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    attendance = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='Present')
    pending_salary = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        if not self.worker_id:
            last = Worker.objects.all().order_by('id').last()
            if last:
                num = int(last.worker_id.split('-')[1]) + 1
            else:
                num = 1
            self.worker_id = f"W-{num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name