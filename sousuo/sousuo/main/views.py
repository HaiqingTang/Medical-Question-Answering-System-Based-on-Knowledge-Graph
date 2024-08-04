from django.shortcuts import render, redirect, reverse
from main.models import user_id, user_infomation, post, back_post, bookmark, message, follow_list
import random
from django.db.models import Q


# 判断当前是否登录
def user_is_login(request):
    uid = request.COOKIES.get('uid')
    sessionUid = request.session.get('uid', 'noUid')
    isLogin = request.session.get('is_login', False)
    if (str(uid) == str(sessionUid) and isLogin == True):
        return True
    else:
        return False

# 主页
def homepage(request):
    if request.method == 'GET':
        if user_is_login(request):
            return render(request, 'homepage/index.html')
        else:
            return redirect(reverse('signIn'))
    elif request.method == 'POST':
        if 'signOut' in request.POST:
            request.session.flush()
            return redirect(reverse('signIn'))

        if 'search' in request.POST:
            searchInfo = request.POST.get('searchText')
            return redirect(f'''search/{searchInfo}/''')


# 注册
def signUp(request):
    if request.method == 'GET':
        return render(request, 'signUp/index.html')
    elif request.method == 'POST':
        password0 = request.POST.get('userPassword0')
        password1 = request.POST.get('userPassword1')
        role = request.POST.get('role')
        if password0 != password1:
            msg = {'text': '两次输入的密码不一致，请重新输入！'}
            return render(request, 'signUp/index.html', msg)

        uid = ''
        for i in range(10):
            uid += str(random.randint(0, 9))
        while(True):
            if user_id.objects.filter(uid=uid).exists():
                uid = ''
                for i in range(10):
                    uid += str(random.randint(0, 9))
            else:
                user = user_id(uid=uid, password=password0, role=role)
                user.save()
                user_info = user_infomation(uid=user, name='张三', age='隐藏', sex='隐藏')
                user_info.save()
                break
        msg = {'text': f'''注册成功!
请牢记您的账号密码：
帐号: {uid}
密码：{password0}'''}
        msg['success'] = 'y'
        return render(request, '', msg)



# 登陆页面
def signIn(request):
    if request.method == 'GET':
        return render(request, 'SignIn/index.html')
    elif request.method == 'POST':
        msg = {}
        uid = request.POST.get('userId')
        password = request.POST.get('userPassword')
        if not user_id.objects.filter(uid=uid).exists():
            msg['text'] = '账号不存在！'
            return render(request, 'signIn/index.html', msg)
        user = user_id.objects.get(uid=uid)
        if user.password != password:
            msg['text'] = '密码错误！'
            return render(request, 'signIn/index.html', msg)
        # 账号密码都正确，记录登陆状态，进入主页
        homepage = redirect(reverse('homepage'))
        uid = uid
        homepage.set_cookie('uid', uid, max_age=3600 * 24 * 7)
        request.session.set_expiry(3600 * 24 * 7)
        request.session['uid'] = uid
        request.session['is_login'] = True
        return homepage


# 修改密码页面
def changePassword(request):
    if request.method == 'GET':
        if user_is_login(request):
            return render(request, 'changePassword/index.html')
        else:
            return redirect(reverse('signIn'))
    elif request.method == 'POST':
        if 'changePassword' in request.POST:
            password = user_id.objects.get(uid=request.session.get('uid')).password
            oldPassword = request.POST.get('oldPassword')
            newPassword0 = request.POST.get('newPassword0')
            newPassword1 = request.POST.get('newPassword1')
            if password != oldPassword:
                msg = {'text': '密码错误!'}
                return render(request, 'changePassword/index.html', msg)
            else:
                if newPassword0 != newPassword1:
                    msg = {'text': '两次输入的密码不一致!'}
                    return render(request, 'changePassword/index.html', msg)
                else:
                    msg = {'text': '密码修改成功！请重新登录'}
                    user = user_id.objects.get(uid=request.session.get('uid'))
                    user.password = newPassword0
                    user.save()
                    request.session.flush()
                    return render(request, 'signIn/index.html', msg)


