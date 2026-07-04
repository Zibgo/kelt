from io import StringIO

class Preprocessor:
    def __init__(self, stream):
        self.stream = stream

    def read(self):
        new_lines = []
        is_slash = False
        is_multiline_comment = False
        
        for line in self.stream.readlines():
            new_line = ''

            for char in line:
                match char:
                    case '#':
                        if is_slash and is_multiline_comment:
                            is_multiline_comment = False
                        elif is_slash:
                            is_multiline_comment = True
                        else:
                            break
                    case '/':
                        is_slash = True
                    case '\n':
                        continue
                    case _:
                        is_slash = False
                        if not is_multiline_comment:
                            new_line += char

            if new_line:
                new_line += '\n'

            new_lines.append(new_line)

        self.stream = StringIO(''.join(new_lines))
        return self.stream

    def readline(self, line):
        new_line = ''
        
        for char in line:
            if char == '#':
                break
            new_line += char

        return new_line
