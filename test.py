import csv

header = ['advsd', 'area', 'country_code2', 'country_code3']


header = ['task', 'block', 'trial','key_pressed', 'timestamp', 'coordinate', 'block_type', 'maze_ID', 'rt'] #edit
f = open(filedir_data + "%s_maze_log.csv" %(subjectID), 'w', encoding='UTF8', newline='')
writer = csv.writer(f)
writer.writerow(header)

f = open(filedir_data + "%s_maze_log.csv" %(subjectID), 'a', encoding='UTF8', newline='')


