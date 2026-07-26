from django.db import models
from django.conf import settings

class Expense(models.Model):
    expense_id = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    amount = models.IntegerField()
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.expense_id:
            last = Expense.objects.all().order_by('id').last()
            if last:
                num = int(last.expense_id.split('-')[1]) + 1
            else:
                num = 1
            self.expense_id = f"E-{num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.expense_id