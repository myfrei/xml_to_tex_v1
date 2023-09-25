import xml.etree.ElementTree as ET

def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()

    first_level_names = []
    second_level_names = []
    second_level_contents = []

    for child in root:
        if child.tag.endswith('TestGroup') or child.tag.endswith('Test'):
            name = child.get('callerName', child.get('name'))
            first_level_names.append(name)

            for subchild in child:
                if subchild.tag.endswith('TestGroup') or subchild.tag.endswith('Test'):
                    sub_name = subchild.get('callerName', subchild.get('name'))
                    second_level_names.append(sub_name)

                    content = {}
                    for item in subchild:
                        if item.tag.endswith('SessionAction') or item.tag.endswith('TestResult'):
                            action_name = item.get('name')
                            content[action_name] = {}
                            for subitem in item.findall(".//c:Item", namespaces={'c': 'urn'}):
                                content[action_name][subitem.get('name')] = subitem.find(".//c:Datum", namespaces={'c': 'urn'}).get('value')

                    second_level_contents.append(content)

    return first_level_names, second_level_names, second_level_contents


file = 'new_test2.xml'

first_level, second_level, contents = parse_xml(file)

print('First Level:', first_level)
print('Second Level:', second_level)
for i, content in enumerate(contents):
    print(f'Content {i + 1}:', content)
