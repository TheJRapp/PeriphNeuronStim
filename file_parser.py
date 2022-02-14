# parse output file from CST
# add data to database
import re
import database

class SuperParser(object):

    def __init__(self, path, filename):
        super(SuperParser, self).__init__()

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
