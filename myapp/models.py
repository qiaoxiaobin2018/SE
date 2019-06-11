from django.db import models
from django.core.validators import MaxValueValidator

class User(models.Model):
    id = models.AutoField(primary_key=True)  #models.BigAutoField
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=32)
    email = models.CharField(unique=True, max_length=40)
    sex = models.CharField(max_length=2)

    class Meta:
        db_table = 'user'

class Footprint1(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    search_content = models.TextField(max_length=1000)

    class Meta:
        managed = True #False
        db_table = 'footprint1'

class Footprint2(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    url = models.CharField(max_length=1000)
    title = models.TextField(max_length=1000)
    time = models.CharField(max_length=20)

    class Meta:
        managed = True #False
        db_table = 'footprint2'

class Collect(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    url = models.CharField(max_length=1000)
    title = models.TextField(max_length=1000)
    time = models.CharField(max_length=20)

    class Meta:
        managed = True  # False
        db_table = 'collect'
