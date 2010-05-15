#!/usr/bin/env python

from dulwich.repo import Repo
from datetime import date
from os.path import basename
from difflib import Differ
from collections import defaultdict

def canonical_author(author):
    if author.find("hortont") > 0:
        return "Tim"
    elif author.find("natesm") > 0:
        return "Nate"
    elif author.find("racarr") > 0:
        return "Robb"
    print "Don't know who {0} is!".format(author)
    return author

def get_object_contents(repository, hash):
    return repository.object_store[hash].get_data().splitlines(True)

def list_commit_info(repository):
    differ = Differ()
    for rev in repository.revision_history(repository.head()):
        parentCommits = rev.get_parents()
        insertions = deletions = 0

        for parent in parentCommits:
            parentTree = repository.object_store[parent].tree
            changes = repository.object_store.tree_changes(parentTree, rev.tree)

            for (_, _, (fromSHA, toSHA)) in changes:
                if (not fromSHA) and toSHA:
                    insertions += len(get_object_contents(repository, toSHA))
                    continue

                if (not toSHA) and fromSHA:
                    deletions += len(get_object_contents(repository, fromSHA))
                    continue

                fromFile = get_object_contents(repository, fromSHA)
                toFile = get_object_contents(repository, toSHA)

                diff = differ.compare(fromFile, toFile)

                for diffLine in list(diff):
                    if diffLine.startswith("+"):
                        insertions += 1
                    elif diffLine.startswith("-"):
                        deletions += 1

        yield (canonical_author(rev.author),
               date.fromtimestamp(rev.author_time),
               basename(repository.path),
               insertions, deletions)

def single_author_stacked_bar_chart(data, author):
    data = filter(lambda x: x[0] == author, data)
    chartData = defaultdict(lambda : defaultdict(int))

    for commit in data:
        chartData[commit[1]][commit[2]] += commit[3] + commit[4]

    return chartData

def mathematica_stacked_bar_chart(data):
    days = sorted(data.keys())
    projects = {}

    # need to inject all dates into list

    for day in days:
        for project in data[day].keys():
            projects[project] = 1

    projects = sorted(projects.keys())

    print "BarChart[{"
    chartStrings = []
    for day in days:
        dayStats = []
        for project in projects:
            dayStats.append(str(data[day][project]))
        chartStrings.append("{" + ", ".join(dayStats) + "}")
    print ",\n".join(chartStrings)
    print "}, ChartLayout->\"Stacked\"," #ChartLabels->Placed[{",
    #print ", ".join(["\"" + str(d) + "\"" for d in days]), "}, Below], ",
    print "ChartLegends->{", ", ".join(["\"" + p + "\"" for p in projects]), "}"
    print "]"

repositories = ["/Users/hortont/src/Average-Lapse", "/Users/hortont/src/same",
                "/Users/hortont/src/orbitals", "/Users/hortont/src/phiface",
                "/Users/hortont/src/particles", "/Users/hortont/src/mbp-video-status",
                "/Users/hortont/src/seed", "/Users/hortont/src/sheeple", "/Users/hortont/Sites"]
commitData = []

for repoPath in repositories:
    commitData.extend(list(list_commit_info(Repo(repoPath))))

chartData = single_author_stacked_bar_chart(commitData, "Tim")
mathematica_stacked_bar_chart(chartData)
