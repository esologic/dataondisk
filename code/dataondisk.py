import os
import pickle


class AbstractDataOnDisk(object):

    def __init__(self, name):
        self.name = name  # the name of the DOD

        self.entry_data_separator = '-'
        self.data_data_separator = ','
        self.data_name_data_value_separator = ':'

        self.bad_set_strings = [self.entry_data_separator,
                                self.data_data_separator,
                                self.data_name_data_value_separator]

    def get_data(self, entry_name, data_name):

        entry_name = str(entry_name)
        data_name = str(data_name)

        try:
            data = self.__get_data__(entry_name, data_name)
            return data
        except KeyError as e:
            raise KeyError("The [" + str(e) + "] couldn't be found")

    def set_data(self, entry_name, data_name, data_value):

        entry_name = str(entry_name)
        data_name = str(data_name)
        data_value = str(data_value)

        fields_to_be_set = [entry_name, data_name, data_value]

        for field in fields_to_be_set:
            for char in field:
                if char in self.bad_set_strings:
                    raise ValueError("You can't include a [" + str(char) + "] in a set field")

        self.__set_data__(str(entry_name), str(data_name), str(data_value))

    def __get_data__(self, entry_name, data_name):
        raise NotImplementedError("You must implement a get data method")

    def __set_data__(self, entry_name, data_name, data_value):
        raise NotImplementedError("You must implement a set data method")


class InMemoryDataOnDisk(AbstractDataOnDisk):

    def __init__(self, name):
        super(InMemoryDataOnDisk, self).__init__(name)

        self.values_names_by_entry_name = {}

        # the structure of this dod is pretty simple
        # { entry_name0 : {data_name0: data_value1, data_name1: data_value1 ...},
        # entry_name1 : {data_name0: data_value1, data_name1: data_value1 ...} ... }

    def __get_data__(self, entry_name, data_name):

        try:
            entry = self.values_names_by_entry_name[entry_name]
        except KeyError as e:
            raise KeyError('entry')

        try:
            value = entry[data_name]
        except KeyError:
            raise KeyError('value')

        return value

    def __set_data__(self, entry_name, data_name, data_value):

        data_by_value_name = None

        while True:
            try:
                data_by_value_name = self.values_names_by_entry_name[entry_name]
                break
            except KeyError:
                # the entry didn't exist in the DOD, create it
                self.values_names_by_entry_name[entry_name] = {}

        data_by_value_name[data_name] = data_value


class ComplexDataOnDisk(AbstractDataOnDisk):

    def __init__(self, name):
        super(ComplexDataOnDisk, self).__init__(name)

        self.cache = InMemoryDataOnDisk(name)

    def __get_data__(self, entry_name, data_name, deep_check=True):

        if deep_check:
            try:
                value = self.__get_data_from_disk__(entry_name, data_name)
            except KeyError as e:
                raise KeyError("Could not get [" + str(e) + "] from disk")
            
            self.cache.set_data(entry_name, data_name, value)
            return value

        elif not deep_check:
            try:
                value = self.cache.get_data(entry_name, data_name)
                return value
            except KeyError:
                pass

            try:
                value = self.__get_data_from_disk__(entry_name, data_name)
                self.cache.set_data(entry_name, data_name, value)
                return value
            except KeyError as e:
                error = "Could not get [" + str(e) + "] from disk or cache"
                raise KeyError(error)

    def __set_data__(self, entry_name, data_name, data_value):

        self.cache.set_data(entry_name, data_name, data_value)
        self.__set_data_to_disk__(entry_name, data_name, data_value)

    def __get_data_from_disk__(self, entry_name, data_name):
        raise NotImplementedError("You must be able to get data from disk")

    def __set_data_to_disk__(self, entry_name, data_name, data_value):
        raise NotImplementedError("You must be able to get data from disk")


