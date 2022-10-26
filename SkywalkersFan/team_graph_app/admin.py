from django.contrib import admin
from .models import score_percentage
from .models import roundrank_count_05_18
from .models import roundrank_count_18_22

# Register your models here.
admin.site.register(score_percentage)
admin.site.register(roundrank_count_05_18)
admin.site.register(roundrank_count_18_22)