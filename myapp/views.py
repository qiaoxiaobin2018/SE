from django.shortcuts import render,HttpResponse
import datetime
from myapp import models
import json
from elasticsearch import Elasticsearch
import smtplib
import random
import hashlib
import json
from email.mime.text import MIMEText
import requests

# 返回数据格式
def getandReturn(status,info,data):
    d = {}
    d['status'] = status
    d['info'] = info
    d['data'] = data
    return json.dumps(d)

# 验证码发送子程序
def emailSender(targetEmail,num):
    # 第三方 SMTP 服务
    mail_host = 'smtp.qq.com'
    mail_user = '2030396508@qq.com'
    mail_pass = 'bzadzamjpodshecf'

    sender = '2030396508@qq.com'
    receivers = targetEmail

    title = '欢迎使用普罗米修斯搜索引擎！'
    content = '您的验证码：' + num + '，有效期1分钟。'

    message = MIMEText(content,'plain','utf-8')
    message['Form'] = '{}'.format(sender)
    message['To'] = ','.join(receivers)
    message['Subject'] = title
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host,465) #启用SSL发信
        smtpObj.login(mail_user,mail_pass) #登录验证
        smtpObj.sendmail(sender,receivers,message.as_string()) #发送
        print('邮件发送成功！')
    except smtplib.SMTPException as e:
        print(e)

#首页
def first(request):
    return render(request, 'index.html')

#呈现
def second(request):
    return render(request, 'searchPage.html')

# 登录
def login(request):
    '''

    :param request: email,password
    :return:
    '''
    if request.method == "POST":
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        if email == "" or password == "":
            print('邮箱和密码不能为空!')
            return HttpResponse(getandReturn(0,"邮箱和密码不能为空!",None))
        try:
            user = models.User.objects.get(email = email)
            if user.password == password:
                #设置session
                request.session['is_login'] = 1
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username

                print('登陆成功！')
                return HttpResponse(getandReturn(1,"登录成功!",None))
            else:
                print('密码不正确！')
                return HttpResponse(getandReturn(0,"密码不正确!",None))
        except:
            print('用户不存在！')
            return HttpResponse(getandReturn(0,"用户不存在!",None))

# 注册
def register(request):
    '''

    :param request: username,email,num,password
    :return:
    '''
    if request.method == "POST":
        num = request.POST.get('num',None)
        sessionCacheData = request.session.get('sessionCacheData',None)
        if num != sessionCacheData:
            print('验证码错误！')
            return HttpResponse(getandReturn('0', '验证码错误！', None))
        else:
            username = request.POST.get('username', None)
            useremail = request.POST.get('email', None)
            password = request.POST.get('password', None)
            if useremail == "" or password == "":
                print('邮箱和密码不能为空！')
                return HttpResponse(getandReturn('0', '邮箱和密码不能为空！', None))
            else:
                user = models.User()
                user.username = username
                user.email = useremail
                user.password = password
                try:
                    del request.session['sessionCacheData']
                    user.save()
                except:
                    print('注册失败！')
                    return HttpResponse(getandReturn('0', '注册失败！', None))

                print('注册成功！')
                return HttpResponse(getandReturn('1', '注册成功！', None))
    else:
        print('注册失败，请使用POST方法！')
        return HttpResponse(getandReturn('0', '注册失败，请使用POST方法！',None))

# 注销
def logout(request):
    '''

    :param request:None
    :return:
    '''
    try:
        del request.session['is_login']
        del request.session['user_id']
        del request.session['user_name']
    except:
        print('注销失败！')
        return HttpResponse(getandReturn('0', '注销失败！', None))

    print('注销成功！')
    return HttpResponse(getandReturn('1', '注销成功！', None))

