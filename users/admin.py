from django.contrib import admin

# Register your models here.
from .models import Child
from .models import Balance
from .models import Ticket_holding
from .models import Request
from .models import History
from .models import History_ticket

admin.site.register(Child)
admin.site.register(Balance)
admin.site.register(Ticket_holding)
admin.site.register(Request)
admin.site.register(History)
admin.site.register(History_ticket)