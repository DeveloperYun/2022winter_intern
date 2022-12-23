from django.contrib import admin
from .models import MovePos, MoveVel, MoveStartPos, MoveToAbsPos

# Register your models here.
class userMovePos(admin.ModelAdmin):
    list_display = ('lAxisNo','dPos','dVel','dAccel','dDecel')
admin.site.register(MovePos,userMovePos)

class userMoveStartPos(admin.ModelAdmin):
    list_display = ('lAxisNo','dPos','dVel','dAccel','dDecel')
admin.site.register(MoveStartPos,userMoveStartPos)

class userMoveVel(admin.ModelAdmin):
    list_display = ('lAxisNo','dVel','dAccel','dDecel')
admin.site.register(MoveVel,userMoveVel)

class userMoveToAbsPos(admin.ModelAdmin):
    list_display = ('lAxisNo','dPos','dVel','dAccel','dDecel')
admin.site.register(MoveToAbsPos,userMoveToAbsPos)