# 添加足迹
def addFootprint(request):
    '''
    POST
    :param request: url,title
    :return:
    '''
    if request.method == "POST":
        try:
            userid = request.session.get('user_id', None)
        except:
            print("用户未登录！")
            return HttpResponse(getandReturn(0, "用户未登录！", None))
        url = request.POST.get('url', None)
        title = request.POST.get('title',None)
        if url == '' or title == '':
            print("添加足迹，内容不能为空！")
            return HttpResponse(getandReturn(0,"添加足迹，内容不能为空！",None))
        try:
            ff = models.Footprint2()
            ff.user_id = userid
            ff.url = url
            ff.title = title
            ff.save()
            print("添加足迹成功！")
        except:
            print("添加足迹失败！")
            return HttpResponse(getandReturn(0,"添加足迹失败！",None))
    else:
        print("请使用POST方法！")
        return HttpResponse(getandReturn(0, "请使用POST方法！", None))

    #返回所有足迹
    try:
        result = models.Footprint2.objects.values().filter(user_id=userid)
        resultList = list(result)
        footprints = json.dumps(resultList)
        print('添加足迹返回信息成功！')
        return HttpResponse(getandReturn(1, '添加足迹返回信息成功！', footprints))
    except:
        print('添加足迹返回信息失败！')
        return HttpResponse(getandReturn(0, '添加足迹返回信息失败！', None))

# 删除足迹
def delFootprint(request):
    '''

    :param request: id
    :return:
    '''
    if request.method == " POST":
        fpid =request.POST.get("id",None)
        try:
            thisfp = models.Footprint2.objects.get(id=fpid)
            thisfp.delete()
            print("删除足迹成功！")
        except:
            print("删除足迹失败！")
            return HttpResponse(getandReturn(0, '删除足迹失败！', None))

        #返回所有足迹
        userid = request.session.get('user_id', None)
        try:
            result = models.Footprint2.objects.values().filter(user_id=userid)
            resultList = list(result)
            footprints = json.dumps(resultList)
            print('删除足迹返回信息成功！')
            return HttpResponse(getandReturn(1, '删除足迹返回信息成功！', footprints))
        except:
            print('删除足迹返回信息失败！')
            return HttpResponse(getandReturn(0, '删除足迹返回信息失败！', None))

# 获取所有足迹
def getAllFootprint(request):
    '''

    :param request:
    :return:nothing
    '''
    if request.method == "POST":
        try:
            userid = request.session.get('user_id', None)
        except:
            print("用户未登录！")
            return HttpResponse(getandReturn(0, "用户未登录！", None))
        try:
            result = models.Footprint2.objects.values().filter(user_id=userid)
            resultList = list(result)
            footprints = json.dumps(resultList)
            print('删除足迹返回信息成功！')
            return HttpResponse(getandReturn(1, '删除足迹返回信息成功！', footprints))
        except:
            print('删除足迹返回信息失败！')
            return HttpResponse(getandReturn(0, '删除足迹返回信息失败！', None))

# 搜索
def search(request):
    '''
    :param request: question(get)
    :return:
    '''
    es = Elasticsearch()
    question = request.GET.get("question",None)
    qq = {
        "query": {
            "match_phrase_prefix": {
                "title": {
                    "query": question,
                    "slop": 4

                }
            }
        }
    }
    res1 = es.search(index="mmp", body=qq)
    list = []
    cc = 0
    if len(question) <= 4:
        tt = "百科 " + question
        uu = '''https://baike.baidu.com/item/''' + str(question)
        mm = question
        ll = {}
        ll['title'] = tt
        ll['url'] = uu
        ll['main'] = mm
        list.append(ll)
        cc = 1

    for itt in res1['hits']['hits']:
        tt = itt['_source']['title']
        uu = itt['_source']['url']
        mm = itt['_source']['main']
        if len(mm) > 74:
            mm = mm[0:77]+"......"
        ll = {}
        ll['title'] = tt
        ll['url'] = uu
        ll['main'] = mm
        list.append(ll)
        cc = cc + 1
    print("搜索结果返回成功！")
    return HttpResponse(getandReturn(1, cc, list))