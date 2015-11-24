# flask-zhihu-demo
==========


##简介

山寨版知乎。具有知乎基本的提问、回答、关注、赞同、评论、话题、收藏功能。[查看网站效果](#show)

##说明

本Demo用python构成，为个人学习Python**练习作品**，**不用于商业用途**。

使用`Flask`框架搭建，数据库使用[MySQL][sql]。

其他工具/扩展：

    $ sudo pip3 install flask-sqlalchemy
    $ sudo pip3 install flask-wtf
    $ sudo pip3 install jinja2
    $ sudo pip3 install flask-script
    $ sudo pip3 install flask-bootstrap
    $ sudo pip3 install flask-migrate
    $ sudo pip3 install flask-mail
    $ sudo pip3 install flask-login
    $ sudo pip3 install flask-pagedown markdown bleach

##构成

    www/
    |-__init__.py
    |-zhihu.py  # 运行
    |-models.py  # 模型
    |-config.py  # 配置
    |-emailbinding.py  # 邮箱绑定
    |-templates/
      |-……  # 模板文件 
    |-static/
      |-……  # 静态文件
    |-main/
      |-__init__.py
      |-errors.py
      |-forms.py  # 表单
      |-views.py  # 视图
    

##主要路由

    main.route('/')：首页动态，包括所关注用户动态包括赞同、关注、提问、回答等动态，按timeline排序。
    main.route('/signin')：登录。
    main.route('/signout')：登出。
    @main.route('/register')：注册。
    ……

    @main.route('/people/<id>')：个人主页，包括个人信息（可编辑）、个人动态等。
    @main.route('/people/<id>/follow')：关注。
    @main.route('/people/<id>/unfollow')：取消关注。
    @main.route('/people/<id>/following')：用户关注的人。
    @main.route('/people/<id>/followers')：关注用户的人。
    ……

    @main.route('/topic/<id>')：话题，话题下包括绑定话题标签的问题及问题下的答案，可添加/编辑话题，关注话题，取消关注等。
    @main.route('/topics')：所有话题。
    @main.route('/topic')：用户关注的所有话题。
    @main.route('/topic/<id>/follow')：关注话题。
    @main.route('/topic/<id>/unfollow')：取消关注。
    ……

    @main.route('/question/<id>')：问题，可编辑，有评论功能，能添加答案，限制提问后表单消失，答案按赞数排序。
    @main.route('/question/add')：提问，话题标签自动绑定提出的，无话题则创建话题，最多5个话题标签。
    @main.route('/question/<id>/follow')：关注问题。
    @main.route('/question/<id>/unfollow')：取消关注。
    ……

    @main.route('/question/<qid>/answer/<aid>')：答案，可编辑，有评论功能。
    @main.route('/answer/<id>/follow')：点赞。
    @main.route('/answer/<id>/unfollow')：取消点赞。
    @main.route('/answer/<id>/collect')：收藏答案。
    ……

    @main.route('/collection/<id>')：收藏夹，可创建，可编辑。
    @main.route('/collection/<cid>/uncollect-answer/<aid>')：取消收藏。
    ……


<h2 id="show">网站效果</h2>

###首页动态

![index][index]

###问题页面

![question][question]

###评论功能

![comment][comment]

###话题页面

![topic][topic]

###个人主页

![people][people]

###收藏页面

![collect][collect]



[sql]: http://www.mysql.com/

[index]: http://i12.tietuku.com/6abee1727c6f964c.jpg
[question]: http://i12.tietuku.com/9fa2f5f8042f0457.jpg
[comment]: http://i12.tietuku.com/e34961276f2b58ec.jpg
[topic]: http://i12.tietuku.com/51ffba4d910026b5.jpg
[people]: http://i12.tietuku.com/0bde8d632327ff13.jpg
[collect]: http://i12.tietuku.com/1c462a5a31477d6b.jpg
