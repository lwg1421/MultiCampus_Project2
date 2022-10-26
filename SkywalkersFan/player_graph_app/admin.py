from turtle import right
from django.contrib import admin
from .models import player_data
from .models import player_season_data
from .models import center_player
from .models import left_player
from .models import libero_player
from .models import right_player
from .models import setter_player

# Register your models here.
admin.site.register(player_data)
admin.site.register(player_season_data)
admin.site.register(center_player)
admin.site.register(left_player)
admin.site.register(libero_player)
admin.site.register(right_player)
admin.site.register(setter_player)