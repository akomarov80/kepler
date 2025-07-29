from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def get_user_count():
    return User.objects.count()

# @login_required
def user_count_view(request):
    count = get_user_count()

    return render(request, 'counter/user_count.html',
                  context={
                      'count': get_user_count()
                  })