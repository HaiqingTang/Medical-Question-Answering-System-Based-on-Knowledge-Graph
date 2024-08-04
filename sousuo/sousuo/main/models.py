from django.db import models
import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sousuo.settings')
# django.setup()


# 用户id, 对应的密码和用户身份('普通用户'或'医生')
class user_id(models.Model):
    uid = models.CharField(max_length=12, primary_key=True)
    password = models.CharField(max_length=18)
    role = models.CharField(max_length=10)


# 用户信息
class user_infomation(models.Model):
    uid = models.ForeignKey(user_id, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    age = models.CharField(max_length=16)
    sex = models.CharField(max_length=16)


# 帖子信息
class post(models.Model):
    post_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(user_id, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    body = models.CharField(max_length=130072)
    date = models.DateTimeField(auto_now=True)


# 回帖信息
class back_post(models.Model):
    back_post_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(post, on_delete=models.CASCADE)
    body = models.CharField(max_length=65536)
    uid = models.ForeignKey(user_id, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)


# 收藏列表
class bookmark(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(user_id, on_delete=models.CASCADE)
    post_id = models.ForeignKey(post, on_delete=models.CASCADE)


# 私信消息
class message(models.Model):
    msg_id = models.AutoField(primary_key=True)
    uid_send = models.ForeignKey(user_id, on_delete=models.CASCADE, related_name='uid_send')
    uid_receive = models.ForeignKey(user_id, on_delete=models.CASCADE, related_name='uid_receive')
    date = models.DateTimeField(auto_now=True)
    msg = models.CharField(max_length=65536)


# 关注列表
class follow_list(models.Model):
    follow_id = models.AutoField(primary_key=True)
    follow_uid = models.ForeignKey(user_id, on_delete=models.CASCADE, related_name='follow_uid')
    be_followed_uid = models.ForeignKey(user_id, on_delete=models.CASCADE, related_name='be_followed_uid')