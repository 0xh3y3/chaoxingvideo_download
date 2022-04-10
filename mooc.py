import requests
from lxml import etree
import re
import time
import os
import stdiomask
import prettytable as pt


def login(uname, password):
    login_url = "https://passport2.chaoxing.com/fanyalogin"
    login_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Referer": "https://passport2.chaoxing.com/login?fid=&newversion=true&refer=http://i.chaoxing.com"
    }
    login_data = {
        "uname": str(uname),
        "password": str(password)
    }
    login_res = session.post(
        url=login_url, headers=login_headers, data=login_data)
    return login_res


def cons_cookies(login_res):
    cookies = 'lv=' + login_res.cookies['lv'] + '; fid=' + login_res.cookies['fid'] + '; _uid=' + login_res.cookies[
        '_uid'] + '; uf=' + \
        login_res.cookies['uf'] + '; _d=' + login_res.cookies['_d'] + '; UID=' + login_res.cookies[
                  'UID'] + '; vc=' + login_res.cookies[
        'vc'] + '; vc2=' + login_res.cookies['vc2'] + '; vc3=' + login_res.cookies['vc3'] + '; xxtenc=' + \
        login_res.cookies[
        'xxtenc'] + '; DSSTASH_LOG=' + login_res.cookies['DSSTASH_LOG'] + ';' + 'source=""; spaceFid=24846; ' \
        'spaceRoleId="" '

    return cookies


def require_id():

    data = {
        "courseType": 1,
        "courseFolderId": 0,
        "courseFolderSize": 0
    }

    # import prettytable  制表
    courese_table = pt.PrettyTable()
    courese_table.field_names = [
        "index", "course_name", "course_status", "teacher", "courseId", "clazzId", "id"]

    # 获取课程列表
    courselistdata_url = "http://mooc1-1.chaoxing.com/visit/courselistdata"
    courselistdata_res = session.post(
        courselistdata_url, headers=headers, data=data)
    courselistdata_text = courselistdata_res.text
    courselistdata_obj = etree.HTML(courselistdata_text)
    courselistdata_id_list = re.findall(
        r'courseId="\d+" clazzId="\d+" personId="\d+" id="(.*?)">', courselistdata_text)

    # 循环将信息写入
    for id_ in courselistdata_id_list:
        # index
        course_table_list = list()
        # number
        course_table_list.append(courselistdata_id_list.index(id_))
        # 课程名
        course_name = courselistdata_obj.xpath(
            '//*[@id="' + id_ + '"]/div[2]/h3/a/span/text()')[0]
        course_table_list.append(course_name.strip())
        # 课程状态
        course_status = courselistdata_obj.xpath(
            '//*[@id="' + id_ + '"]/div[1]/a[2]/text()')
        if len(course_status) != 0:
            course_table_list.append((course_status[0]).strip())
        else:
            course_table_list.append("课程未结束")
        # Teacher
        teacher = courselistdata_obj.xpath(
            '//*[@id="' + id_ + '"]/div[2]/p[2]/text()')
        if len(teacher) != 0:
            course_table_list.append(teacher[0])
        else:
            course_table_list.append("未知")
        # courseId
        course_table_list.append(id_.split('_')[1])
        # clazzId
        course_table_list.append(id_.split('_')[2])
        # id
        course_table_list.append(id_)
        # 插入表格
        courese_table.add_row(course_table_list)
    print(courese_table.get_string(title="YOUR CHAOXING COURSE TABLE"))
    while True:
        try:
            # 用户输入
            input_index = (input("请输入您要下载的课程index:")).strip()
            # 因无法取出表格中的值 所以将用正则或者split
            index_row = courese_table.get_string(
                start=int(input_index), end=(int(input_index) + 1))
            index_row_list = index_row.split("|")
            # 取出 courseId clazzId    return      courseId      clazzId
            courseId = index_row_list[13]
            clazzid = index_row_list[14]

            require_chapterid_url = "https://mooc2-ans.chaoxing.com/mycourse/studentcourse?courseid=" + \
                courseId + "&clazzid=" + clazzid + "&ut=s"
            chapterid_text = session.get(
                require_chapterid_url, headers=headers).text
            chapterId_list = re.findall(
                r"toOld\('\d+', '(.*?)', '\d+'\)", chapterid_text)
            if len(chapterId_list) == 0:
                print("此课程未开发,请重新选择index!")
            else:
                chapterId = chapterId_list[0]
                break
        except:
            print("请输入正确的index")
    return chapterId, courseId, clazzid


