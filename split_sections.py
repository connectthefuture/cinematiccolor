import os
import re
from collections import OrderedDict

class OrderedDefaultDict(OrderedDict):
    factory = list

    def __missing__(self, key):
        self[key] = value = self.factory()

        return value

def split_sections(path):
    basename, extension = os.path.splitext(os.path.basename(path))

    if not os.path.exists(basename):
        os.makedirs(basename)

    with open(path) as tex_file:
        tex_content = tex_file.readlines()

    section = basename
    sections = OrderedDefaultDict()
    for line in tex_content:
        if re.match('\\\\section[\*]?\{', line):
            section = re.search('\\\\section[\*]?\{(.*)\}', line)
            section = (
                section.group(1)
                .replace(' ', '-')
                .replace(',', '-')
                .replace(':', '-')
                .replace('(', '-')
                .replace(')', '-')
                .lower()
            )

        sections[section].append(line)

    tex_inputs = []
    for i, (section, lines) in enumerate(sections.items()):
        tex_path = os.path.join(basename, '{0}.tex'.format(section))

        if i != 0:
            tex_inputs.append(tex_path)

        with open(tex_path, 'w') as tex_file:
            for line in lines:
                tex_file.write(line)

    with open(os.path.join(basename, '{0}.tex'.format(basename)), 'a') as tex_file:
        for tex_input in tex_inputs:
            tex_file.write('\\input{{{0}}}\n\n'.format(tex_input))


split_sections('workflow.tex')