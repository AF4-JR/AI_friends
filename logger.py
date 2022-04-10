from datetime import datetime


def write(filename, _msg):
    try:
        file = open(filename, 'a+', encoding="utf-8")
        file.write(str(datetime.now()) + "-----------------------" + str(_msg) + "\n")
        file.close()
    except BaseException as e:
        file = open(filename, 'a+')
        file.write(str(datetime.now()) + "| Error: " + str(e) + ". When attempting to write the following message to: " + filename + " - with Msg: " + str(_msg) + "\n")
        file.close()
