"""
Copyright 2017 Humboldt-CS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import shutil
import re
from queue import Queue

class CodeDocument:

    def __init__(self):
        self.fileName = ""
        self.fileContents = ""
        self.dependencies = dict()
        self.incomingEdgeCount = 0

file_filters = ['.h', '.cpp']
files_to_merge = dict()

#grab all related files
for item in os.listdir():
    file_name, file_extension = os.path.splitext(item)
    if file_extension in file_filters and file_name != 'merged':
        with open(item) as input_file:
            lines = input_file.readlines()
            doc = CodeDocument()
            doc.fileName = item.lower()
            doc.fileContents = lines
            files_to_merge[doc.fileName] = doc

#for each related file, pull includes list
for file_name in files_to_merge:

    doc = files_to_merge[file_name]
    
    #find all includes
    include_files = list()
    regex_pattern = '#include "([a-z_0-9]+.h)"'

    for i in range(len(doc.fileContents)):
        line = doc.fileContents[i]
        result = re.findall(regex_pattern, line, flags=re.IGNORECASE)

        if len(result) > 0:
            #include found, remember for later
            for match_text in result:
                match_text = match_text.lower()
                doc.dependencies[match_text] = files_to_merge[match_text]
                
                #remove include line from file to prevent compiler error
                files_to_merge[match_text].incomingEdgeCount += 1
                line = re.sub(regex_pattern, line, "", flags=re.IGNORECASE)
                doc.fileContents[i] = line

#with includes built, deterine order.  
ordered_docs = list()
doc_queue = Queue()

#try putting main.cpp last if possible
try:
    doc_queue.put(files_to_merge['main.cpp'])
except:
    pass

#include any other vertices with zero incoming edges
for file_name in files_to_merge:
    if files_to_merge[file_name].incomingEdgeCount == 0 and file_name != 'main.cpp':
        doc_queue.put(files_to_merge[file_name])

while doc_queue.empty() == False:

    #dequeue
    doc = doc_queue.get()

    #add to list of ordered docs
    ordered_docs.append(doc)

    #decrement all outgoing edges
    for dependency_name in doc.dependencies:
        files_to_merge[dependency_name].incomingEdgeCount -= 1
        if files_to_merge[dependency_name].incomingEdgeCount == 0:
            doc_queue.put(files_to_merge[dependency_name])

#in reverse order, build final document
with open('merged.cpp', 'w') as output_file:

    while len(ordered_docs) > 0:
        doc = ordered_docs.pop()
        for line in doc.fileContents:
            print(line, file=output_file, end="")
        print("", file=output_file)
print('successfully created merged.cpp')