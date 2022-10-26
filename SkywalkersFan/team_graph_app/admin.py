from django.contrib import admin
from .models import score_percentage
from .models import roundrank_count_05_18
from .models import roundrank_count_18_22
from .models import seasonrank
from .models import clean_sheet
from .models import home_away_2021
from .models import home_away_all
from .models import relative_record_2021
from .models import relative_record_all
from .models import upset

# Register your models here.
admin.site.register(score_percentage)
admin.site.register(roundrank_count_05_18)
admin.site.register(roundrank_count_18_22)
admin.site.register(seasonrank)
admin.site.register(clean_sheet)
admin.site.register(home_away_2021)
admin.site.register(home_away_all)
admin.site.register(relative_record_2021)
admin.site.register(relative_record_all)
admin.site.register(upset)