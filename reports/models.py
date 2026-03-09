from django.db import models


class Challenge(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title         = models.CharField(max_length=200)
    description   = models.TextField()
    ai_solution   = models.TextField()
    industry_area = models.CharField(max_length=100)
    ai_analysis   = models.TextField(blank=True, null=True)
    severity      = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'challenges'
        ordering = ['-created_at']


class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title           = models.CharField(max_length=200)
    category        = models.CharField(max_length=100)
    description     = models.TextField()
    priority        = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    ai_generated    = models.BooleanField(default=False)
    gemini_response = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'recommendations'
        ordering = ['-created_at']


class Report(models.Model):
    title        = models.CharField(max_length=200)
    content      = models.TextField()
    generated_by = models.CharField(max_length=100)
    report_type  = models.CharField(max_length=50)
    ai_summary   = models.TextField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
