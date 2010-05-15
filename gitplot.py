#!/usr/bin/env python

from dulwich.repo import Repo
from datetime import date
from os.path import basename
from difflib import Differ
from pprint import pprint

def canonical_author(author):
    if author.find("hortont") > 0:
        return "Tim"
    elif author.find("natesm") > 0:
        return "Nate"
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

repositories = ["/Users/hortont/src/orbitals",
                "/Users/hortont/src/Average-Lapse"]

print [list(list_commit_info(Repo(r))) for r in repositories]