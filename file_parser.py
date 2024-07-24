# parse output file from CST
# add data to database
import re
import numpy as np
import database

class SuperParser(object):

    def __init__(self, path, filename):
        super(SuperParser, self).__init__()

        self.path = path
        self.file_name = filename
        self.inputfile = open(path + filename, "r")


class CSTFileParser(SuperParser):

    def __init__(self, path, filename):
        super(CSTFileParser, self).__init__(path, filename)

    def parse_file(self, database):

        i = 0
        for line in self.inputfile:
            caption_match = re.findall('([A-Za-z]+\s)', line)
            digit_match = re.findall('-?\d+\.?\d*', line)
            if caption_match:
                for component in caption_match:
                    database.captions.append(component)
                    database[component] = []
            if digit_match:
                for component in database.captions:
                    database[component].append(float(digit_match[database.captions.index(component)]))


class NewCSTFileParser(SuperParser):

    def __init__(self, path, filename):
        super(NewCSTFileParser, self).__init__(path, filename)

    def parse_file(self, database):

        row1 = next(self.inputfile)
        caption_match = re.findall('([A-Za-z]+\s)', row1)
        if caption_match:
            for component in caption_match:
                database.captions.append(component)
                database[component] = []
        next(self.inputfile)
        for line in self.inputfile:
            for component in database.captions:
                database[component].append(float(line.split()[database.captions.index(component)]))


class CSVNerveShapeParser(SuperParser):

    def __init__(self, path, filename):
        super(CSVNerveShapeParser, self).__init__(path, filename)

    def parse_file(self, database):
        x = []
        y = []
        z = []

        with open(self.path + self.file_name) as f:
            # lines = f.readlines()
            next(f)
            for line in f:
                line_elements = line.split(',')
                x.append(float(line_elements[0]))
                y.append(float(line_elements[1]))
                z.append(float(line_elements[2]))

        database["x "] = x
        database["y "] = y
        database["z "] = z
        database["ExRe "] = []
        database["EyRe "] = []
        database["EzRe "] = []
        database["ExIm "] = []
        database["EyIm "] = []
        database["EzIm "] = []


class S4LFileParser(SuperParser):

    def __init__(self, path, filename):
        super(S4LFileParser, self).__init__(path, filename)

    def parse_file(self, database):
        x, y, z = [], [], []
        Ex_Re, Ex_Im = [], []  # Electric field intensity in Sim4Life
        Ey_Re, Ey_Im = [], []
        Ez_Re, Ez_Im = [], []
        i = 0
        inputfile = open(self.file_name, "r")
        for line in inputfile:
            if i == 0:  # [0] headers
                str_list = line.split()  # separated by the symbol inside ''

            elif i == 1:  # [1] dash line
                str_list = line.split()

            elif i > 19:  # line after headers [0] and dash line [1]
                str_list = line.split()  # separated by the symbol
                x.append((float(str_list[0])))
                y.append((float(str_list[1])))
                z.append((float(str_list[2])))
                Ex_Re.append(float(str_list[3]))
                Ex_Im.append(float(str_list[4]))
                Ey_Re.append(float(str_list[5]))
                Ey_Im.append(float(str_list[6]))
                Ez_Re.append(float(str_list[7]))
                Ez_Im.append(float(str_list[8]))

            i = i + 1

        print('Parsing done')
        database["x "] = x
        database["y "] = y
        database["z "] = z
        database["ExRe "] = Ex_Re
        database["EyRe "] = Ey_Re
        database["EzRe "] = Ez_Re
        database["ExIm "] = Ex_Im
        database["EyIm "] = Ey_Im
        database["EzIm "] = Ez_Im
