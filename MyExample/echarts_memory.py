# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 22:12:27 2020

@author: ZhengChao
"""
from pyecharts.charts import Grid, Line, Tab
from pyecharts import options as opts
import datetime
import webbrowser
import os
import json
import argparse

def scan_json_files(path):
    print("scan_json_files(), path=%s" % path)
    jsfiles = []
    for rt, dirs, files in os.walk(path):
        for f in files:
            ff = os.path.join(rt,f)
            if ".json" == os.path.splitext(ff)[-1]:
                jsfiles.append(ff)
                print("json file: %s" % ff)
    return jsfiles


def write_json_file(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def read_json_file(filename):
    data = {}
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

def to_px(number):
    return "%dpx" % number

def plot_one_line(grid, xData, yData, name, top, height):
    line = (
        Line()
        .add_xaxis(xData)
        .add_yaxis(name, 
                yData,
                label_opts=opts.LabelOpts(is_show=False),#默认显示Y轴的值在曲线上，设置为False清除这个设置
                )
        .set_global_opts(
            legend_opts=opts.LegendOpts(orient="vertical", pos_right="0px", pos_top=to_px(top)),
            xaxis_opts=opts.AxisOpts(
                type_="time",
                name="Time",
            ),
            yaxis_opts=opts.AxisOpts(
                name="",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
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
    grid.add(line,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top=to_px(top),  height=to_px(height)),) #000px-350px

def plot_with_data(data):
    grid = (Grid(init_opts=opts.InitOpts(width = "1080px", height = "1000px",)))

    gap = 50
    height = 100
    top = 0
    for i in range(0, len(data)):
        xs = []
        for d in data[i]['x']:
            d = "2020-" + d[0:-4]
            temp = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            xs.append(temp)
        # print(xs)
        ys = []
        for dd in data[i]['y']:
            dd = dd[0:-1]
            temp = int(dd)
            ys.append(temp)
        # print(ys)
        top  = top + gap
        plot_one_line(grid, xs, ys, data[i]['name'], top, height)
        top = top + height

    return grid

def plot_with_data_one_chart(data):
    grid = (Grid(init_opts=opts.InitOpts(width = "1080px", height = "1000px",)))

    lines = Line()
    x_added = False
    for i in range(0, len(data)):
        xs = []
        for d in data[i]['x']:
            year = "2020-"
            d = year + d[0:-4]
            temp = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
            #delta = datetime.timedelta(hours = 1)
            #temp = temp + delta * i
            xs.append(temp)
        # print(xs)
        if x_added == False:
            lines.add_xaxis(xs)
            x_added = False
        ys = []
        for dd in data[i]['y']:
            dd = dd[0:-1]
            temp = int(dd)
            ys.append(temp)
        # print(ys)
        lines.add_yaxis(data[i]['name'], ys, label_opts=opts.LabelOpts(is_show=False),)

    lines.set_global_opts(
            legend_opts=opts.LegendOpts(orient="vertical", pos_right="0px", pos_top=to_px(50)),
            xaxis_opts=opts.AxisOpts(
                type_="time",
                name="Time",
            ),
            yaxis_opts=opts.AxisOpts(
                name="Memory",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
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
                    
    grid.add(lines,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="10%", pos_top=to_px(50),  height=to_px(300)),) #000px-350px

    return grid


def plot(jsonfile):
    data = read_json_file(jsonfile)
    if len(data) >= 2 and data[0].get("type") == "json-config" and data[0].get("style") == "time-series":
        grid1 = plot_with_data(data[1:-1])
        grid2 = plot_with_data_one_chart(data[1:-1])
        
        tab = Tab()
        tab.add(grid1, "分离图")
        tab.add(grid2, "整合图")

        html_saved = r"echarts_myplot.html"
        tab.render(path=html_saved)
        webbrowser.open(html_saved)
    else:
        print("wrong format in json file len=%d type=%s style=%s" % (len(data), data[0].get("type"), data[0].get("style")))


def parse_config_args(s):
    ret = []
    v = s.split(" ")
    for v1 in v:
        temp_val = v1.split('_')
        if len(temp_val) != 4:
            print("config paramters %s != 4" % v1)
            exit(-1)

        l = []

        for v2 in temp_val:
            l.append(int(v2))

        ret.append(l)
    return ret


def main():
    print("4 ", datetime.datetime.now())
    # description:  the usage of the script
    parser = argparse.ArgumentParser(description="Echarts with jsonfile")
    # action: means when the arg is set, the value set to True. eg args.verbose=True
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
    parser.add_argument('--example', '-e', type=int,
                        help='Run MyPlot with the choosed example\n'
                             '\t1: testdata/memory.json\n'
                             '\t2: testdata/power_123.json\n')
    parser.add_argument('--file', '-f',
                        help='The json file to plot')
    parser.add_argument('--config', '-c', type=parse_config_args,
                        help='configs for MyPlot')

    args = parser.parse_args()

    if args.verbose is not None:
        print("args.verbose : %s" % args.verbose)
    if args.config is not None:
        print("args.config : %s" % args.config)
    if args.example is not None:
        print("args.example :  %d" % args.example)
    if args.file is not None:
        print("args.file : %s" % args.file)

    file = 'testdata\\memory.json'
    if args.example == 1:
        file = 'testdata\\memory.json'
    elif args.example == 2:
        file = 'testdata\\power_123.json'

    if args.file is not None:
        file = args.file
    print("5 ", datetime.datetime.now())
    plot(file)
    print("6 ", datetime.datetime.now())


if __name__ == '__main__':
    #import cProfile
    #cProfile.run('main()')
    print("Start")
    main()

