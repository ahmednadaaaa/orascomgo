from django.db import models

class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('new', 'جديد'),
        ('read', 'مقروء'),
        ('replied', 'تمت الإجابة'),
        ('closed', 'مغلق'),
    )
    
    name = models.CharField(max_length=200, verbose_name="الاسم")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    subject = models.CharField(max_length=500, verbose_name="الموضوع")
    message = models.TextField(verbose_name="الرسالة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="الحالة")
    reply = models.TextField(blank=True, null=True, verbose_name="الرد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"

    def __str__(self):
        return f"{self.name} - {self.subject}"

