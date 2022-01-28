from b_tree import BTree
from permute import permute_word, get_match_word, wildcard_rotate, wildcard_match_2

import os
import string

# 倒排索引

dict1 = {}
dict2 = {}

files = []

path = 'C:/Users/86137/Desktop/信息检索/data/数据'
# filelist = [path + i for i in os.listdir(path)]
for i in range(1,10001):
    file = os.path.join(path, str(i) + ".txt")
    tmp = []
    with open(file, 'r') as file_to_read:
        while True:  
            lines = file_to_read.readline()
            lsplit = lines.split( )
            if (len(lines) == 0): break
            for word in lsplit:
                tmp.append(word)
        files.append(tmp)
    file_to_read.close()   

for i in range(10000):
    file = files[i]
    #print(file)
    for word in file:
        if (word == ' '): continue
        if word.lower() not in dict1:
            dict1[word.lower()] = set()
            dict2[word.lower()] = 1
        else:
            dict2[word.lower()] += 1
        dict1[word.lower()].add(i+1)
        
#print(dict1)
#print(dict2)

output_list = sorted(dict2.items(),key=lambda d:d[1], reverse=True)
output_list_delete_top100 = output_list[100:]
output_sort = sorted(output_list_delete_top100, key=lambda x:x[0])

with open('./dict.index.txt', 'w') as f:
    for word in output_sort:
        f.write("%s\t" % (word[0]))
        sort_dotid = sorted(dict1[word[0]])
        for i in range(len(sort_dotid)):
            f.write("%d" % (sort_dotid[i]))
            if(i != len(sort_dotid)-1):
                f.write(" ")
        f.write('\n')
    f.close()

dict = []
for word in output_sort:
    dict.append(word[0])
#print(dict)

# 通配查询

if __name__=='__main__':
    tree = BTree(3)
    #for word in output_sort:
    #	tree.btree_insert(word[0])
    
    for word in dict:
        for pm_word in permute_word(word):
            tree.insert(pm_word)
            
    while True:
        query = input('Query:')
        if query == 'q':
            print('————————END————————')
            break
        prefix = wildcard_rotate(query)
        wordlist = []
        if prefix == '$':
            wlist = list(output_sort.keys())
            for word in wlist:
                if wildcard_match_2(query, word):
                    wordlist.append(word)
            wordlist = list(set(wordlist))
            wordlist.sort()
        else:
            matchlist = tree.get_suffix(prefix)
            wordlist = get_match_word(matchlist, query)
        
        print(wordlist)
        
        docID_list = []
        for word in wordlist:
            docID = dict1[word]
            docID_list += docID
        docID_list.sort()
        print(docID_list)