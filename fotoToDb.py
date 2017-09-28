import os
import hashlib
import sqlite3
import logging

# caclulate md5 of files including filenames
def md5sum(t):
    return hashlib.md5(t).hexdigest()


# calculate md5 of filecontent
def hashfile(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

LOG_FILENAME = 'parse.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

primid = 0
#test if database exist else create db
dbname = "C:\python/foto.db"
db = os.path.exists(dbname)
print (db)
if not db:
    conn = sqlite3.connect(dbname)
    print ("Database created and opened succesfully")
    c = conn.cursor()
    c.execute('''CREATE TABLE pictures
         (ID INT PRIMARY KEY     NOT NULL,
         FILENAME           TEXT    NOT NULL,
         SIZE            INT     NOT NULL,
         SUM        TEXT    NOT NULL,
         NAME       TEXT);''')
    print ("Table created successfully")
    conn.commit()
    conn.close()
    primid = 1
else:
    print ("using existing database")
    #get id of last record and assign it to primid
    con = sqlite3.connect(dbname)
    cursor = con.execute('SELECT max(ID) FROM pictures')
    max_id = cursor.fetchone()[0]
    if not max_id is None:
        primid = max_id + 1
    con.close()
doubles = []
errors = 0
fileList = []
wasted = 0
fileSize = 0
folderCount = 0
totalSize = 0

conn = sqlite3.connect(dbname)
logging.debug('Test ' + dbname)
#conn.create_function("md5", 1, md5sum)
c = conn.cursor()

for root, subFolders, files in os.walk(os.getcwd()):
    folderCount += len(subFolders)
    logging.debug('Inside directory ' + root)
    for file in files:
        try:
            fl = str(file)
            f = str(os.path.join(root, file))
            print (f)
            fileSize = os.path.getsize(f)
            totalSize += fileSize
            fsum = hashfile(f)
            curs = c.execute("SELECT * FROM pictures WHERE SUM = ?", (fsum,))
            bestaat = curs.fetchone()
            if bestaat is None:
                print ("ok")
            else:
                #print(bestaat)
                doubles.append(f)
                wasted += fileSize
                continue
            print(fsum)
            fileList.append(f)
            d = { 'ID' : primid, 'FILENAME' : f, 'SIZE' : fileSize, 'SUM' : fsum, 'NAME' : fl }
            keylist = ('ID', 'FILENAME', 'SIZE', 'SUM', 'NAME')
            c.execute('INSERT INTO pictures (ID,FILENAME,SIZE,SUM,NAME) VALUES (?,?,?,?,?);',tuple(d[k] for k in keylist))
            conn.commit()
            primid += 1
        except UnicodeEncodeError:
            errors += 1
            pass


        #fsum = hashlib.md5(f.encode()).hexdigest()

conn.close()
print(("Total Size is {0} bytes".format(totalSize)))
#print ("Total size is %d bytes" % totalSize)

gblengte = (totalSize / 1000000000)
print(("Total Files ", len(fileList), " totalling ", gblengte, " GB"))
print(("Total Folders ", folderCount))
for d in doubles:
    print (d)
answer = input("Wil je de dubbele bestanden verwijderen (ja/nee)?")
if answer == 'ja':
	for d in doubles:
		os.remove(d)
print (("removed ", wasted / 1000000, " MB"))
print (("errors: ", errors))
#conn=sqlite3.connect('/home/reginald/scripts/foto.db')
#c = conn.cursor()
#for row in c.execute('SELECT * FROM pictures'):
        #print (row)
#conn.close()