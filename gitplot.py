#!/usr/bin/env python

from dulwich.repo import Repo
from datetime import date, timedelta
from os.path import basename
from collections import defaultdict

import cProfile

def canonical_author(author):
    if author.find("hortont") > 0:
        return "Tim"
    elif author.find("natesm") > 0:
        return "Nate"
    elif author.find("racarr") > 0:
        return "Robb"
    elif author.find("arsenm") > 0:
        return "Matt"
    print "Don't know who {0} is!".format(author)
    return author

def get_object_contents(repository, hash):
    return repository.object_store[hash].get_data().splitlines(True)

def list_commit_info(repository):
    for rev in repository.revision_history(repository.head()):
        parentCommits = rev.get_parents()
        insertions = 0

        for parent in parentCommits:
            parentTree = repository.object_store[parent].tree
            changes = repository.object_store.tree_changes(parentTree, rev.tree)
            insertions += len(list(changes))

        yield (canonical_author(rev.author),
               date.fromtimestamp(rev.author_time),
               basename(repository.path),
               insertions)

def single_author_stacked_bar_chart(data, author):
    data = filter(lambda x: x[0] == author, data)
    chartData = defaultdict(lambda : defaultdict(int))

    for commit in data:
        chartData[commit[1]][commit[2]] += commit[3]

    return chartData

def mathematica_stacked_bar_chart(data):
    days = sorted(data.keys())
    projects = {}

    addingDay = days[0]
    while addingDay < days[-1]:
        addingDay += timedelta(1)

        if not addingDay in data:
            data[addingDay]["null"] = 0

    for day in days:
        for project in data[day].keys():
            projects[project] = 1

    days = sorted(data.keys())

    projects = sorted(projects.keys())

    print "BarChart[{"
    chartStrings = []
    for day in days:
        dayStats = []
        for project in projects:
            dayStats.append("Style["+str(data[day][project])+", EdgeForm[]]")
        chartStrings.append("{" + ", ".join(dayStats) + "}")
    print ",\n".join(chartStrings)
    print "}, ChartLayout->\"Stacked\","
    print "ChartLegends->{", ", ".join(["\"" + p + "\"" for p in projects]), "},"
    print "ChartStyle -> \"DarkRainbow\""
    print "]"

repositories = ["/Users/hortont/src/Average-Lapse", "/Users/hortont/src/same",
                "/Users/hortont/src/orbitals", "/Users/hortont/src/phiface",
                "/Users/hortont/src/particles", "/Users/hortont/src/mbp-video-status",
                "/Users/hortont/src/seed", "/Users/hortont/src/sheeple",
                "/Users/hortont/Sites", "/Users/hortont/src/scripts",
                "/Users/hortont/src/mbs-computerlab-signout",
                "/Users/hortont/src/mandelbrot", "/Users/hortont/src/gltd",
                "/Users/hortont/src/wanda", "/Users/hortont/src/glsl-life-saver",
                "/Users/hortont/src/ease", "/Users/hortont/src/configs",
                "/Users/hortont/src/libtetris", "/Users/hortont/src/carmen",
                "/Users/hortont/src/induction", "/Users/hortont/src/cocoa-schedule-prettyprinter",
                "/Users/hortont/src/aperture-viewer", "/Users/hortont/src/piano-stairs"]
commitData = []

def main():
    for repoPath in repositories:
        commitData.extend(list(list_commit_info(Repo(repoPath))))

    chartData = single_author_stacked_bar_chart(commitData, "Tim")
    mathematica_stacked_bar_chart(chartData)

main()