# 我的信息页面
def myInfo(request):
    if request.method == 'GET':
        if user_is_login(request):
            user = user_infomation.objects.get(uid=user_id.objects.get(uid=request.session.get('uid')))
            role = user_id.objects.get(uid=request.session.get('uid')).role
            msg = {
                'uid': request.session.get('uid'),
                'name': user.name,
                'age': user.age,
                'sex': user.sex,
                'role': role
            }
            return render(request, 'myInfo/index.html', msg)
        else:
            return redirect(reverse('signIn'))
    elif request.method == 'POST':
        if 'changeInfo' in request.POST:
            user = user_infomation.objects.get(uid=user_id.objects.get(uid=request.session.get('uid')))
            role = user_id.objects.get(uid=request.session.get('uid')).role
            msg = {
                'uid': request.session.get('uid'),
                'name': user.name,
                'age': user.age,
                'sex': user.sex,
                'role': role
            }
            return render(request, 'myInfo/changeMyInfo.html', msg)
        elif 'change' in request.POST:
            userInfo = user_infomation.objects.get(uid=user_id.objects.get(uid=request.session.get('uid')))
            userInfo.name = request.POST.get('name')
            userInfo.sex = request.POST.get('sex')
            userInfo.age = request.POST.get('age')
            userInfo.save()
            return redirect(reverse('myInfo'))
        elif 'changePassword' in request.POST:
            return redirect(reverse('changePassword'))


# 搜索结果页面
def searchResult(request, question):
    if request.method == 'GET':
        if user_is_login(request):
            msg = {'searchText': question}
            return render(request, 'searchResult/index.html', msg)
        else:
            return redirect(reverse('signIn'))


class post0():
    def __init__(self, postId, title, uName, date, uid):
        self.postId = postId
        self.title = title
        self.uName = uName
        self.date = date
        self.uid = uid
# 交流区页面
def exchangeArea(request):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        if 'getMore' not in request.GET:
            post_num = 10 if 10 < post.objects.count() else post.objects.count()
            msg = {}
            posts = []
            for i in range(post_num):
                post_info_class = post.objects.all().order_by('-date')[i]
                post_info = post0(postId=post_info_class.post_id,
                                  title=post_info_class.title,
                                  uName=user_infomation.objects.get(uid=post_info_class.uid).name,
                                  date=post_info_class.date,
                                  uid=post_info_class.uid.uid)
                posts.append(post_info)
            msg['posts'] = posts
            num0 = post.objects.count()
            msg['num0'] = num0
            page = render(request, 'exchangeArea/index.html', msg)
            page.set_cookie('postsNum', post_num)
            return page
        else:
            post_num = int(request.COOKIES.get('postsNum'))
            if post_num + 10 < post.objects.count():
                post_num += 10
            else:
                post_num = post.objects.count()
            msg = {}
            posts = []
            for i in range(post_num):
                post_info_class = post.objects.all().order_by('-date')[i]
                post_info = post0(postId=post_info_class.post_id,
                                  title=post_info_class.title,
                                  uName=user_infomation.objects.get(uid=post_info_class.uid).name,
                                  date=post_info_class.date,
                                  uid=post_info_class.uid.uid)
                posts.append(post_info)
            msg['posts'] = posts
            page = render(request, 'exchangeArea/index.html', msg)
            page.set_cookie('postsNum', post_num)
            return page


    elif request.method == 'POST':
        return redirect(reverse('makePost'))


# 发表帖子页面
def makePost(request):
    if request.method == 'GET':
        if user_is_login(request):
            return render(request, 'makePost/index.html')
        else:
            return redirect(reverse('signIn'))
    elif request.method == 'POST':
        if 'upload' in request.POST:
            uid = user_id.objects.get(uid=request.session.get('uid'))
            title = request.POST.get('title')
            body = request.POST.get('body')
            post0 = post(uid=uid, title=title, body=body)
            post0.save()
            return redirect(f'''/post/{post0.post_id}/''')