def require_list(courseId, chapterId, clazzid):
    id_url = 'https://mooc1.chaoxing.com/mycourse/studentstudycourselist?courseId=' + courseId + '&chapterId=' + chapterId + ' \
                   &clazzid=' + clazzid + '&mooc2=1 '

    while True:
        try:
            htm_obj = etree.HTML((session.get(id_url, headers=headers)).text)
            cur_id_text = (session.get(id_url, headers=headers)).text
            break
        except:
            print("网络请求失败,正在尝试重连.若等待时常过久,还请重新启动程序!")

    big_id_list = re.findall(
        r'id="(.*?)"><span class="posCatalog_title posCatalog_rotate', cur_id_text)  # 大标题id
    cur_id_list = re.findall(r'id="cur(.*?)">', cur_id_text)  # curxxxx list
    all_id_list = re.findall(r'id="(.*?)">', cur_id_text)
    return htm_obj, cur_id_list, big_id_list, all_id_list


def require_coursename(courseId, clazzid):
    coursename_url = "https://mobilelearn.chaoxing.com/v2/apis/class/getClassDetail?fid=24846&courseId=" + \
        courseId + "&classId=" + clazzid
    while True:
        try:
            coursename_text = (session.get(
                coursename_url, headers=headers)).text
            break
        except:
            print("网络请求失败,正在尝试重连.若等待时常过久,还请重新启动程序!")
    coursename = re.findall(r'"name":"(.*?)","', coursename_text)[1]
    coursename_path = "d:\\CHAOXING\\" + coursename
    # 创建文件夹
    coursename_path = coursename_path.strip()
    # 去除尾部 \ 符号
    coursename_path = coursename_path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(coursename_path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(coursename_path)
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(coursename_path + ' 目录已存在')
    return coursename


def download_video(htm_obj, clazzid, courseId, all_id_list, coursename):
    for all_id in all_id_list:
        if "cur" not in all_id:
            big_chapter_name = htm_obj.xpath(
                '//*[@id="' + str(all_id) + '"]/span/em/text()')[0]  # 章节名称
            big_title_name = htm_obj.xpath(
                '//*[@id="' + str(all_id) + '"]/span/text()')[0]  # 标题名称
            path_initial = "d:\\CHAOXING\\" + coursename + "\\" + \
                big_chapter_name + big_title_name.strip() + "\\"
            # 创建文件夹
            path = path_initial.strip()
            # 去除尾部 \ 符号
            path = path.rstrip("\\")
            # 判断路径是否存在
            # 存在     True
            # 不存在   False
            isExists = os.path.exists(path)
            # 判断结果
            if not isExists:
                # 如果不存在则创建目录
                # 创建目录操作函数
                os.makedirs(path)
            else:
                # 如果目录存在则不创建，并提示目录已存在
                print(path + ' 目录已存在')

        else:
            # 课程名称提取  这里不论chapterId 是多少都可以请求到页面 只需要更改xpath的值取相应名称即可
            all_id = str(all_id).split("cur")[1]
            chapter_name = htm_obj.xpath(
                '//*[@id="cur' + str(all_id) + '"]/span[1]/em/text()')[0]  # 章节名称
            title_name = htm_obj.xpath(
                '//*[@id="cur' + str(all_id) + '"]/span[1]/text()')[0]  # 标题名称

            # 获取object_name用于json_url  knowledgeid即chapterId
            object_url = 'https://mooc1.chaoxing.com/knowledge/cards?clazzid=' + clazzid + '&courseid=' + courseId + '&knowledgeid=' \
                         + str(all_id)
            while True:
                try:
                    res = (session.get(object_url, headers=headers)).text
                    break
                except:
                    print("网络请求失败,正在尝试重连.若等待时常过久,还请重新启动程序!")
            object_id = re.findall(
                r'"doublespeed":\d+,"objectid":"(.*?)","_jobid":"', res)[0]  # 用于获取json数据

            # 此url 是用来获取下载地址用的 请求该地址会获取一个json格式 451fd649397bccc34a28fea241cc0b5d是objectid
            json_url = "https://mooc1.chaoxing.com/ananas/status/" + \
                object_id + "?k=24846&flag=normal"
            while True:
                try:
                    json_res = (session.get(json_url, headers=headers)).json()
                    break
                except:
                    print("网络请求失败,正在尝试重连.若等待时常过久,还请重新启动程序!")
            download_url = json_res["http"]  # 下载地址

            # 思维导图
            png_object_id_list = re.findall(
                r'"insertimage","objectid":"(.*?)"},"aid"', res)
            if len(png_object_id_list) != 0:
                png_object_id = png_object_id_list[0]
                mind_png_url = "https://p.ananas.chaoxing.com/star3/origin/" + png_object_id + ".png"
                mind_png = (session.get(mind_png_url, headers=headers)).content
                isExists_png = os.path.exists(
                    path_initial + str(chapter_name) + '.png')
                if not isExists_png:
                    with open(path_initial + str(chapter_name) + '.png', 'wb') as f:
                        f.write(mind_png)
                        print("已下载思维导图")
                else:
                    print(str(chapter_name) + ' 思维导图已存在')

            # get 请求下载地址 转换为字节流
            media = (session.get(download_url, headers=headers)).content

            # 写入文件
            isExists_file = os.path.exists(
                path_initial + str(chapter_name + title_name) + '.mp4')
            if not isExists_file:
                with open(path_initial + str(chapter_name + title_name) + '.mp4', 'wb') as f:
                    f.write(media)
            else:
                print(str(chapter_name + title_name) + ' 课程已存在')


def view():
    view_table = pt.PrettyTable()
    view_table.field_names = ["作者", "联系方式", "注意事项", "支持网站", "下载路径"]
    view_table.add_row(["GlowXuthusFly", "2579290631@qq.com", "本程序仅供学习交流,请勿传播,否则后果自负!!!\n 切勿将已下载视频进行传播,否则后果自负!!!",
                        "https://www.chaoxing.com/", "默认下载路径为 d:\\CHAOXING\\"])
    print(view_table.get_string(title="POWER BY GlowXuthusFly"))


if __name__ == '__main__':
    session = requests.Session()
    view()
    while True:
        try:
            while True:
                uname = input("请输入您的账号:")
                password = stdiomask.getpass(prompt="请输入您的密码:", mask='*')
                login_res = login(uname, password)
                login_res_json = login_res.json()['status']
                if login_res_json:
                    print("登录成功")
                    break
                else:
                    print("登录失败请重新登录")

            cookies = cons_cookies(login_res)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
                "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2022-0329-1945",
                "Cookie": cookies
            }
            while True:
                try:
                    id_tuple = require_id()
                    chapterId = id_tuple[0]
                    courseId = id_tuple[1]
                    clazzid = id_tuple[2]
                    break
                except:
                    time.sleep(3)

            require_tuple = require_list(courseId, chapterId, clazzid)
            htm_obj = require_tuple[0]
            all_id_list = require_tuple[3]

            coursename = require_coursename(courseId, clazzid)
            download_video(htm_obj, clazzid, courseId, all_id_list, coursename)
            break
        except:
            print("未知错误,正在重试")
            time.sleep(3)
    print("视频下载完成,感谢您的使用!")
    os.system('pause')
