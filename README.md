# NUAA_ClassSchedule


## Description
NUAA_ClassSchedule  
模拟登录南京航空航天大学新版教务系统，获取课表，解析后生成iCal日历文件...  

   >点击访问[**新版教务系统**](http://aao-eas.nuaa.edu.cn/eams/login.action)

其实这个项目挺有意思的 *(斜眼笑.gif)*

鉴于时间有限，最近事情较多，有继续开发的计划不过估计会咕咕咕  

所以——    
感兴趣的一起来干呗！   
**欢迎提issue & PR！**

---

## Version

@Version: V0.3.0.20191017  

@Update Log:  
    V0.3.0.20191017 增加 课表解析，增加 班级、实践周匹配，优化代码结构  
    V0.2.1.20191012 增加UA列表，增加BeautifulSoup提取姓名学号，优化代码结构，为下一步解析课表做准备  
    V0.2.0.20191010 成功登录教务系统，并成功获取个人或班级课表，但还未进行提取  
    V0.1.1.20190910 加入未登录成功或过快点击的判断  
    V0.1.0.20190909 尝试登录新教务系统成功，仅登录而已  
    
    

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


## Reference
1. 开源项目`NUAA-Open-Source/NUAA-iCal-Python`  
    >项目网址：[点这里](https://github.com/NUAA-Open-Source/NUAA-iCal-Python)  
    https://github.com/NUAA-Open-Source/NUAA-iCal-Python    

   这是个（已经毕业了的）学长开发的小项目，但老接口随着新教务系统的启用而关闭，进而原脚本无法继续使用。
   
   在开发本项目过程中，解析了课表之后，受到了此项目的启发，打算参考此项目实现iCal日历文件的生成。

2. ISCNU iCal课表
    >网址：[点这里](https://i.scnu.edu.cn/ical/)   
    https://i.scnu.edu.cn/ical/
    

## Copyright

网络非法外之地，本项目相关技术内容仅供学习研究，请在合理合法范围内使用！  
The relevant technical content of this project is only for study and research, please use within the reasonable and legal scope!

未经允许不得商用！  
Non-commercial use!    

最终解释权归本项目开发者所有。  
The final interpretation right belongs to the developer of the project.  


Copyright © 2019 [miaoTony](https://github.com/miaotony)  

