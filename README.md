# NUAA_ClassSchedule

[点此访问本项目网页](https://miaotony.github.io/NUAA_ClassSchedule/)  

[点此访问本项目GitHub仓库](https://github.com/miaotony/NUAA_ClassSchedule)  



## Description

NUAA_ClassSchedule  
模拟登录南京航空航天大学新版教务系统，获取课表，解析后生成iCal日历文件...  

   >点击访问[**新版教务系统**](http://aao-eas.nuaa.edu.cn/eams/login.action)

其实这个项目挺有意思的 *(斜眼笑.gif)* 

鉴于时间有限，最近事情较多，有继续开发的计划不过估计会咕咕咕  

所以——    
感兴趣的一起来干呗！   
**欢迎提issue & PR！**  

### **Important!! 免责条款**  

本项目课表由官方教务系统导出，但使用时建议**仔细对照教务系统核对是否所有课程均正常导出**！  

**对于解析异常导致的各种后果请自行承担！**   

（意思就是  *不背锅*）  

---
## Usage

**请在`Python 3`环境下使用，并确保以下库均已安装**。   

使用到的库:   
>requests  
re  
bs4  
lxml  
hashlib  
time  
random  
json  
logging   

### **Step:**  

- Step 1   
 将本仓库clone到本地，或直接下载`*.py`文件   

- Step 2  
**使用时先修改程序里的`stuID`为学号，`stuPwd`为教务处密码**  
   请在`r""`两个引号之间输入，即变量类型为字符串str。  
  
   *（习惯命令行参数的，后面会加的啦）*  
  
    密码仅在本地保存，访问官方教务系统，请放心使用。   
  
   `choice`为个人或班级课表的选择，0为个人，1为班级，**默认为个人课表**。  
   而后保存，再执行此程序即可。  


Windows 环境下：  

```
    python ./aaoLogin.py
```

Linux 环境下：  

```
    python3 ./aaoLogin.py
```


- Step 3  
运行后即可得到解析好的课表  
使用截图：  

![V3.1.20191018](img/V3.1.20191018.png)

P.S.:  
课表解析部分原始JavaScript数据片段：   

![Code_JS](img/Code_JavaScript.png)

---
## Known Issues

**已知存在的bug**

* 登录时提示 **`ERROR! 请不要过快点击!`**  
  
    ![过快点击](img/bug_TooQuickClick.png)
    
    貌似教务系统存在访问时间间隔的限制，比如不能频繁刷新，短时间内不能多次登录之类的。  
    
    **解决方案：**   
        稍等一下，几秒后再次运行本程序，不行多试几次，总能成功的（前提是在浏览器可以正常访问及登录新教务系统）！   
        如果还不行嘛，那就改一下User-Agent再试试吧。   
    
    ​	*后续打算将之前登录的cookies保存在本地，选择是否调用登录记录直接进行访问。若认证已经过期，则重新登录。*         
    
* 考虑到不同课表在解析上可能存在差异，且随着时间发展页面的访问可能会发生变化，目前版本具有时效性。  

* 对于存在的问题和疑问，欢迎在issue中提出，也欢迎提出PR哈！  

---
## Version

@Version:  V0.3.1.20191018  

@Update Log:  
>    V0.3.1.20191018 增加解析课程所在周并优化课表输出格式，修复班级课表中班级解析bug，引入logging模块记录日志便于debug  

>    V0.3.0.20191017 增加 课表解析，增加 班级、实践周匹配，优化代码结构   

>    V0.2.1.20191012 增加UA列表，增加BeautifulSoup提取姓名学号，优化代码结构，为下一步解析课表做准备  

>    V0.2.0.20191010 成功登录教务系统，并成功获取个人或班级课表，但还未进行提取  

>    V0.1.1.20190910 加入未登录成功或过快点击的判断  

>    V0.1.0.20190909 尝试登录新教务系统成功，仅登录而已  

---
## TODO

- [x] 登录新教务管理系统  Login to the new Educational Administration System   
- [x] 获取课表  Get class schedule data   
- [x] 解析课表  Parse class schedule data  
- [ ] 导出课表  Export class schedule data  
- [ ] 基于对象重构  Refactor based on object  
- [ ] 生成.ics日历文件 :calendar:  Generate .ics file  
- [ ] 命令行参数  Get args from terminal  
- [ ] 打包为.exe可执行程序 Packing  
- [ ] 图形化界面  GUI  
- [ ] 搭建网络服务，在线导出日历文件  Web service  
- [ ] 提供课表订阅服务  Subscribe service  
- [ ] 使用情况分析  Usage analysis  
- [ ] etc.     

  

---
## Reference

1. 开源项目`NUAA-Open-Source/NUAA-iCal-Python`  
    >项目网址：[点这里](https://github.com/NUAA-Open-Source/NUAA-iCal-Python)  
    https://github.com/NUAA-Open-Source/NUAA-iCal-Python    

   这是个（已经毕业了的）学长开发的小项目，但老接口随着新教务系统的启用而关闭，进而原脚本无法继续使用。
   
   在开发本项目过程中，解析了课表之后，受到了此项目的启发，打算参考此项目实现iCal日历文件的生成。

2. ISCNU iCal课表
    >网址：[点这里](https://i.scnu.edu.cn/ical/)   
    https://i.scnu.edu.cn/ical/
    

---
## Sponsorship

如果真想赞助的话，`Alipay`扫下面的二维码领个红包吧，每天都能领的那种，顺手薅个羊毛。  

或者 

> 打开支付宝首页搜“**522869066**”领红包

<img src="img/Sponsorship.jpg" style="max-width:50%;" />

`WeChat`:   

<img src="img/Sponsorship2.png" style="max-width:40%;" />


非常感谢啦！  

如果能给校园生活多一些便利，感觉也挺满足的啦。  

**更希望有小伙伴来继续开发和维护这个项目啦~**  

---
## Copyright

网络非法外之地，本项目相关技术内容仅供学习研究，请在合理合法范围内使用！  
The relevant technical content of this project is only for study and research, please use within the reasonable and legal scope!

未经允许不得商用！  
Non-commercial use!    

最终解释权归本项目开发者所有。  
The final interpretation right belongs to the developer of the project.  


Copyright © 2019 [miaoTony](https://github.com/miaotony)  

