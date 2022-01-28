from fnmatch import fnmatch

def permute_word(word):
    permute_list = []
    word = word + '$'
    while word[0] != '$':
        permute_list.append(word)
        word = word[1:] + word[0]
    permute_list.append(word)
    return permute_list

def rotate_back(word_rotated):
    while word_rotated[-1] != '$':
        word_rotated = word_rotated[1:] + word_rotated[0]
    return word_rotated[:-1]

def get_match_word(word_rotated_list, query):
    word_set = set()
    for word_rotated in word_rotated_list:
        word = rotate_back(word_rotated)
        if wildcard_match_2(query, word):
            word_set.add(word)
    word_list = list(word_set)
    word_list.sort()
    return word_list

def wildcard_rotate(query):
    rotate_query = query
    pos = rotate_query.find('*')
    rotate_query += '$'
    if pos < len(query) - 1:
        truncate_flag = False
        for i in range(len(query) - pos):
            if rotate_query[-1] == '*':
                truncate_flag = True
            if truncate_flag:
                rotate_query = rotate_query[: -1]
            else:
                rotate_query = rotate_query[-1] + rotate_query[: -1]
    else:
        rotate_query = rotate_query[-1] + rotate_query[: -1]
    return rotate_query[:-1]

def wildcard_match_2(query, word):
    return fnmatch(word, query)