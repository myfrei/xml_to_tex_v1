import xml.dom.minidom
import os
from report_helper import translate_en_ru


def get_xml(file):
    if os.path.isfile(file):
        doc = xml.dom.minidom.parse(file)
        node = doc.documentElement
        return node
    return None


class XMLParser():
    def __init__(self, file):
        self._node = get_xml(file)

    def __del__(self):
        if not (self._node is None):
            self._node.unlink()

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, file):
        self._node = get_xml(file)

    # эта функция нужна для Jinja2, т.к. она не может присваивать значения атрибутам сторонних объектов
    def set_node(self, file):
        self._node = get_xml(file)

    def get_first_attribute(self, current_node, nameOfAttribute):
        value_of_attribute = ''
        if isinstance(nameOfAttribute, str) and not (
                current_node is None) and current_node.nodeType == xml.dom.Node.ELEMENT_NODE:
            for (name, value) in current_node.attributes.items():
                if name == nameOfAttribute:
                    value_of_attribute = value
        return value_of_attribute

    def get_child_elements_by_tag_name(self, parent_node, tag_name):
        child_nodes = []
        if isinstance(tag_name, str) and tag_name != '' and not (
                parent_node is None) and parent_node.nodeType == xml.dom.Node.ELEMENT_NODE:
            all_child_nodes = parent_node.childNodes
            for child_node in all_child_nodes:
                if child_node.nodeType == xml.dom.Node.ELEMENT_NODE and child_node.tagName == tag_name:
                    child_nodes.append(child_node)
        return child_nodes

    def get_elements(self, path, parent_node=None):
        target_elements = []
        if isinstance(path, str) and path != '':
            current_node = self._node
            if not (parent_node is None) and parent_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                current_node = parent_node
            tags = path.split('/')
            target_elements = self.get_child_elements_by_tag_name(current_node, tags[0])
            for i in range(1, len(tags)):
                if len(target_elements) < 1 or target_elements[0].nodeType != xml.dom.Node.ELEMENT_NODE:
                    target_elements = []
                    break
                target_elements = self.get_child_elements_by_tag_name(target_elements[0], tags[i])
        return target_elements

    def get_element_by_name(self, path='', necessary_name='', parent_node=None, list_of_elements=[],
                            isNeedOneElement=True, isUsingPath=True):
        target_elements = []
        if isNeedOneElement:
            res_element = None
        else:
            res_element = []
        if isinstance(necessary_name, str):
            if isUsingPath:
                target_elements = self.get_elements(path, parent_node)
            else:
                target_elements = list_of_elements
            if len(target_elements) > 0:
                if necessary_name == '':
                    if isNeedOneElement:
                        res_element = target_elements[0]
                    else:
                        res_element.append(target_elements[0])
                else:
                    for target_element in target_elements:
                        if target_element.nodeType == xml.dom.Node.ELEMENT_NODE:
                            target_caller_name = target_element.getAttribute('callerName')
                            if target_caller_name == necessary_name:
                                if isNeedOneElement:
                                    res_element = target_element
                                    break
                                else:
                                    res_element.append(target_element)
                            elif target_caller_name == '':
                                target_caller_name = target_element.getAttribute('name')
                                if target_caller_name == necessary_name:
                                    if isNeedOneElement:
                                        res_element = target_element
                                        break
                                    else:
                                        res_element.append(target_element)
        return res_element

    def get_value_of_text_node(self, parent_node):
        value_of_text_node = ''
        if not (parent_node is None) and parent_node.nodeType == xml.dom.Node.ELEMENT_NODE:
            text_nodes = parent_node.childNodes
            if text_nodes.length > 0 and text_nodes.item(0).nodeType == xml.dom.Node.TEXT_NODE:
                value_of_text_node = text_nodes.item(0).data
        return value_of_text_node

    def get_value_of_text_node_by_path(self, path):
        value_of_text_node = ''
        if isinstance(path, str):
            parent_of_text_node = self.get_element_by_name(path)
            value_of_text_node = self.get_value_of_text_node(parent_of_text_node)
        return value_of_text_node

    def get_value_of_text_node_by_parent_node_and_internal_path(self, parent_node, internal_path):
        value_of_text_node = ''
        if isinstance(internal_path, str) and not (parent_node is None):
            elements = self.get_elements(internal_path, parent_node)
            for element in elements:
                value_of_text_node = self.get_value_of_text_node(element)
                if value_of_text_node != '':
                    break
        return value_of_text_node

    def get_value_of_attribute_by_parent_node_and_internal_path(self, parent_node, internal_path, name_of_attribute):
        value_of_attribute = ''
        if isinstance(name_of_attribute, str) and isinstance(internal_path, str) and not (
                parent_node is None) and parent_node.nodeType == xml.dom.Node.ELEMENT_NODE:
            elements = self.get_elements(internal_path, parent_node)
            for element in elements:
                value_of_attribute = self.get_first_attribute(element, name_of_attribute)
                if value_of_attribute != '':
                    break
        return value_of_attribute

    def get_analog_waveform(self, path, add_result_name):
        if isinstance(add_result_name, str):
            graph_elements_list = []
            # Ищем SessinAction с графиком по имени
            # all_tests_element = self.get_element_by_name(step)
            if not (path is None):
                # поиск всех SessionAction в подшаге
                Session_nodes = self.get_child_elements_by_tag_name(path, 'tr:SessionAction')
                # return(Session_nodes)
                # проверка каждой SessionAction
                for Session_node in Session_nodes:
                    # вытаскиваем имя
                    name_of_param = self.get_first_attribute(Session_node, 'name')
                    # если это имя - то, что мы ищем: добавчем в
                    if name_of_param == add_result_name:
                        graph_elements_list.append(Session_node)

            graph_points = []
            raw_waveforms = []
            i = 0
            for step_graph in graph_elements_list:
                i += 1
                in_graph_path = self.get_elements('tr:Data/c:Collection/c:Item/c:Collection', step_graph)
                # get_elements возвращает список(хотя в нем 1 значение), поэтому in_graph_path[0] стоит с индексом 0
                all_items_in_path = self.get_child_elements_by_tag_name(in_graph_path[0], 'c:Item')
                # из всех Item нам нужно Item с dt для оси X, и Item с Y для соотв. оси
                for item_in_path in all_items_in_path:
                    name_of_param = self.get_first_attribute(item_in_path, 'name')
                    # ищем дельта_t - время, промежуток межд измерений-точек
                    if name_of_param == "dt":
                        find_time = float(
                            self.get_value_of_attribute_by_parent_node_and_internal_path(item_in_path, 'c:Datum',
                                                                                         'value'))
                    elif name_of_param == "Y":
                        first_graph_path_points = self.get_elements('c:IndexedArray/ts:Element', item_in_path)
                        for path_point in first_graph_path_points:
                            graph_point = float(self.get_first_attribute(path_point, 'value'))
                            index = self.get_first_attribute(path_point, 'position')
                            index = int(index[1:-1])
                            graph_points += [((index * find_time), graph_point)]

                raw_waveforms.append(graph_points)
                graph_points = []

        f = open(r'C:\avs\Utilities\Template_generator\For DWNT From XML\test.txt', 'a')
        f.write(str(raw_waveforms))
        f.close()
        return raw_waveforms


