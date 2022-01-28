import os
import string

#倒排索引

dict1 = {}
dict2 = {}

files = []

path = './数据/'
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

    
#布尔检索
index = {}
query_dict = {}

with open("./dict.index.txt", 'r', encoding="UTF-8") as f:
    for line in f.readlines():
        line_data = line.split( )
        query_dict[line_data[0]] = line_data[1:]
        
def print_query_ret(query_ret):
    if (len(query_ret) == 0):
        print("0")
        return
    query_ret = sorted(query_ret)
    for docID in query_ret:
        print(docID.strip())
    print('\n')
        
def query():
    while True:
        x = input("Search for：").split( )
        #print(len(x))
        if (len(x) == 1):
            x = x[0]
            if (x == "q"):
                print("------------END-----------")
                break
            if (x in query_dict):
                q = query_dict[x]
                print_query_ret(q)
            else:
                print("none")
        else:
            if (x[1] == 'and'):
#                 print(x)
                setx = set(query_dict.get(x[0], []))
                sety = set(query_dict.get(x[2], []))
                q = list(setx & sety)
                print_query_ret(q)
            elif (x[1] == 'or'):
                setx = set(query_dict.get(x[0], []))
                sety = set(query_dict.get(x[2], []))
                q = list(setx | sety)
                print_query_ret(q)
                
query()