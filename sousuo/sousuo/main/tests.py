from django.test import TestCase
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from main.models import uid_password, uid_power
import random

# 添加用户到数据库
uid = ''
for i in range(10):
    uid += str(random.randint(0, 9))

# u0 = uid_password(uid='1234567890', password='000000')
# u0.save()

uid_password.objects.all().delete()