class XMLConfigParser(XMLParser):
    def get_UUT_Names(self, res_dict):
        rem = self._node.getElementsByTagName('Report')
        if rem.item(0).nodeType == xml.dom.Node.ELEMENT_NODE:
            for (name, value) in rem.item(0).attributes.items():
                if name == 'UUT_Name':
                    res_dict['uut_name'] = value
                if name == 'Headers':
                    res_dict['headers'] = value

    def get_list_of_headers_by_name(self, type_of_header):
        # считывание необходимых заголовков
        rem = self._node.getElementsByTagName('Headers')
        headers = ''
        end_loop = False
        for i in rem:
            if i.nodeType == xml.dom.Node.ELEMENT_NODE:
                for (name, value) in i.attributes.items():
                    if name == 'Name' and value == type_of_header:
                        headers = i.attributes.items()
                        end_loop = True
                        break
            if end_loop:
                break
        return headers

    def get_params_for_header(self, res_dict, type_of_header=''):
        if type_of_header == '':
            # получение типа заголовка
            dop_dict = {'headers': 'Default'}
            self.get_UUT_Names(dop_dict)
        else:
            dop_dict = {'headers': type_of_header}

        headers = self.get_list_of_headers_by_name(dop_dict['headers'])
        # если был указан неправильный тип заголовка, считывается тип заголовка с конфигурационного файла
        if not isinstance(headers, list):
            self.get_UUT_Names(dop_dict)
        headers = self.get_list_of_headers_by_name(dop_dict['headers'])
        if isinstance(headers, list):
            for (name, value) in headers:
                if value != '':
                    if name == 'Head1':
                        res_dict['head1'] = value
                    if name == 'Head2':
                        res_dict['head2'] = value
                    if name == 'Head3':
                        res_dict['head3'] = value
                    if name == 'Date':
                        res_dict['date'] = value


