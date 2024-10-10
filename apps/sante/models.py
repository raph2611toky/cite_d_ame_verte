from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Woman(models.Model):
    id_woman = models.AutoField(primary_key=True)
    
    woman_type = models.OneToOneField(ContentType, on_delete=models.CASCADE)
    woman_id = models.PositiveIntegerField()
    woman = GenericForeignKey('woman_type', 'woman_id')
    
    average_cycle_length = models.IntegerField(default=28)
    last_period_date = models.DateField(null=True, blank=True)
    notification_preference = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.woman)
    
    def update_average_cycle_length(self):
        menstruations = self.menstruations.all()
        if menstruations.count() > 1:
            total_cycle_length = 0
            for m in menstruations:
                if not m.end_date is None:
                    total_cycle_length += (m.end_date - m.start_date).days
            if menstruations.count()-1 == 0:
                self.average_cycle_length = 28
            else:
                self.average_cycle_length = total_cycle_length // (menstruations.count()-1)
            self.save()
    
    class Meta:
        db_table = 'woman'
        
class Menstruation(models.Model):
    id_menstruation = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='menstruations')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    cycle_length = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Cycle from {self.start_date} to {self.end_date} (Duration: {self.cycle_length} days)"

    class Meta:
        db_table = 'menstruation'
        
class Ovulation(models.Model):
    id_ovulation = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='ovulations')
    predicted_ovulation_date = models.DateField()
    fertility_window_start = models.DateField()
    fertility_window_end = models.DateField()
    
    def __str__(self):
        return f"Ovulation on {self.predicted_ovulation_date}"

    class Meta:
        db_table = 'ovulation'
        
class Symptom(models.Model):
    id_symptom = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='symptoms')
    date = models.DateField()
    description = models.TextField()
    
    def __str__(self):
        return f"Symptom on {self.date}: {self.description}"
    
    class Meta:
        db_table = 'symptom'

class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message

    class Meta:
        db_table = 'notification'
