#!/usr/bin/env python3
"""
Plotting recorded performance data to .png graphs. Usage:
./perfplot.py ../perftests graphs_out
"""
from dataclasses import dataclass
import functools
import os
import shutil
import pathlib
import signal
import sys
import mdutils
from mdutils.tools.Table import Table
import json
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from packaging import version
from pathlib import Path

# pip3 install packaging matplotlib


def generateGraph(testName: str, statFiles: dict, dstDir: str, mainLineName: str = 'throughput', secondLineName: str = 'meanResTime' ):
    tags = []
    statData = {}
    i = 0
    for file in statFiles:
        obj : dict = json.load(open(file, 'rb'))
        tag = file.parts[-3]
        tags.append(tag)
        for metric, value in obj['Total'].items():
            try:
                val = float(value)
                data = statData.setdefault(metric, [])
                data.append(val)
            except:
                print(f"W: Skipping value \'{value}\' for metric \'{metric}\'")
                pass
        i += 1
    
    secondLineData = statData.setdefault(secondLineName, [])

    lineColor = None if len(secondLineName) == 0 else "blue"
    secondaryColor = 'red'
    
    labelFontSize = 12

    
    lines = []
    fig, axes =  plt.subplots(2, 1) # , constrained_layout=True  , figsize=plt.figaspect(0.5)
    #fig = plt.figure(figsize=plt.figaspect(1))
    #plt.subplots_adjust(wspace=0, hspace=0, top=2) 

    table : Axes = axes[1]
    table.set_visible(True)
    table.axis("off")
    table.table(list(zip(tags, secondLineData)), colLabels = ['Tags', 'Vals'], colColours = ['lightgray', "lightgray"], loc="upper center")
    tableData = [p for p in range(len(tags)) for p in (tags[p], secondLineData[p])]
    strtable = Table().create_table(columns=2, rows=len(tags) + 1, text=['Tags', 'Vals'] + tableData, text_align='center')
    print(strtable)
    
    y1: Axes = axes[0] # plt.gca()
    for lineName, lineData in statData.items():
        if lineName == mainLineName:
            lineAlpha = 1.0
        elif len(secondLineName) == 0:
            lineAlpha = 0.3
        else:
            continue
        lines += y1.plot(tags, lineData, label = lineName, color = lineColor, linewidth = 2.0, alpha = lineAlpha)

    y1.set_xticks(tags) # avoiding warning next line
    y1.set_xticklabels(tags, fontsize = 8, rotation = 45)
    y1.set_xlabel("Tags", fontsize = labelFontSize)
    
    sz = plt.gcf().get_size_inches()
    #plt.gcf().set_size_inches(sz[0] * 1.5, sz[1] * 1)

    extraLabel = {} if lineColor == None else {'color': lineColor}
    extraTick = {} if lineColor == None else {'labelcolor': lineColor}
    y1.set_ylabel(mainLineName, fontsize = labelFontSize, **extraLabel)

    y1.tick_params(axis = "y", **extraTick)
    y1.set_ylim(bottom = 0)
    
    y1.tick_params(axis='x', which='major', labelsize=labelFontSize * 0.5)
    y1.tick_params(axis='x', which='minor', labelsize=labelFontSize)

    if len(secondLineName) > 0 and len(secondLineData) > 0:
        y2: Axes = y1.twinx()
        lines += y2.plot(tags, secondLineData, label = secondLineName, color = secondaryColor, linestyle='-', marker='^', alpha = 0.3)
        y2.set_ylabel(secondLineName, fontsize = labelFontSize, color = secondaryColor)
        y2.tick_params(axis = "y", labelcolor = secondaryColor)
        y2.set_ylim(bottom = 0.0)
        #y2.set_visible(False)


    #y1.set_visible(False)
    #y1.axis("off")

    y1.legend(handles = lines, loc='upper right', framealpha = 0.6)
    y1.grid(color = 'lightgray', linestyle = 'dashed')
    y1.set_title(f'JMeter artipie test {testName}', fontsize = 16)
    plt.tight_layout()
    os.makedirs(dstDir, exist_ok = True)
    plt.savefig(f"{dstDir}/{testName}.png", dpi=150, bbox_inches='tight')
    plt.cla()
    plt.clf()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} perftests_dir graphs_out")
        exit(1)

    perftestsDir = sys.argv[1]
    testGroups = {}
    for root, dirs, files in os.walk(perftestsDir):
        for f in files:
            if f == "statistics.json":
                statsFile = Path(root, f)
                testName = statsFile.parts[-2]
                statResults = testGroups.setdefault(testName, [])
                statResults.append(statsFile)

    for name, stats in testGroups.items():
        print(name, stats)
        stats.sort(key = lambda x: version.parse(x.parts[-3])) #sort by tag as version

    for name, stats in testGroups.items():
        #print(name, stats)
        generateGraph(name, stats, sys.argv[2])

    #TODO: 
    # External args & names
    # all 0.5 alpha or 2 opaque ?
    # usage doc - list of params + their meaning/units; # throughput meanResTime medianResTime pct1ResTime sampleCount
    # try log scale for Y
    
    exit(0)

    #plt.show()
    
#./perfplot.py ../perftests graphs && wslview graphs/jmx-files-maven-ul.png