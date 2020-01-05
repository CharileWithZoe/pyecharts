# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 22:31:41 2020

@author: ZhengChao
"""

from pyecharts.charts import Bar, Grid, Line, Page, Pie
from pyecharts import options as opts
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType
import re
import datetime
import webbrowser

pattern_battery = r"(\d\d-\d\d\s\d\d:\d\d:\d\d).+?battery_level.+?\[(\d*).+?(\d*).+?(\d*)\]"
TimeBattery = []
LEVEL = []
VOLTAGE = []
TEMP = []
pattern_screen = r"(\d\d-\d\d\s\d\d:\d\d:\d\d).+?screen_toggled.+?(\d).*"
TimeScreen = []
ScreenOnOff = []
# 01-01 09:02:17.242  1722  2831 I battery_status: [4,2,1,1,Li-ion]
pattern_chargerType = r"(\d\d-\d\d\s\d\d:\d\d:\d\d).+?battery_status.+?\[(.*)\]"
TimeCharge = []
ChargeType = []

AllDATA = {
        "battery"       : (TimeBattery, LEVEL, VOLTAGE, TEMP),
        "screenOnOff"   : (TimeScreen, ScreenOnOff),
        "chgType"       : (TimeCharge, ChargeType),
        }
# these two variable is used to alignment
MIN_DATETIME = 0
MAX_DATETIME = 0

file_path = r"logcat_events.txt"
with open(file_path, 'r', encoding='UTF-8') as f:
    lines = f.readlines()

for line in lines:
    match_obj = re.search(pattern_battery, line)
    if match_obj is not None:
        #print(match_obj.group(0))
        dtime = datetime.datetime.strptime("2020-"+match_obj.group(1), "%Y-%m-%d %H:%M:%S")
        level = int(match_obj.group(2))
        voltage = int(match_obj.group(3))
        temp = int(match_obj.group(4))
        #print(dtime, level, voltage, temp)
        TimeBattery.append(dtime)
        LEVEL.append(level)
        VOLTAGE.append(voltage)
        TEMP.append(temp / 10.0)
        continue

    match_obj = re.search(pattern_screen, line)
    if match_obj is not None:
        #print(match_obj.group(0))
        dtime = datetime.datetime.strptime("2020-"+match_obj.group(1), "%Y-%m-%d %H:%M:%S")
        screen = int(match_obj.group(2))
        #print(dtime, screen)
        TimeScreen.append(dtime)
        if screen == 2:
            screen = 1
        ScreenOnOff.append(screen)
        continue
    
    match_obj = re.search(pattern_chargerType, line)
    if match_obj is not None:
        #print(match_obj.group(0))
        dtime = datetime.datetime.strptime("2020-"+match_obj.group(1), "%Y-%m-%d %H:%M:%S")
        chgType = int(match_obj.group(2).split(',')[3])
        #print(dtime, match_obj.group(2), chgType)
        TimeCharge.append(dtime)
        ChargeType.append(chgType)
        continue

initialiezed = False
for k, v in AllDATA.items():
    if (len(v[0]) < 1):
        print("%s data error, len=%d" % (k, len(v[0])))
    if initialiezed is False:
        initialiezed = True
        MIN_DATETIME = v[0][0]
        MAX_DATETIME = v[0][-1]
    if v[0][0] < MIN_DATETIME:
        MIN_DATETIME = v[0][0]
    if v[0][-1] > MAX_DATETIME:
        MAX_DATETIME = v[0][-1];
    print("k=%s min:%s max:%s" % (k, MIN_DATETIME, MAX_DATETIME))

    

BaseDateTime = datetime.datetime.strptime("1900-01-01 00:00:01", "%Y-%m-%d %H:%M:%S")
Ratio = 100 * (TimeBattery[0] - BaseDateTime).total_seconds() / (TimeBattery[-1] - BaseDateTime).total_seconds()
print("Base Time: ",BaseDateTime) 
print("Start Time: ",TimeBattery[0], (TimeBattery[0] - BaseDateTime).total_seconds()) 
print("End Time: ",TimeBattery[-1], (TimeBattery[-1] - BaseDateTime).total_seconds()) 
print(Ratio)

colorList = ['#4f81bd', '#c0504d', '#9bbb59', '#604a7b', '#948a54', '#e46c0b'];
grid = (
        Grid(
                init_opts=opts.InitOpts(
                        #theme = ThemeType.DARK,
                        width = "1080px",
                        height = "2000px",
                )
            )
        )

line_batteryInfo = (
    Line()
    .add_xaxis(TimeBattery)
    .add_yaxis("Level", 
               LEVEL,
               xaxis_index=1,
               #symbol="none",
               label_opts=opts.LabelOpts(is_show=False),#默认显示Y轴的值在曲线上，设置为False清除这个设置
              )
    .add_yaxis("Temperature",
               TEMP,
               xaxis_index=1,
               symbol = "none",
               label_opts=opts.LabelOpts(is_show=False),)
    .set_global_opts(
        #title_opts=opts.TitleOpts(title="MyPowerEchart", subtitle="^_^"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_right="0px", pos_top="50px"),
        xaxis_opts=opts.AxisOpts(
            type_="time",
            name="Time",
            min_=MIN_DATETIME,
            max_=MAX_DATETIME,
        ),
        yaxis_opts=opts.AxisOpts(
            name="123",
            splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        #设置缩放图
        datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 1, 2],
                    range_start=Ratio,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=False,
                    xaxis_index=[0, 1, 2],
                    type_="slider",
                    pos_top="90%",# dataZoom-slider 组件离容器上侧的距离
                    range_start=Ratio,
                    range_end=100,
                ),
        ],
        #设置鼠标放置位置的值
        tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",#显示 x y轴两条线交叉，并且把xy值都显示出来
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
    )
)

line_screenOnOff = (
    Line()
    .add_xaxis(TimeScreen)
    .add_yaxis("ScreenOnOff", 
               ScreenOnOff,
               is_step = "end",
               symbol = "none",
               areastyle_opts=opts.AreaStyleOpts(opacity=1),
               label_opts=opts.LabelOpts(is_show=False),#默认显示Y轴的值在曲线上，设置为False清除这个设置
              )   
    .set_global_opts(
        #title_opts=opts.TitleOpts(title="MyPowerEchart", subtitle="^_^"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_right="0px", pos_top="400px"),
        xaxis_opts=opts.AxisOpts(
            type_="time",
            name="Time",
            is_show=False, # dont show x axis
            min_=MIN_DATETIME,
            max_=MAX_DATETIME,
        ),
        yaxis_opts=opts.AxisOpts(
            name="",
            is_show=False, # dont show y axis
            splitline_opts=opts.SplitLineOpts(is_show=False)
        ),
    )
)
        
line_chgType = (
    Line()
    .add_xaxis(TimeCharge)
    .add_yaxis("ChgType", 
               ChargeType,
               is_step = "end",
               symbol = "none",
               areastyle_opts=opts.AreaStyleOpts(opacity=1),
               label_opts=opts.LabelOpts(is_show=False),#默认显示Y轴的值在曲线上，设置为False清除这个设置
              )   
    .set_global_opts(
        #title_opts=opts.TitleOpts(title="MyPowerEchart", subtitle="^_^"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_right="0px", pos_top="430px"),
        xaxis_opts=opts.AxisOpts(
            type_="time",
            name="Time",
            is_show=False, # dont show x axis
            min_=MIN_DATETIME,
            max_=MAX_DATETIME,
        ),
        yaxis_opts=opts.AxisOpts(
            name="",
            is_show=False, # dont show y axis
            splitline_opts=opts.SplitLineOpts(is_show=False)
        ),
    )
)

grid.add(line_batteryInfo,
         grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="50px",  height="300px"),) #000px-350px
grid.add(line_screenOnOff,
         grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="400px", height="20px"),) #400px-500px
grid.add(line_chgType,
         grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top="430px", height="20px"),) #400px-500px

html_saved = r"echarts_power.html"
grid.render(path=html_saved)
webbrowser.open(html_saved)
#grid.render_notebook()