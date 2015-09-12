f = open('iris.csv')
f = f.readlines()
with open('iris2.csv', 'a') as file:
    for i, line in enumerate(f):
        file.write("X" + str(i) + "," + line)