# 回复的信息
class backPostInfo():
    def __init__(self, name, date, body, uid):
        self.name = name
        self.date = date
        self.body = body
        self.uid = uid
# 帖子页面
def lookPost(request, postId):
    if request.method == 'GET':
        if user_is_login(request):
            postInfo = post.objects.get(post_id=postId)
            author = user_infomation.objects.get(uid=postInfo.uid)
            authorRole = user_id.objects.get(uid=author.uid.uid).role
            # 查看用户是否已经收藏该文章
            if bookmark.objects.filter(uid=user_id.objects.get(uid=request.session.get('uid')), post_id=postInfo).exists():
                isMark = True
            else:
                isMark = False
            # 获取回帖
            back_posts_class = back_post.objects.filter(post_id=post.objects.get(post_id=postId)).order_by('-date')
            back_posts = []
            for i in range(len(back_posts_class)):
                back_post0 = back_posts_class[i]
                back_posts.append(backPostInfo(name=user_infomation.objects.get(uid=back_post0.uid).name,
                                               date=back_post0.date,
                                               body=back_post0.body,
                                               uid=back_post0.uid.uid))
            msg = {
                'uid': postInfo.uid.uid,
                'authorName': author.name,
                'authorRole': authorRole,
                'title': postInfo.title,
                'body': postInfo.body,
                'date': postInfo.date,
                'postId': postId,
                'back_posts': back_posts,
                'isMark': isMark,
            }
            return render(request, 'post/index.html', msg)
        else:
            return redirect(reverse('signIn'))

    elif request.method == 'POST':
        if 'reply' in request.POST:
            post_id_class = post.objects.get(post_id=postId)
            uid_class = user_id.objects.get(uid=request.session.get('uid'))
            body = request.POST.get('body')
            back_post_class = back_post(post_id=post_id_class, body=body, uid=uid_class)
            back_post_class.save()
            return redirect(f'''/post/{postId}/''')
        elif 'cancelMark' in request.POST:
            bookmark.objects.get(uid=user_id.objects.get(uid=request.session.get('uid')),
                                 post_id = post.objects.get(post_id=postId)).delete()
            return redirect(f'''/post/{postId}/''')
        elif 'mark' in request.POST:
            bookmark(uid=user_id.objects.get(uid=request.session.get('uid')),
                     post_id=post.objects.get(post_id=postId)).save()
            return redirect(f'''/post/{postId}/''')



# 查看别的用户信息
def lookUserInfo(request, uid):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        userId = uid
        userInfo = user_infomation.objects.get(uid=user_id.objects.get(uid=uid))
        if follow_list.objects.filter(follow_uid=user_id.objects.get(uid=request.session.get('uid')),
                                      be_followed_uid=user_id.objects.get(uid=uid)).exists():
            isFollow = True
        else:
            isFollow = False
        msg={
            'uid': userId,
            'uName': userInfo.name,
            'role': user_id.objects.get(uid=uid).role,
            'age': userInfo.age,
            'sex': userInfo.sex,
            'isFollow': isFollow,
        }
        return render(request, 'userInfo/index.html', msg)
    elif request.method == 'POST':
        if 'cancelFollow' in request.POST:
            follow_list.objects.filter(follow_uid=user_id.objects.get(uid=request.session.get('uid')),
                                       be_followed_uid=user_id.objects.get(uid=uid)).delete()
            return redirect(f'''/info/{uid}/''')
        elif 'follow' in request.POST:
            follow_list(follow_uid=user_id.objects.get(uid=request.session.get('uid')),
                        be_followed_uid=user_id.objects.get(uid=uid)).save()
            return redirect(f'''/info/{uid}/''')


class markPostInfo():
    def __init__(self, title, postId):
        self.title = title
        self.postId = postId
# 我收藏的帖子页面
def myMark(request):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        posts = []
        msg = {}
        for mark in bookmark.objects.filter(uid=user_id.objects.get(uid=request.session.get('uid'))):
            post0 = mark.post_id
            title = post0.title
            postId = post0.post_id
            posts.append(markPostInfo(title=title, postId=postId))
        msg['markPosts'] = posts
        return render(request, 'myMark/index.html', msg)


