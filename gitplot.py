#!/usr/bin/env python

from dulwich.repo import Repo
from datetime import date
from os.path import basename
from difflib import Differ
from pprint import pprint

def canonical_author(author):
    if author.find("hortont") > 0:
        return "hortont"
    print "Don't know who {1} is!".format(author)
    return author

def list_commit_times(repository):
    differ = Differ()
    for rev in repository.revision_history(repository.head()):
        parentCommits = rev.get_parents()
        insertions = deletions = 0

        for parent in parentCommits:
            parentTree = repository.object_store[parent].tree
            changes = repository.object_store.tree_changes(parentTree, rev.tree)

            for (_, _, (fromSHA, toSHA)) in changes:
                if (not fromSHA) and toSHA:
                    insertions += len(repository.object_store[toSHA].get_data().splitlines(True))
                    continue

                if (not toSHA) and fromSHA:
                    deletions += len(repository.object_store[fromSHA].get_data().splitlines(True))
                    continue

                fromFile = repository.object_store[fromSHA].get_data().splitlines(True)
                toFile = repository.object_store[toSHA].get_data().splitlines(True)

                diff = differ.compare(fromFile, toFile)

                for diffLine in list(diff):
                    if diffLine.startswith("+"):
                        insertions += 1
                    elif diffLine.startswith("-"):
                        deletions += 1

        yield (canonical_author(rev.author),
               date.fromtimestamp(rev.author_time),
               basename(repository.path), insertions, deletions)

repository = Repo("/Users/hortont/Desktop/particles")
print(list(list_commit_times(repository)))