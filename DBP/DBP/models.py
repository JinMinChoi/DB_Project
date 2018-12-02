from django.db import models

# Create your models here.
class Data(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    text = models.TextField()
    community = models.CharField(max_length = 40)
    time = models.CharField(max_length= 20)

    def __str__(self):
        return str(self.id) + "_" + str(self.community) + "_" + str(self.time)
