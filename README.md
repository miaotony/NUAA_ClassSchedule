# NUAA_ClassSchedule

[点此访问本项目网页](https://miaotony.github.io/NUAA_ClassSchedule/)  

[点此访问本项目GitHub仓库](https://github.com/miaotony/NUAA_ClassSchedule)  



## Description

NUAA_ClassSchedule  
模拟登录南京航空航天大学新版教务系统，获取课表，解析后生成iCal日历文件...  

>- 话说大家平常是怎么看课表的呀？  
>  - **上教务系统** / **截图** / **小程序** / **手动建课表** / **问同学** / ...   
>
>- I have an idea! 大家有没有想过把课表导入到日历呀？！  
>你看，这么做不仅可以**自定义课程**，和其他安排放在一起；  
>还可以利用**桌面插件**，方便快捷地获取课表；  
>还能根据自己的需要**设定提醒**……  
>更多用途可以自由发挥，多棒的主意呢！  
>   
>说实话，这的确就是偶然间想到的一个小想法呢，说干就干，于是就有了这个项目啦！  
>还在犹豫什么呢，不如就来试试吧！嘿嘿嘿~  


其实这个项目挺有意思的233 *(斜眼笑.gif)*  

鉴于时间有限，最近事情较多，有继续开发的计划不过估计会咕咕咕  

所以——    
感兴趣的一起来干呗！   
**欢迎提issue & PR！**  

### **Important!! 免责条款**  

本项目课表由官方教务系统导出，但使用时**请仔细对照教务系统核对是否所有课程均正常导出**！  

**对于解析异常导致的各种后果请自行承担！**   
*（坚决不背锅）*  

 技术问题请提issue，非技术问题原则上不予处理，请咨询有关部门，谢谢！  

>点击访问[**南航新版教务系统**](http://aao-eas.nuaa.edu.cn/eams/login.action)



---
## Usage
**食用指南**  

**请在`Python 3`环境下食用**。   

### **Step**  

- Step 1   
 进入你喜欢的目录，将本仓库clone到本地，或直接下载`zip`文件（Download ZIP）   
```
    git clone https://github.com/miaotony/NUAA_ClassSchedule.git
```
 
- Step 2  
 安装所需的库（Linux下使用pip3，Windows下使用pip）  
```
    pip3 install -r requirement.txt
```

- Step 3  
**使用时先修改程序里的`stuID`为学号，`stuPwd`为教务处密码**  
   请在`r""`两个引号之间输入，即变量类型为字符串str。  
   
   `choice`为个人或班级课表的选择，0为个人，1为班级，**默认为个人课表**。  
   而后保存，再执行此程序即可。  
   
   **密码仅在本地保存，访问官方教务系统，请放心使用。**   
     
   *习惯命令行参数的，~~后面会加的啦~~*   
   **已经实现了命令行参数，具体往下看！**   
  

Windows 环境下：  

```
    python main.py
```

Linux 环境下：  

```
    python3 main.py
```

从 V0.4.0.20191026 版本起开始支持命令行参数啦！  
**命令行参数说明：**  
```
usage: main.py [-h] [-i ID] [-p PWD] [-c {0,1}]  

Get NUAA class schedule at ease! 一个小jio本，让你获取课表更加便捷而实在~  

optional arguments:  
  -h, --help            show this help message and exit  
  -i ID, --id ID        Student ID 学号  
  -p PWD, --pwd PWD     Student password 教务处密码  
  -c {0,1}, --choice {0,1}  
                        Input `0` for personal curriculum(default), `1` for class curriculum.   
                        输入`0`获取个人课表(无此参数默认为个人课表)，输入`1`获取班级课表   
```  

示例：  
```
    python main.py -i <your ID> -p <your password> 
```

同时也支持在控制台输入学号密码啦，且为了保护，密码不带回显，输完之后`<ENTER>`就好啦！  

当然，和上面的初始参数也是互相兼容的，解析的优先级由高到低为：  
命令行参数->上面的初始设置->控制台输入  


- Step 4  
运行后即可得到解析好的课表啦~   
在`NUAAiCal-Data`目录下就可以看到生成好的`.ics`日历文件，`.txt`文本文件，还有`.xlsx`表格文件啦！  

- Step 5  
将生成好的`.ics`日历文件导入你喜欢的日历，然后尽情享用吧~！  
**顺手再点个Star吧~**   
**在导入iCal日历前，请确认时区已设定为 `UTC/GMT+08:00` 即北京时间，否则可能会出现导入后时间不正确的情况！**   

    
### **Screenshots 使用截图**    

**使用命令行参数：**  
![V0.7.0.20191109-1](img/V0.7.0.20191109-1.png)  

**控制台输入：**  
![V0.4.0.20191026-1](img/V0.4.0.20191026-1.png)  

**导出`.ics`文件：**   
![V0.6.0.20191108-1.png](img/V0.6.0.20191108-1.png)  

**将`.ics`导入到Outlook的效果：**   
![Outlook_example.png](img/Outlook_example.png)  

**将课表导出到`.xlsx`文件：**
![xlsx_file](img/V0.8.0.20191112.png)

### Raw Data  
课表解析部分原始JavaScript数据片段：   

> 20191107更新：  
教务系统中`TaskActivity`函数新增了一个`teachClassName`参数，导致之前的版本匹配出现问题，
在 V0.5.0.20191107 版本中已经修复。  

```javascript
var teachers = [{id:2270,name:"任艳芳",lab:false}];
var actTeachers = [{id:2270,name:"任艳芳",lab:false}];
var assistant = _.filter(actTeachers, function(actTeacher) {
    return (_.where(teachers, {id:actTeacher.id,name:actTeacher.name,lab:actTeacher.lab}).length == 0) && (actTeacher.lab == true);
});
var assistantName = "";
if (assistant.length > 0) {
    assistantName = assistant[0].name;
    actTeachers = _.reject(actTeachers, function(actTeacher) {
        return _.where(assistant, {id:actTeacher.id}).length > 0;
    });
}
var actTeacherId = [];
var actTeacherName = [];
for (var i = 0; i < actTeachers.length; i++) {
    actTeacherId.push(actTeachers[i].id);
    actTeacherName.push(actTeachers[i].name);
}

    activity = new TaskActivity(
        actTeacherId.join(','),
            actTeacherName.join(','),
            "8340",
            "信息检索与利用",
            "548",
            "10302(将军路)",
            "00000011111110000000000000000000000000000000000000000",
            "",
            null,
            assistantName,
            "",
            "",
            "");
    index =0*unitCount+8;
    table0.activities[index][table0.activities[index].length]=activity;
    index =0*unitCount+9;
    table0.activities[index][table0.activities[index].length]=activity;
    
```

其中的`TaskActivity`函数如下：  
```javascript
// new taskAcitvity
function TaskActivity(teacherId,teacherName,courseId,courseName,roomId,roomName,vaildWeeks,taskId,remark,assistantName,experiItemName,schGroupNo, teachClassName){
    this.teacherId=teacherId;
    this.teacherName=teacherName;
    this.courseId=courseId;
    this.courseName=courseName;
    this.roomId = roomId;
    this.roomName = roomName;
    this.vaildWeeks = vaildWeeks;	// 53个01组成的字符串，代表了一年的53周
    this.taskId=taskId;
    this.marshal=marshalValidWeeks;
    this.addAbbreviate=addAbbreviate;
    this.clone=cloneTaskActivity;
    this.canMergeWith=canMergeWith;
    this.isSame=isSameActivity;
    this.toString=activityInfo;
    this.adjustClone=adjustClone;
    this.leftShift=leftShift;
    this.needLeftShift=needLeftShift;
    this.remark = remark;
    this.assistantName=assistantName;
    this.experiItemName=experiItemName;
    this.schGroupNo=schGroupNo;
    this.teachClassName = teachClassName;
}
```
![Code_JS](img/Code_JavaScript.png)  

下面这个是原来的：  
![Code_JS_old](img/Code_JavaScript_old.png)  

---
## Known Issues  
**已知存在的bug**

* ~~登录时提示 **`ERROR! 请不要过快点击!`**~~  
已经解决啦~

* ~~隐含bug：未匹配天目湖校区时间表，后面再说吧……（欢迎PR）~~  
已经匹配天目湖校区时间表啦~  
（潜在bug：教室名称为空则默认是将军路明故宫校区时间表...

* 课程所在周还没有进行合并，于是显示出来的是分立的，这个后面再说吧。  

* 时长持续超过两节（如持续三节课）的课，获取的原始数据中可能存在分开（如2+1）的形式，导致生成的iCal也是独立的，
目前还没有做合并emmm。  

* 考虑到不同课表在解析上可能存在差异，且随着时间发展页面的访问可能会发生变化，目前版本具有时效性。  

* 对于存在的问题和疑问，欢迎在issue中提出，也欢迎提出PR哈！  

---
## Version

@Version:  V0.8.1.20191113

@Update Log:  
>    V0.8.1.20191113 修复表格导出bug，完善`requirement.txt`等  

>    V0.8.0.20191112 新增导出课表到`.xlsx`表格文件；调换输出课程名称和教师顺序，更加符合逻辑   

>    V0.7.0.20191109 新增导出课表到`.txt`文件；  
新增匹配天目湖校区时间表；  
修复Issue #2 `Too Quick Click` bug；  
删除`requirement.txt`中存在的标准库，仅保留第三方库  

>    V0.6.0.20191108 基于对象重构课表解析的部分功能，增加生成iCal日历文件并导出（部分参考NUAA-iCal-Python）  

>    V0.5.1.20191107 优化代码结构，便于下一步重构及生成iCal文件  

>    V0.5.0.20191107 修复因教务系统JS代码变更而无法解析课表的重大bug，增加requirement.txt

>    V0.4.0.20191026 增加命令行参数解析，增加控制台输入学号密码（不回显处理），并与初始设置兼容；修复班级课表中教师为空时解析异常bug  
     ![V0.4.0.20191026-2](img/V0.4.0.20191026-2.png)  
    
>    V0.3.1.20191018 增加解析课程所在周并优化课表输出格式，修复班级课表中班级解析bug，引入logging模块记录日志便于debug  
     ![V0.3.1.20191018](img/V0.3.1.20191018.png)

>    V0.3.0.20191017 增加 课表解析，增加 班级、实践周匹配，优化代码结构   
     ![V0.3.0.20191017](img/V0.3.0.20191017.png)  
        
>    V0.2.1.20191012 增加UA列表，增加BeautifulSoup提取姓名学号，优化代码结构，为下一步解析课表做准备  

>    V0.2.0.20191010 成功登录教务系统，并成功获取个人或班级课表，但还未进行提取  

>    V0.1.1.20190910 加入未登录成功或过快点击的判断  

>    V0.1.0.20190909 尝试登录新教务系统成功，仅登录而已  

---
## TODO

- [x] 登录新教务管理系统  Login to the new Educational Administration System   
- [x] 获取课表  Get class schedule data   
- [x] 解析课表  Parse class schedule data  
- [x] 导出课表到`.txt`文件  Export class schedule data to `.txt` file  
- [x] 命令行参数  Get args from terminal  
- [x] 基于对象重构  Refactor based on object  
- [x] 生成`.ics`日历文件 :calendar:  Generate `.ics` file  
- [x] 生成`.xlsx`表格文件  Generate `.xlsx` file  
- [ ] 打包为`.exe`可执行程序 Packing  
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
   
   在开发本项目过程中，解析了课表之后，受到了此项目的启发，参考其实现了iCal日历文件的生成。在此非常感谢原作者！  

2. ISCNU iCal课表
    >网址：[点这里](https://i.scnu.edu.cn/ical/)   
    https://i.scnu.edu.cn/ical/
    
    这里有一些关于iCal的使用方法，可以参考一波。  

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

**License:**    
**[GPL-3.0](LICENSE)**  

未经允许不得商用！  
Non-commercial use!    

最终解释权归本项目开发者所有。  
The final interpretation right belongs to the developer of the project.  


Copyright © 2019 [MiaoTony](https://github.com/miaotony)  