class XMLReportParser(XMLParser):
    def get_data_from_string(self, data, data_type):
        if data_type == 'ts:TS_double':
            try:
                data = float(data)
            except:
                data = ''
        return data

    def get_step_status(self, element):
        step_status = ''
        if not (element is None) and element.nodeType == xml.dom.Node.ELEMENT_NODE:
            # sub_elements = element.getElementsByTagName('tr:ActionOutcome')
            sub_elements = self.get_child_elements_by_tag_name(element, 'tr:ActionOutcome')
            if len(sub_elements) > 0 and sub_elements[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                sub_element = sub_elements[0]
            else:
                # sub_elements = element.getElementsByTagName('tr:Outcome')
                sub_elements = self.get_child_elements_by_tag_name(element, 'tr:Outcome')
                if len(sub_elements) > 0 and sub_elements[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                    sub_element = sub_elements[0]
                else:
                    sub_element = None
            if not (sub_element) is None:
                step_status = sub_element.getAttribute('value')
                if step_status == 'UserDefined':
                    step_status = sub_element.getAttribute('qualifier')
        return step_status

    def get_step_name(self, element):
        step_name = ''
        if not (element is None) and element.nodeType == xml.dom.Node.ELEMENT_NODE:
            step_name = element.getAttribute('callerName')
            if step_name == '':
                step_name = element.getAttribute('name')
        return step_name

    def get_uut_serial_number(self):
        serial_number = self.get_value_of_text_node_by_path(r'trc:TestResults/tr:UUT/c:SerialNumber')
        return serial_number

    def get_test_name(self):
        file_name = ''
        all_tests_element = self.get_element_by_name(r'trc:TestResults/tr:ResultSet')
        file_name = self.get_first_attribute(all_tests_element, 'name')
        file_name = file_name[file_name.rfind('\\') + 1:len(file_name) - 17]
        file_name = file_name.replace('_', ' ')
        return file_name

    def get_start_time(self):
        time_and_date = ''
        all_tests_element = self.get_element_by_name(r'trc:TestResults/tr:ResultSet')
        time_and_date = self.get_first_attribute(all_tests_element, 'startDateTime')
        return time_and_date

    def get_steps(self, path, step_type, step_group):
        step_elements_list = []
        if isinstance(step_type, str) and isinstance(step_group, str) and isinstance(path, str):
            main_seq = self.get_element_by_name(path)
            if not (main_seq is None):
                step_nodes = self.get_child_elements_by_tag_name(main_seq,
                                                                 'tr:ResultSet') + self.get_child_elements_by_tag_name(
                    main_seq, 'tr:TestGroup') + \
                             self.get_child_elements_by_tag_name(main_seq,
                                                                 'tr:SessionAction') + self.get_child_elements_by_tag_name(
                    main_seq, 'tr:Test')
                for step_node in step_nodes:
                    value_of_text_node = self.get_value_of_text_node_by_parent_node_and_internal_path(step_node,
                                                                                                      r'tr:Extension/ts:TSStepProperties/ts:StepType')
                    if value_of_text_node == step_type:
                        value_of_text_node = self.get_value_of_text_node_by_parent_node_and_internal_path(step_node,
                                                                                                          r'tr:Extension/ts:TSStepProperties/ts:StepGroup')
                        if value_of_text_node == step_group:
                            step_elements_list.append(step_node)
        return step_elements_list

    def take_number(self, name_of_step):
        # поиск первой точки
        index = name_of_step.find('.')
        name_of_step = name_of_step[index + 1:]
        # поиск второй точки
        if name_of_step.find('.') != -1:
            index = name_of_step.find('.') + 1
        else:
            index = index - 1
        number = ''
        # при отсутствии символа в строке функция find возвращает значение -1
        if index != -1:
            for i in range(index, len(name_of_step)):
                if name_of_step[i].isdigit():
                    if name_of_step[i] == '0' and number == '':
                        pass
                    else:
                        number += name_of_step[i]
                else:
                    break
        return int(number)

    def sort_list_of_steps(self, seq):
        if isinstance(seq, list):
            length_of_list = len(seq)
            for j in range(1, length_of_list):
                for i in range(0, length_of_list - j):
                    step_name1 = self.get_step_name(seq[i])
                    step_name1 = self.take_number(step_name1)
                    step_name2 = self.get_step_name(seq[i + 1])
                    step_name2 = self.take_number(step_name2)
                    if step_name1 > step_name2:
                        mem = seq[i + 1].cloneNode(True)
                        seq[i + 1] = seq[i].cloneNode(True)
                        seq[i] = mem.cloneNode(True)
        return seq

    def get_substeps(self, parent_node, step_type, step_group):
        substep_elements_list = []
        if isinstance(step_type, str) and isinstance(step_group, str):
            if not (parent_node is None) and parent_node.nodeType == xml.dom.Node.ELEMENT_NODE:
                step_nodes = self.get_child_elements_by_tag_name(parent_node,
                                                                 'tr:SessionAction') + self.get_child_elements_by_tag_name(
                    parent_node, 'tr:Test') + self.get_child_elements_by_tag_name(parent_node, 'tr:TestGroup')
                for step_node in step_nodes:
                    value_of_text_node = self.get_value_of_text_node_by_parent_node_and_internal_path(step_node,
                                                                                                      r'tr:Extension/ts:TSStepProperties/ts:StepType')
                    if value_of_text_node == step_type:
                        value_of_text_node = self.get_value_of_text_node_by_parent_node_and_internal_path(step_node,
                                                                                                          r'tr:Extension/ts:TSStepProperties/ts:StepGroup')
                        if value_of_text_node == step_group:
                            substep_elements_list.append(step_node)
        return substep_elements_list

    def get_prop(self, substeps, name_of_substep, name_of_item):
        additional_results = []
        correct_substeps = []
        if isinstance(name_of_substep, str) and isinstance(name_of_item, str):
            if len(substeps) > 0 and substeps[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                for substep in substeps:
                    name_attribute = self.get_first_attribute(substep, 'name')
                    if name_attribute == name_of_substep:
                        correct_substeps.append(substep)
                if len(correct_substeps) > 0 and correct_substeps[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                    for correct_substep in correct_substeps:
                        item_element = self.get_element_by_name('tr:Data/c:Collection/c:Item', name_of_item,
                                                                correct_substep)
                        result_type = self.get_value_of_attribute_by_parent_node_and_internal_path(item_element,
                                                                                                   'c:Datum',
                                                                                                   'xsi:type')
                        if result_type != '':
                            additional_result = self.get_value_of_attribute_by_parent_node_and_internal_path(
                                item_element, 'c:Datum', 'value')
                            if additional_result == '':
                                additional_result = self.get_value_of_text_node_by_parent_node_and_internal_path(
                                    item_element, 'c:Datum/c:Value')
                            if additional_result != '':
                                additional_result = self.get_data_from_string(additional_result, result_type)
                                additional_results.append(additional_result)
        return additional_results

    def get_result_of_numeric_limit(self, test_result_node):
        result_of_numeric_limit = ''
        if not (test_result_node is None):
            prop_nodes = self.get_elements('tr:TestData/c:Datum', test_result_node)
            if len(prop_nodes) > 0 and prop_nodes[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                data_type = self.get_first_attribute(prop_nodes[0], 'xsi:type')
                result_of_numeric_limit = self.get_first_attribute(prop_nodes[0], 'value')
                result_of_numeric_limit = self.get_data_from_string(result_of_numeric_limit, data_type)
        return result_of_numeric_limit

    def get_prop_of_numeric_limit(self, test_result_node, name_of_prop):
        additional_results = []
        if not (test_result_node is None) and isinstance(name_of_prop, str) and name_of_prop != '':
            prop_nodes = self.get_element_by_name('tr:TestResult', name_of_prop, test_result_node,
                                                  isNeedOneElement=False)
            for prop_node in prop_nodes:
                datum_elements = self.get_elements('tr:TestData/c:Datum', prop_node)
                for datum_element in datum_elements:
                    if datum_element.nodeType == xml.dom.Node.ELEMENT_NODE:
                        data_type = self.get_first_attribute(datum_element, 'xsi:type')
                        if data_type != '':
                            prop_result = self.get_value_of_text_node_by_parent_node_and_internal_path(datum_element,
                                                                                                       'c:Value')
                            if prop_result != '':
                                prop_result = self.get_data_from_string(prop_result, data_type)
                                additional_results.append(prop_result)
        return additional_results

    def load_controller_graph(self, search_x_volts, search_y_amps, name_of_y='Check Valve Current',
                              name_of_x='Output TEST Signal', subname_of_y='Numeric', subname_of_x='Test signal, V'):
        x_volts = []
        y_main_graph = []
        hi_main_graph = []
        lo_main_graph = []
        main_ghaph = []
        hi_graph = []
        lo_graph = []
        temp = []
        # если список не пуст
        if (search_x_volts) and (search_y_amps):
            for volts_test in search_x_volts:
                if not (volts_test is None):
                    prop_nodes = self.get_elements('tr:Parameters/tr:Parameter/tr:Data/c:Datum', volts_test)
                    if len(prop_nodes) > 0 and prop_nodes[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                        result_of_numeric_limit = self.get_first_attribute(prop_nodes[0], 'value')
                        x_volts.append(float(result_of_numeric_limit))
            # забор всех 12тизначений в стандартный словарь
            for amps_test in search_y_amps:
                if not (amps_test is None):
                    temp.append(self.get_numeric_limits([amps_test], name_of_y, subname_of_y))
            # распределение на линии: основная, верхняя и нижняя пределы
            for test in temp:
                for test1 in test:
                    if isinstance(test1, dict):
                        y_main_graph.append(test1['result'])
                        hi_main_graph.append(test1['hi'])
                        lo_main_graph.append(test1['lo'])

            for i in range(len(x_volts)):
                main_ghaph += [(x_volts[i], y_main_graph[i])]
                hi_graph += [(x_volts[i], hi_main_graph[i])]
                lo_graph += [(x_volts[i], lo_main_graph[i])]

        return main_ghaph, hi_graph, lo_graph

    def join_XY_to_graph_coordinates(self, list_X=[], list_Y=[], generate_X=False):
        new_list_Y = []
        # если не переданы значения по оси х и нас просят их сгенерировать - предполагаем, что это линии от 1 до длины list_Y
        if len(list_X) < 1 and generate_X:
            list_X = [i + 1 for i in range(len(list_Y))]

        # если лист пустой или не того формата
        if not list_Y or (isinstance(list_Y[0], int) or isinstance(list_Y[0], list)):
            print("Error: Empty Y list")

        # если кол-во точек х совпадает с у - можем поставить их как координаты
        if len(list_X) == len(list_Y) != 0:
            # если передали словарь - надо преобразовать в list Y
            # обычно такой список содержит еще список или словарь
            # также проверим что все элементы одного типа
            if [i for i in list_Y if type(i) != list_Y[0]] and isinstance(list_Y[0], list):
                for i in range(len(list_Y)):
                    new_list_Y.append(list_Y[i][0]['result'])
            elif [i for i in list_Y if type(i) != list_Y[0]] and isinstance(list_Y[0], int):
                new_list_Y = list_Y
            else:
                print('Error. Change type of lyst_Y.')

            result_list = list(zip(list_X, new_list_Y))

        return result_list

    def get_value_after_parameters(self, test_result_node, test_name):
        result_of_numeric_limit = ''
        if not (test_result_node is None):
            numeric_element = self.get_element_by_name('tr:TestResult', test_name, test_result_node)
            number = self.get_result_of_numeric_limit(numeric_element)

        return number

    def get_numeric_limit(self, test_result_node, test_name, if_result_status_is_in_TestResult=False):
        # инициализация всего словаря сделана для большей наглядности
        res_limit = {'hi': '',
                     'lo': '',
                     'comp': '',
                     'units': '',
                     'result': '',
                     'status': ''}

        if not (test_result_node is None):
            numeric_element = self.get_element_by_name('tr:TestResult', test_name, test_result_node)
            if if_result_status_is_in_TestResult == False:
                step_status = self.get_step_status(test_result_node)
            else:
                step_status = self.get_step_status(numeric_element)

            # проверка, если успешно - не пишем ничего
            res_limit['status'] = self.cancel_passed(step_status)

            res_limit['result'] = self.get_result_of_numeric_limit(numeric_element)
            limits_element = self.get_elements('tr:TestLimits/tr:Limits', numeric_element)
            if len(limits_element) > 0 and limits_element[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                # первым дочерним элементом является текстовый элемент, содержащий
                # перенос строки и символы табуляции XML-файла, поэтому нужно обращаться ко второму элементу
                first_element_in_limits = limits_element[0].childNodes.item(1)
                if not (
                        first_element_in_limits is None) and first_element_in_limits.nodeType == xml.dom.Node.ELEMENT_NODE:
                    # если предел установлен с одной стороны
                    if first_element_in_limits.tagName == 'c:SingleLimit' or first_element_in_limits.tagName == 'c:Expected':
                        res_limit['comp'] = self.get_first_attribute(first_element_in_limits, 'comparator')
                        datum_element = first_element_in_limits.childNodes.item(1)
                        if not (datum_element is None) and datum_element.nodeType == xml.dom.Node.ELEMENT_NODE:
                            res_limit['units'] = self.get_first_attribute(datum_element, 'nonStandardUnit')
                            data_type = self.get_first_attribute(datum_element, 'xsi:type')
                            lo_limit = self.get_first_attribute(datum_element, 'value')
                            res_limit['lo'] = self.get_data_from_string(lo_limit, data_type)
                    elif first_element_in_limits.tagName == 'c:LimitPair':
                        # не учитывается возможность установки OR вместо AND, т.к. OR обычно не применяется
                        if self.get_first_attribute(first_element_in_limits, 'operator') == 'AND':
                            limits_pair = self.get_child_elements_by_tag_name(first_element_in_limits, 'c:Limit')
                            for i in range(0, len(limits_pair)):
                                comp_operator = self.get_first_attribute(limits_pair[i], 'comparator')
                                res_limit['comp'] += comp_operator
                                datum_element = limits_pair[i].childNodes.item(1)
                                if not (datum_element is None) and datum_element.nodeType == xml.dom.Node.ELEMENT_NODE:
                                    if i == 0:
                                        res_limit['units'] = self.get_first_attribute(datum_element, 'nonStandardUnit')
                                    data_type = self.get_first_attribute(datum_element, 'xsi:type')
                                    lo_limit = self.get_first_attribute(datum_element, 'value')
                                    if comp_operator == 'GE' or comp_operator == 'GT':
                                        res_limit['lo'] = self.get_data_from_string(lo_limit, data_type)
                                    else:
                                        res_limit['hi'] = self.get_data_from_string(lo_limit, data_type)

        return res_limit

    def get_numeric_limits(self, substeps, name_of_substep, test_name, if_result_status_is_in_TestResult=False):
        print(test_name)
        numeric_limits = []
        correct_substeps = []
        if isinstance(name_of_substep, str) and len(substeps) > 0 and substeps[0].nodeType == xml.dom.Node.ELEMENT_NODE:
            correct_substeps = self.get_element_by_name(necessary_name=name_of_substep, list_of_elements=substeps,
                                                        isNeedOneElement=False, isUsingPath=False)
            if len(correct_substeps) > 0 and correct_substeps[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                for correct_substep in correct_substeps:
                    res_limit = self.get_numeric_limit(correct_substep, test_name, if_result_status_is_in_TestResult)
                    numeric_limits.append(res_limit)
        return numeric_limits

    def cancel_passed(self, step_status):
        if step_status == 'Passed' or step_status == 'Done':
            step_status = ' '
        return step_status

    def get_test_status_by_name(self, substeps, name_of_substep):
        status_list = []
        correct_substeps = []
        if isinstance(name_of_substep, str) and len(substeps) > 0 and substeps[0].nodeType == xml.dom.Node.ELEMENT_NODE:
            correct_substeps = self.get_element_by_name(necessary_name=name_of_substep, list_of_elements=substeps,
                                                        isNeedOneElement=False, isUsingPath=False)
            if len(correct_substeps) > 0 and correct_substeps[0].nodeType == xml.dom.Node.ELEMENT_NODE:
                for correct_substep in correct_substeps:
                    status_list.append(self.get_step_status(correct_substep))
        return status_list


# для проверки

if __name__ == '__main__':
    file = r'Main_Buf_v0.1_Report[11 47 43][19.05.2023].xml'
    cp = XMLConfigParser(file)
    d = {'head1': '%device %serialNumber', 'head2': 'ПСИ. Проверка работоспособности', 'head3': 'Нормальные условия',
         'date': 'DATE'}
    cp.get_params_for_header(d)
    for key in d:
        print(key, d[key])
    # удаление считывателя конфигурационного файла
    del cp
    file = r'Main_Buf_v0.1_Report[11 47 43][19.05.2023].xml'
    e = XMLReportParser(file)
    del e
