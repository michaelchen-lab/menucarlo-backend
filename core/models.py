from django.db import models
from django.contrib.auth.models import User

from django.core.files.base import ContentFile
import pandas as pd
import json
from io import BytesIO

from datetime import datetime
from dateutil import tz

class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analytics")
    start_date = models.DateField()
    end_date = models.DateField()
    update_date = models.DateField()
    data = models.JSONField()

    def save(self, *args, **kwargs):
        ''' On save, change update_date '''
        self.update_date = datetime.now().astimezone(tz.gettz('Singapore'))
        return super(Analytics, self).save(*args, **kwargs)

    def __str__(self):
        return '{}: {} - {}'.format(
            self.user.username,
            self.start_date.strftime(format="%Y%m%d"),
            self.end_date.strftime(format="%Y%m%d")
        )

class Data(models.Model):
    SOURCES = [
        ('Square', 'Square'),
        ('Unknown', 'Unknown')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="data")
    business_name = models.CharField(max_length=100)
    source = models.CharField(choices=SOURCES, max_length=100)
    access_key = models.CharField(max_length=1000, blank=True)
    raw_data = models.FileField()
    parsed_data = models.FileField()
    menu_data = models.FileField()

    def __str__(self):
        return self.business_name

    def read_raw_data(self) -> dict:
        bytes_data = self.raw_data.read()
        json_data = json.load(BytesIO(bytes_data))
        return json_data

    def save_raw_data(self, json_data: dict):
        bytes_data = bytes(json.dumps(json_data), 'utf-8')
        self.raw_data.save('{}_raw'.format(self.pk), ContentFile(bytes_data))

    def read_parsed_data(self, field: str = "parsed_data") -> pd.DataFrame:
        if field == "parsed_data":
            bytes_data = self.parsed_data.read()
        elif field == "menu_data":
            bytes_data = self.menu_data.read()
        else:
            return False

        df = pd.read_csv(BytesIO(bytes_data))
        return df

    def save_parsed_data(self, df: pd.DataFrame, field: str = "parsed_data"):
        file = df.to_csv(index=False)
        file = bytes(file, 'utf-8')

        if field == "parsed_data":
            self.parsed_data.save('{}_parsed'.format(self.pk), ContentFile(file))
        elif field == "menu_data":
            self.menu_data.save('{}_menu'.format(self.pk), ContentFile(file))
        else:
            return False