# 我发表的所有帖子
def myPosts(request):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        msg = {}
        posts = []
        for post0 in post.objects.filter(uid=user_id.objects.get(uid=request.session.get('uid'))):
            posts.append({'title': post0.title,
                          'postId': post0.post_id})
        msg['posts'] = posts
        return render(request, 'myPosts/index.html', msg)
    elif request.method == 'POST':
        if 'deletePost' in request.POST:
            postId = request.POST.get('deletePost')
            post.objects.get(post_id=postId).delete()
        return redirect(reverse('myPosts'))


# 我的关注
def myFollow(request):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        msg = {}
        users = []
        for followObj in follow_list.objects.filter(follow_uid=user_id.objects.get(uid=request.session.get('uid'))):
            users.append({
                'uid': followObj.be_followed_uid.uid,
                'name': user_infomation.objects.get(uid=followObj.be_followed_uid).name
            })
        msg['users'] = users
        return render(request, 'myFollow/index.html', msg)


# 私信页面
def sendMessage(request, uid):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        if 'getMore' in request.GET:
            dic = {}
            dic['uid'] = uid
            msgs_obj = message.objects.filter(
                (Q(uid_send=user_id.objects.get(uid=request.session.get('uid')))&
                Q(uid_receive=user_id.objects.get(uid=uid)))
                |
                (Q(uid_send=user_id.objects.get(uid=uid))&
                 Q(uid_receive=user_id.objects.get(uid=request.session.get('uid'))))
            ).order_by('date')
            msgs = []
            for msg in msgs_obj:
                msgs.append({
                    'name': user_infomation.objects.get(uid=msg.uid_send).name,
                    'time': msg.date,
                    'msg': msg.msg
                })
            dic['msgs'] = msgs
            return render(request, 'message/index.html', dic)
        else:
            dic = {}
            dic['uid'] = uid
            msgs_obj = message.objects.filter(
                (Q(uid_send=user_id.objects.get(uid=request.session.get('uid'))) &
                 Q(uid_receive=user_id.objects.get(uid=uid)))
                |
                (Q(uid_send=user_id.objects.get(uid=uid)) &
                 Q(uid_receive=user_id.objects.get(uid=request.session.get('uid'))))
            ).order_by('-date')
            print(len(msgs_obj))
            if len(msgs_obj) > 6:
                msgs_obj = msgs_obj[:6]
            print(len(msgs_obj))
            msgs = []
            for msg in msgs_obj:
                msgs.append({
                    'name': user_infomation.objects.get(uid=msg.uid_send).name,
                    'time': msg.date,
                    'msg': msg.msg
                })
            msgs.reverse()
            dic['msgs'] = msgs
            return render(request, 'message/index.html', dic)

    elif request.method == 'POST':
        if 'sendMessage' in request.POST:
            uid_send = user_id.objects.get(uid=request.session.get('uid'))
            uid_receive = user_id.objects.get(uid=uid)
            msg = request.POST.get('message')
            message(uid_send=uid_send, uid_receive=uid_receive, msg=msg).save()
            return redirect(f'''/sendMessage/{uid}/''')


# 我的消息页面
def myMessage(request):
    if not user_is_login(request):
        return redirect(reverse('signIn'))
    if request.method == 'GET':
        send_uids = []
        message_objs = message.objects.filter(uid_receive=user_id.objects.get(uid=request.session.get('uid'))).order_by('-date')
        uids = []
        for msg in message_objs:
            if msg.uid_send.uid not in uids:
                send_uids.append({
                    'uid': msg.uid_send.uid,
                    'date': msg.date,
                    'name': user_infomation.objects.get(uid=msg.uid_send).name
                })
                uids.append(send_uids[-1]['uid'])
        dic = {
            'sendUids': send_uids
        }
        return render(request, 'myMessage/index.html', dic)