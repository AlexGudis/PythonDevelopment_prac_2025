import sys
import os
import zlib

def git_obj_info(path, hash):
    obj_path = path + '/' + ".git" + "/" + "objects" + '/' + hash[:2] + '/' + hash[2:]

    f = open(obj_path, "rb")
    obj = zlib.decompress(f.read())
    header, _, body = obj.partition(b'\x00')
    kind = header.split()[0]
    f.close()

    if kind == b'commit':
        return body.decode()
    else:
        output = ""
        i = 0
        while i < len(body):
            mode_end = body.find(b' ', i)

            name_end = body.find(b'\x00', mode_end)
            name = body[mode_end + 1:name_end].decode()

            sha = body[name_end + 1:name_end + 21]
            hash = sha.hex()

            obj_path = path + '/' + ".git" + "/" + "objects" + '/' + hash[:2] + '/' + hash[2:]

            f = open(obj_path, "rb")
            compr = zlib.decompress(f.read())
            typ = compr.split(b' ')[0].decode()
            f.close()

            output += typ + " " + hash + " " + name + '\n'
            i = name_end + 21

        return output.strip()

def last_commit_hash(repo, branch):
    path_to_branch = repo + '/' + ".git" + "/" + "refs" + '/' + "heads" + '/' + branch
    f = open(path_to_branch, 'r')
    hash = f.read()
    f.close()
    return hash.strip()



path = sys.argv[1]
if len(sys.argv) == 2:
    full_path = path + '/' + ".git" + "/" + "refs" + '/' + "heads"
    for br in os.listdir(full_path):
        print(br)

else:
    branch = sys.argv[2]
    print('Chose option. Input 2, 3 or 4')
    check = int(input())
    if check == 2:
        hash = last_commit_hash(path, branch)
        print(git_obj_info(path, hash))
    elif check == 3:
        pass
    else:
        pass

    