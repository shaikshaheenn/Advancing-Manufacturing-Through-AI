from django.db import models

class PredictiveMaintenance(models.Model):
    machine_id        = models.CharField(max_length=50)
    temperature       = models.FloatField()
    vibration         = models.FloatField()
    pressure          = models.FloatField()
    runtime_hours     = models.FloatField()
    failure_predicted = models.BooleanField(default=False)
    prediction_score  = models.FloatField(default=0.0)
    recorded_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Machine {self.machine_id} - {'FAIL' if self.failure_predicted else 'OK'}"

    class Meta:
        db_table = 'predictive_maintenance'
        ordering = ['-recorded_at']


class QualityControl(models.Model):
    SEVERITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    product_id    = models.CharField(max_length=50)
    defect_type   = models.CharField(max_length=100)
    severity      = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    image         = models.ImageField(upload_to='quality_images/', blank=True, null=True)
    ai_confidence = models.FloatField(default=0.0)
    ai_detected   = models.BooleanField(default=False)
    detected_at   = models.DateTimeField(auto_now_add=True)
    resolved      = models.BooleanField(default=False)

    def __str__(self):
        return f"Product {self.product_id} - {self.defect_type}"

    class Meta:
        db_table = 'quality_control'
        ordering = ['-detected_at']


class ProcessOptimization(models.Model):
    process_name       = models.CharField(max_length=100)
    efficiency_before  = models.FloatField()
    efficiency_after   = models.FloatField()
    improvement_percent= models.FloatField()
    ai_recommendation  = models.TextField()
    applied_at         = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.process_name} - {self.improvement_percent}% improvement"

    class Meta:
        db_table = 'process_optimization'
        ordering = ['-applied_at']


class SupplyChain(models.Model):
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    supplier_name    = models.CharField(max_length=150)
    component        = models.CharField(max_length=100)
    delivery_days    = models.IntegerField()
    price_volatility = models.FloatField(default=0.5)
    past_delays      = models.IntegerField(default=0)
    distance_km      = models.IntegerField(default=500)
    defect_rate      = models.FloatField(default=0.02)
    risk_level       = models.CharField(max_length=20, choices=RISK_CHOICES)
    ai_insight       = models.TextField()
    ai_predicted     = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier_name} - {self.component}"

    class Meta:
        db_table = 'supply_chain'
        ordering = ['-created_at']