class TextFileDataOnDisk(ComplexDataOnDisk):

    def __init__(self, name):

        super(TextFileDataOnDisk, self).__init__(name)

        self.path = os.path.join(os.getcwd(), self.name + ".txt")

    def __get_data_from_disk__(self, entry_name, data_name):

        lines = None
        good_line = None

        try:
            lines = self.__get_lines__()
        except IOError:
            raise KeyError("file")

        for line in lines:

            entry_data_pair = line.split(self.entry_data_separator)
            if len(entry_data_pair) != 2:
                break

            line_entry_name = entry_data_pair[0]
            line_data_value_pairs = entry_data_pair[1]

            if line_entry_name == entry_name:

                line_data_value_pairs_separated = line_data_value_pairs.split(self.data_data_separator)
                if len(line_data_value_pairs_separated) == 0:
                    break

                for data_name_data_value in line_data_value_pairs_separated:

                    data_name_data_value_separated = data_name_data_value.split(self.data_name_data_value_separator)
                    if len(data_name_data_value_separated) != 2:
                        break

                    line_data_name = data_name_data_value_separated[0]
                    line_data_value = data_name_data_value_separated[1]

                    if line_data_name == data_name:
                        return line_data_value

                raise KeyError("value")

        raise KeyError("entry")

    def __set_data_to_disk__(self, entry_name, data_name, data_value):

        lines = None

        line_found = False

        non_modified_lines_pre_mod = []
        non_modified_lines_post_mod = []

        try:
            lines = self.__get_lines__()

            for line in lines:

                entry_data_pair = line.split(self.entry_data_separator)
                if len(entry_data_pair) != 2:
                    break

                line_entry_name = entry_data_pair[0]

                if line_entry_name == entry_name:
                    good_line = line_entry_name + self.entry_data_separator
                    entry_found = False

                    formed_entry = data_name + self.data_name_data_value_separator + data_value

                    line_data_value_pairs_separated = entry_data_pair[1].split(self.data_data_separator)
                    if len(line_data_value_pairs_separated) == 0:
                        break

                    for data_name_data_value in line_data_value_pairs_separated:

                        data_name_data_value_separated = data_name_data_value.split(self.data_name_data_value_separator)
                        if len(data_name_data_value_separated) != 2:
                            break

                        line_data_name = data_name_data_value_separated[0]

                        if line_data_name == data_name:
                            good_line += formed_entry + self.data_data_separator
                            entry_found = True
                        else:
                            good_line += data_name_data_value + self.data_data_separator

                    if not entry_found:
                        good_line += formed_entry

                    line_found = True

                else:
                    if not line_found:
                        non_modified_lines_pre_mod.append(line)
                    else:
                        non_modified_lines_post_mod.append(line)

        except IOError:
            pass

        if not line_found:
            good_line = entry_name + self.entry_data_separator + data_name + self.data_name_data_value_separator + data_value + self.data_data_separator

        outgoing_lines = non_modified_lines_pre_mod + [good_line] + non_modified_lines_post_mod

        path = os.path.join(os.getcwd(), self.name + ".txt")

        while True:
            try:
                with open(path, 'w') as file_stream:
                    for line in outgoing_lines:
                        file_stream.write("%s\n" % line)
                    break
            except IOError:
                pass

    def __get_lines__(self):
        lines = []
        with open(self.path) as file_stream:
            stream_lines = file_stream.readlines()
            for line in stream_lines:
                lines.append(line.rstrip('\n'))
        return lines


class PickleDict(object):

    def __init__(self, path):
        self.path = path

        if not os.path.isfile(self.path):
            with open(self.path, "wb") as file:
                file.flush()

    def __setitem__(self, key, value):

        with open(self.path, "rb") as file:
            try:
                d = pickle.load(file)
                file.flush()
            except EOFError:
                d = {}

        d[key] = value

        with open(self.path, "wb") as file:
            pickle.dump(d, file)
            file.flush()

        del d

    def __getitem__(self, item):

        d = None

        with open(self.path, "rb") as file:
            try:
                d = pickle.load(file)
                file.flush()
            except EOFError:
                raise KeyError("Item isn't found in dict")

        val = d[item]

        del d

        return val
