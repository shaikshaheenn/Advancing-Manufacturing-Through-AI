from django.db import models

class TechnologyModule(models.Model):
    TECH_TYPES = [
        ('xai', 'Explainable AI'),
        ('iot', 'IoT Integration'),
        ('edge', 'Edge Computing'),
        ('hrc', 'Human-Robot Collaboration'),
    ]
    title = models.CharField(max_length=200)
    tech_type = models.CharField(max_length=20, choices=TECH_TYPES)
    description = models.TextField()
    benefits = models.TextField()
    use_cases = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.tech_type})"

    class Meta:
        db_table = 'technology_modules'
