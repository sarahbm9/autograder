import os, unicodecsv as csv
# open and store the csv file
IDs = {}
with open('PID.csv','rb') as csvfile:
    timeReader = csv.reader(csvfile, delimiter = ',')
    # build dictionary with associated IDs
    for row in timeReader:
        IDs[row[0]] = row[1]
# move files
path = r'C:\Users\Sarah\Downloads\fall21-assignment10-11-01-2021-03-28-18-20211124T031910Z-001\fall21-assignment10-11-01-2021-03-28-18'
gitname = os.listdir(path)
keys = list(IDs)
for names in keys:
    if (names not in gitname):
        try:
            os.mkdir(IDs[names])
        except FileExistsError:
            print('File present')

for oldname in os.listdir(path):
    # ignore files in path which aren't in the csv file
    if oldname in IDs:
        try:
            os.rename(os.path.join(path, oldname), os.path.join(path,(IDs[oldname])))
        except:
            print('File ' + oldname + ' could not be renamed to ' + IDs[oldname] + '!')
    
#temp = os.listdir(path)
#Files_write = open("FilePath.csv", "w")
#for lines in temp:
#    Files_write.write(lines+"\n")
#Files_write.close()
