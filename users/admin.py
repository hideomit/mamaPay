from django.contrib import admin

# Register your models here.
from .models import Child
from .models import Balance
from .models import Ticket_holding
from .models import Request
from .models import History


admin.site.register(Child)
admin.site.register(Balance)
admin.site.register(Ticket_holding)
admin.site.register(Request)
admin.site.register(History)
