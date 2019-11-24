#! /usr/bin/python
###############################################################################
# License
###############################################################################
# MIT License
#
# Copyright (c) 2019 Kevin Buffardi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# GETTING STARTED
###############################################################################
# PSEUDO-CONSTANTS
# should the script be quiet (no standard output, only file out)
def QUIET():
  return False

###############################################################################
# DEPENDENCIES
import re
import os
import sys
import subprocess
from decimal import *
###############################################################################
# FUNCTIONS
# newCSVFile(name) - creates a new csv file with a unique name (as provided)
# with an increasing integer suffix if that file already exists
def newCSVFile(name):
  pwd = os.getcwd()
  file = pwd+"/"+name
  suffix = ""
  while os.path.isfile(file+str(suffix)+".csv"):
    if suffix == "":
      suffix = -1
    else:
      suffix = int(suffix)-1
  file = file + str(suffix) + ".csv"
  stdout("Creating file " + file)
  return open(file, "a") #opened file for appending

# prints the provided message to standard out as long as the 
# QUIET value is not true
def stdout(message):
  if not QUIET():
    print(message)

# finds the id of the tester from the testing file, 
# ex. quiz-data/fa2017430-028/PiezasTest.cpp returns fa2017430-028
def getAuthor(source):
  match = re.findall(r'Author:\s+[^<]+', source, re.S)[0]
  return re.sub(r'Author:\s+', '', match).strip() #remove Author and leading/trailing whitespace

def getEmail(source):
  match = re.findall(r'[<][^>]+[>]', source, re.S)[0]
  return re.sub(r'[<>]', '', match).strip() #remove enclosing braces and spacing

def getTime(source):
  match = re.findall(r'Date:\s+\d+', source, re.S)[0]
  return int(re.sub(r'Date:\s+', '', match).strip()) #remove label and spacing

def getInsertions(source):
  match = re.findall(r'\d+ insertion', source, re.S)
  return int(re.sub(r'insertion', '', match[0]).strip()) if match else 0 #strips down to the number

def getDeletions(source):
  match = re.findall(r'\d+ deletion', source, re.S)
  return int(re.sub(r'deletion', '', match[0]).strip()) if match else 0 #strips down to the number

# builds an array by each commit's data
def splitByCommit(source):
  return re.split(r'^|\ncommit\s+\S{6,}',source, maxsplit=0) # splits by "commit <40 char hash value>"

###############################################################################
# PROCEDURES
if len(sys.argv) != 1:
  stdout("Usage:\n python gitlog2csv.py")
  sys.exit()
#git log --date=unix --shortstat > ../repo-name-log.txt 
log=None
try:
  result = subprocess.run(
            ['git','log','--date=unix','--shortstat'], 
            check=True,
            stdout=subprocess.PIPE
           )
except subprocess.CalledProcessError as err:
  stdout("ERROR from generating git log: "+str(err))
  sys.exit(1)
else: #get piped output in log and current directory as log_file
  log = result.stdout.decode("utf-8")
  log_file = os.getcwd().split(os.sep)[-1]
  stdout(str(log_file))

# Read function under test analysis from text
stdout("Loading "+ log_file + " for commit log parsing.")
content = log.replace('\r\n', '\n').replace('\r', '\n')

lines = re.findall(r'\n',content)
stdout("..Read "+str(len(lines))+" lines.")
commits=splitByCommit(content)
stdout("..Found "+str(len(commits))+" commits.")
commits.reverse() #chronological order
commits.pop() #removes trailing empty string

with newCSVFile(log_file+"-gitlog") as output:
  output.write("commit_number,time,elapsed,author,email,insertions,deletions\n")
  initialized = -1
  for i, commit in enumerate(commits):
    num = i+1
    author = getAuthor(commit)
    email = getEmail(commit)
    time = getTime(commit)
    insertions = getInsertions(commit)
    deletions = getDeletions(commit)
    if i == 0:
      initialized = time
    elapsed = time - initialized
    output.write(str(num)+","+str(time)+","+str(elapsed)+","+author+","+email+","+str(insertions)+","+str(deletions)+"\n")