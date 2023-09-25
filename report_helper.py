def translate_en_ru(fn):
    """
    Декоратор для перевода некоторых слов с английского на русский
    """
    dictionary = {'Failed': 'Ошибка',
                  'Passed': 'Без замечаний',
                  'Skipped': 'Пропущено',
                  'Done': 'Выполнено',
                  'Aborted': 'Ошибка',
                  'UserDefined': 'Ошибка',
                  'None': '',
                  'GT': '>',
                  'LT': '<',
                  'GELE': '$\div$',
                  'GE': '$\geq$',
                  'LE': '$\leq$',
                  'NE': '\\neq'}
    if callable(fn):
        def translated(*args, **kwargs):
            raw = fn(*args, **kwargs)
            if isinstance(raw, list):
                return [dictionary.get(element, element) for element in raw]
            else:
                return dictionary.get(raw, raw)

        return translated
    else:
        if isinstance(fn, list):
            return [dictionary.get(element, element) for element in raw]
        else:
            return dictionary.get(fn, fn)


def escape(fn):
    """
    Декоратор для обработки служебных символов (добавляет слэш перед символами, которые latex считает служебными)
    """
    if callable(fn):
        def escaped(*args, **kwargs):
            raw = fn(*args, **kwargs)
            if isinstance(raw, list):
                return [element.translate(str.maketrans({'_': r'\_{}', '&': r'\&', '"': '"{}'})) for element in raw]
            else:
                return raw.translate(str.maketrans({'_': r'\_{}', '&': r'\&', '"': '"{}'}))

        return escaped
    else:
        if isinstance(fn, list):
            return [element.translate(str.maketrans({'_': r'\_{}', '&': r'\&', '"': '"{}'})) for element in raw]
        else:
            return fn.translate(str.maketrans({'_': r'\_{}', '&': r'\&', '"': '"{}'}))


class ReportHelper:
    """
    Помошник составления отчетов
    """

    def __init__(self):
        self.__list_of_headers = []
        self._value1 = 0
        self._value2 = 0
        self._remainder_of_division = 1

    def set_list_of_headers(self, list_of_headers):
        """
        Установка текущих видов заголовков отчётов
        :param list_of_headers: список словарей, из которых строится заголовок одного отчёта (список)
        """
        self.__list_of_headers = list_of_headers

    def get_header(self, index):
        """
        Получение словаря из списка словарей заголовоков под индексом index
        :param index: индекс (целое число)
        :return: словарь со строками из нужного заголовка (словарь)
        """
        return self.__list_of_headers[index]

    def add_block(self, orientation, content):
        """
             Добавление тела таблицы
             :param orientation Ориентация блока, может быть horizontal(горизонтальной) и vertical(вертикальной)
             :param content Содержимое блока в виде массива объектов {data, mode}, где data - массив значений, mode -
             режим вставки
        """
        # TODO: поменять orientation на enum

        table = []
        modes = []

        # put data in table
        for item in content:
            table.append(item['data'])
            modes.append(item['mode'])

        self.process_content(table, modes, orientation)

        table = {
            'vertical': self.transpose_table,
            'horizontal': self.prepare_horizontal_table
        }[orientation](table)

        result = ''

        for row in table:
            result += ' '.join(row) + ' \\\\'
            if orientation == 'vertical':
                for j in range(len(modes)):
                    if modes[j] == 'all':
                        result += ' \cline{' + str(j + 1) + '-' + str(j + 1) + '}'
            if orientation == 'horizontal':
                for j in range(len(row)):
                    result += ' \cline{' + str(j + 1) + '-' + str(j + 1) + '}'
            result += '\n'

        return result

    # заглушка
    def prepare_horizontal_table(self, table):
        print('prepare_horizontal_table')
        return table

    def transpose_table(self, table):
        """
        Функция траспонирования таблицы
        :param table: таблица
        :return: транспонированная таблицы
        """
        print('transpose_table')
        return [list(i) for i in zip(*table)]

    def process_content(self, table, modes, orientation):
        """
        Внутренняя функция обработки таблицы
        :param table: Таблица
        :param modes: режимы
        :param orientation: ориентация
        :return: latex-представление таблицы
        """
        {
            'vertical': self.process_vertical,
            'horizontal': self.process_horizontal
        }[orientation](table, modes)

    def process_vertical(self, table, modes):
        """
        Внутренняя функция для обработки вертикальной таблицы
        :param table: таблицы
        :param modes: режимы для колонок
        :return: latex-представление таблицы
        """

        for idx, mode in enumerate(modes):
            col = []

            # определение количества элементов в наибольшем списке из table
            max_ = 0
            for item in table:
                if len(item) > max_:
                    max_ = len(item)

            # for row in range(len(table[0])):
            for row in range(max_):
                try:
                    col.append(table[idx][row])
                except:
                    col.append('')

            {
                'all': self.process_all_mode_vertical,
                'first': self.process_first_mode_vertical
            }[mode](col, idx)

            table[idx] = col

    def process_horizontal(self, table, modes):
        """
        Внутренняя функция для обработки горизонтальной таблицы
        :param table: таблица
        :param modes: режимы для строк
        :return: latex-представление таблицы
        """
        for idx, mode in enumerate(modes):
            row = table[idx]

            {
                'all': self.process_all_mode_horizontal,
                'first': self.process_first_mode_horizontal
            }[mode](row, idx)

            table[idx] = row

    def process_all_mode_vertical(self, col, idx):
        """
         Внутренняя функция для обработки строки при формировании горизонтально-направленного блока с режимом "Все"
        :param col: Колонка
        :param idx: индекс
        :return: latex-код для данной колонки
        """
        print('process_all_mode_vertical')
        for i, item in enumerate(col):
            col[i] = (('' if idx == 0 else '& ') + item)

    def process_first_mode_vertical(self, col, idx):
        """
        Внутренняя функция для обработки строки при формировании горизонтально-направленного блока с режимом "Первый"
        :param col: колонка
        :param idx: номер строки
        :return: latex-код для данной колонки
        """
        print('process_first_mode_vertical')
        for i, item in enumerate(col):
            if i == 0:
                col[i] = (('& ' if idx != 0 else '') + '\\multirow{{{}}}{{*}}{{{}}}'.format(len(col), item))
            else:
                col[i] = ('& ' if idx != 0 else '')

    def process_all_mode_horizontal(self, row, idx):
        """
        Внутренняя функция для обработки строки при формировании горизонтально-направленного блока
        :param row: строка
        :param idx: индекс
        :return: latex-код для данной строки
        """
        print('process_all_mode_horizontal')
        for i, item in enumerate(row):
            row[i] = (('' if i == 0 else '& ') + item)

    def process_first_mode_horizontal(self, row, idx):
        """
        Внутренняя функция для обработки строки при формировании вертикально-направленнонго блока
        :param row: строка
        :param idx: индекс
        :return: latex-код для данной строки
        """
        print('process_first_mode_vertical')
        for i, item in enumerate(row):
            if i == 0:
                row[i] = '\\multicolumn{{{}}}{{l}}{{{}}}'.format(len(row), item)
            else:
                row[i] = ('')

    def get_color_for_status(self, status):
        """
        Выставление цвета для статуса
        :param status: статус
        :return: цвет
        """
        color = {'Ошибка': 'red',
                 'Пропущено': 'cyan'
                 }.get(status, 'white')
        """
        color = {'Passed': 'green',
                 'Failed': 'red',
                 'Skipped': 'cyan',
                 'Done': 'blue'
                 }.get(status, 'white')
        """
        return color

    def add_background_color(self, raw):
        """
        Добавление фоноового цвета для текста
        :param raw: текст в виде строки или списка
        :return: текст, обернутый в фоновый цвет
        """
        if isinstance(raw, list):
            colored_list = []
            for element in raw:
                color = self.get_color_for_status(element)
                colored_list.append(r'\\colorbox{{0}}{{1}}'.format(color, element))
            return colored_list
        else:
            color = self.get_color_for_status(raw)
            return ('\colorbox{' + color + '}{' + raw + '}')

    def rotate_text(self, grade, text):
        """
        Поворачивает текст на указанный градус
        :param grade: градус
        :param text: текст
        """
        result = r'\rotatebox{' + str(grade) + '}{' + text + '}'
        return result

    def add_plots(self, data, title, xlabel, ylabel, grid, height, width, rotate, precision, xmin, xmax,
                  power_of_x_axis=1, min_xlabel=0, interval_of_xlabel=0, legend_position='north west'):
        """
        Добавление графиков
        :param data: массив словарей ('function':'Название кривой', 'color':'цвет', 'mark':'метка точек', 'coordinates':'координаты (x,y)')
        :param title: заголовок всего графика (строка)
        :param xlabel: название оси Х (строка)
        :param ylabel: название оси Y (строка)
        :param grid: сетка (строка, значения: 'major' - только через основные деления, 'minor' - только через дополнительные деления, 'both', 'none')
        :param height: высота (строка, например '10cm')
        :param width: ширина (строка, например '15cm')
        :param rotate: угол поворота подписей значений на оси OX (строка)
        :param precision: количество знаков после запятой в подписях значений на оси OX (строка)
        :param xmin: начало рассматриваемого отрезка оси OX на графике (строка)
        :param xmax: конец рассматриваемого отрезка оси OX на графике (строка)
        :param legend_position: позиция подвиси легенды (строка) (Пример: north west - в левом верхнем углу, outer north east - за графиком справа)
        """
        # пример вызова: add_plots([ ('Function 1', 'blue', 'x', [(1, 3600), (5, 4200)]),
        #                            ('Function 2', 'red', '.', [(1, 3000), (3, 3500), (5, 4000)])
        #                          ],
        #                          'Заголовок Графиков', 'x', 'y', 'major', '10cm', '15cm')
        if isinstance(data, list):
            if xlabel == '' and ylabel == '':
                result = r'\begin{tikzpicture}' + '\n' \
                                                  r'\begin{axis}[' + '\n' \
                                                                     'title={' + title + '},\n' \
                                                                                         'height={' + height + '},\n' \
                                                                                                               'width={' + width + '},\n' \
                                                                                                                                   'grid={' + grid + '},\n' \
                                                                                                                                                     'xticklabel style={\n' \
                                                                                                                                                     'rotate=' + rotate + ',\n' \
                                                                                                                                                                          'xmin=' + xmin + ',\n' \
                                                                                                                                                                                           'xmax=' + xmax + ',\n' \
                                                                                                                                                                                                            '/pgf/number format/precision=' + precision + ',\n' \
                                                                                                                                                                                                                                                          '/pgf/number format/fixed,\n' \
                                                                                                                                                                                                                                                          '/pgf/number format/fixed zerofill,},\n'

            else:
                result = r'\begin{tikzpicture}' + '\n' \
                                                  r'\begin{axis}[' + '\n' \
                                                                     'title={' + title + '},\n' \
                                                                                         'xlabel={' + xlabel + '},\n' \
                                                                                                               'ylabel={' + ylabel + '},\n' \
                                                                                                                                     'height={' + height + '},\n' \
                                                                                                                                                           'width={' + width + '},\n' \
                                                                                                                                                                               'grid={' + grid + '},\n' \
                                                                                                                                                                                                 'xticklabel style={\n' \
                                                                                                                                                                                                 'rotate=' + rotate + ',\n' \
                                                                                                                                                                                                                      'xmin=' + xmin + ',\n' \
                                                                                                                                                                                                                                       'xmax=' + xmax + ',\n' \
                                                                                                                                                                                                                                                        '/pgf/number format/precision=' + precision + ',\n' \
                                                                                                                                                                                                                                                                                                      '/pgf/number format/fixed,\n' \
                                                                                                                                                                                                                                                                                                      '/pgf/number format/fixed zerofill,},\n'

            if min_xlabel != 0 and interval_of_xlabel != 0:
                result += 'xtick={' + str(min_xlabel)
                min_xlabel += interval_of_xlabel
                while min_xlabel <= int(xmax):
                    result += ', ' + str(min_xlabel)
                    min_xlabel += interval_of_xlabel
                result += '},\n'
            result += ']\n'
            for item in data:
                coord = ''
                for sub_item in item['coordinates']:
                    sub_item = list(sub_item)
                    sub_item[0] *= power_of_x_axis
                    sub_item = tuple(sub_item)
                    coord += str(sub_item) + '\n'

                if item['function'] == '':
                    result += r'\addplot[{smooth}, mark={' + item['mark'] + '}, {' + str(item['color']) + '}]\n' \
                                                                                                          'coordinates{' + coord + '};\n'
                else:
                    result += r'\addplot[{smooth}, mark={' + item['mark'] + '}, {' + str(item['color']) + '}]\n' \
                                                                                                          'coordinates{' + coord + '};\n' \
                                                                                                                                   r'\addlegendentry{' + str(
                        item['function']) + '}\n'

            result += r'\end{axis}' + '\n' \
                                      r'\end{tikzpicture}'  # + '\n'

            return result
        else:
            return 0

    def add_plot_double_Y(self, data0, data1, xlabel, ylabel0, ylabel1, height, width, ymin0=0, ymax0=100):
        """
        Добавление графиков
        :param data: массив словарей ('function':'Название кривой', 'color':'цвет', 'mark':'метка точек', 'coordinates':'координаты (x,y)')
        :param title: заголовок всего графика (строка)
        :param xlabel: название оси Х (строка)
        :param ylabel: название оси Y (строка)
        :param grid: сетка (строка, значения: 'major' - только через основные деления, 'minor' - только через дополнительные деления, 'both', 'none')
        :param height: высота (строка, например '10cm')
        :param width: ширина (строка, например '15cm')
        :param rotate: угол поворота подписей значений на оси OX (строка)
        :param precision: количество знаков после запятой в подписях значений на оси OX (строка)
        :param xmin: начало рассматриваемого отрезка оси OX на графике (строка)
        :param xmax: конец рассматриваемого отрезка оси OX на графике (строка)
        :param legend_position: позиция подвиси легенды (строка) (Пример: north west - в левом верхнем углу, outer north east - за графиком справа)
        """
        # пример вызова: add_plots([ ('Function 1', 'blue', 'x', [(1, 3600), (5, 4200)]),
        #                            ('Function 2', 'red', '.', [(1, 3000), (3, 3500), (5, 4000)])
        #                          ],
        #                          'Заголовок Графиков', 'x', 'y', 'major', '10cm', '15cm')
        print('------------------------------------------')
        ymin0 = min(data0[0]['coordinates'])[0]
        ymax0 = max(data0[0]['coordinates'], key=lambda x: x[1])[1] + 2
        print(ymax0)
        print('------------------------------------------')
        if isinstance(data0, list):
            result = r'\begin{tikzpicture}' + '\n'
            result += r'\begin{axis}[' + '\n' \
                                         'axis y line*=left,\n' \
                                         ' y axis style=blue!75!black, \n ' \
                                         'xlabel={' + xlabel + '},\n' \
                                                               'ylabel={' + ylabel0 + '},\n' \
                                                                                      'height={' + height + '},\n' \
                                                                                                            'width={' + width + '},\n' \
                                                                                                                                'ymin={' + str(
                ymin0) + '},\n' \
                         'ymax={' + str(ymax0) + '}]\n'
            # for ghaf_parameters in data0:

            result += r'\addplot[ ' \
                      '{smooth},' \
                      'mark={' + data0[0]['mark'] + '},' \
                                                    '{' + str(data0[0]['color']) + '}]\n'

            coord = '\n '
            for item in data0[0]['coordinates']:
                coord += str(item) + '\n '
            result += 'coordinates{' + coord + '};' + r'\label{plot_one}' + '\n '

            result += r'\end{axis}' + '\n'
            if isinstance(data1, list):
                result += r'\begin{axis}[' + '\n' \
                                             ' axis y line*=right, \n ' \
                                             ' y axis style=blue!80!white, \n ' \
                                             'ylabel={' + ylabel1 + '},\n' \
                                                                    'height={' + height + '},\n' \
                                                                                          'width={' + width + '},\n' \
                                                                                                              'ymin=-0.01, ymax=0.01]\n'
                result += r'\addplot[ ' \
                          '{smooth},' \
                          'mark={' + data1[0]['mark'] + '},' \
                                                        '{blue!50!white}]\n'

                coord = '\n '
                for item in data1[0]['coordinates']:
                    coord += str(item) + '\n '
                result += 'coordinates{' + coord + '};\n'

                result += r'\end{axis}' + '\n'

            result += r'\end{tikzpicture}'
            return result
        else:
            return 0

    def add_table(self, centering, caption, headers, content):
        """
        Добавляет таблицу с указанным выравниванием, названием, заголовками и содержимым
        :param centering: выравнивание
        :param caption: название таблицы
        :param headers: заголовки
        :param content: тело таблицы
        """
        result = ''
        if (not isinstance(centering, list) and not isinstance(headers, list)) or len(content) == 0:
            print('не верный тип заданных параметров!')
            return result
        result = r'\begin{longtable}{|'

        # добавление выравнивания
        for item in centering:
            if item == 'center':
                result += 'c' + '|'
            if item == 'right':
                result += 'r' + '|'
            if item == 'left':
                result += 'l' + '|'
        result += '}\n' + '\caption{' + caption + '} \\tabularnewline \hline \n'

        # добавление заголовков
        head = '&'.join(headers)
        head = head[0:len(head) - 1] + r' \tabularnewline '
        result += head + \
                  '\hline \n \endfirsthead \n' + \
                  '\multicolumn{' + str(
            len(centering)) + r'}{l} {\tablename\ \thetable\ -- {Продолжение}} \tabularnewline' + \
                  '\hline \n' + \
                  head + \
                  '\hline \n \endhead \n' + \
                  content + \
                  '\\tabularnewline \hline \n \end{longtable} \n'

        return result

    def fixed_table(self, caption, content_list):
        """
        Добавляет таблицу с указанным выравниванием, названием, заголовками и содержимым
        :param caption: название таблицы
        :param content: тело таблицы, несколько списков
        ex.:[['ЛП', 'KZ', 'KZ', 'KZ'],['ЛП', 'KZ', 'KZ', 'KZ'],['ЛП', 'KZ', 'KZ', 'KZ']]
        """
        result = ''
        # в том числе что все вложенные списки одной длины и равны 4
        if len(caption) < 1 or (not isinstance(content_list, list)) or not (
                len(set(map(len, content_list))) == 1 and set(map(len, content_list)).pop() == 4):
            print('не верный тип заданных параметров!')
            return result
        # установка размеров ячеек таблицы
        result = r'\begin{longtable}{|C{74mm}|C{22mm}|C{42mm}|C{24mm}|}' + '\n'
        # установка названия
        result += '\caption{' + caption + '} \\tabularnewline \hline \n'

        # добавление заголовка
        fixed_head = '& Измерено & Допустимое значение & Наличие ошибки' + ' \\tabularnewline '
        head = fixed_head + \
               '\hline \n \endfirsthead \n' + \
               r'\multicolumn{4}{l} {\tablename\ \thetable\ -- {Продолжение}} \tabularnewline' + \
               ' \hline \n' + \
               fixed_head + \
               ' \hline \n \endhead \n'
        result += head
        # тело таблицы построчно
        body = ''
        for content in content_list:
            body += '&'.join(content) + '\\tabularnewline \hline \n'
        result += body
        # закрываем таблицу
        result += ' \end{longtable} \n'

        return result

    def encode(self, decoded_str):
        """
        Кодирование валидного utf8 в cp1252 для работы с БД
        :param decoded_str: корректно отображаемая кириллица
        :return: cp1252 строка для работы с БД
        """
        return decoded_str.encode('cp1251').decode('cp1252')

    def decode(self, encoded_str):
        """
        Раскодирование из UTF-16 в CP1251 для нормального отображения кириллицы
        :param encoded_str: некорректно отображаемая кириллица
        :return: валидный utf8
        """
        if not isinstance(encoded_str, str):
            return "ERR"

        new_str = ''
        decoded_str = encoded_str.encode().decode().encode('UTF-16LE').decode('cp1251')
        for i in range(len(decoded_str)):
            if i % 2 == 0:
                new_str += decoded_str[i]

        return new_str

    def translate_en_to_ru(self, fn):
        """
        Декоратор для перевода некоторых часто используемых слов
        """
        dictionary = {'Failed': 'Неудачно',
                      'Passed': 'Успешно',
                      'Skipped': 'Пропущено',
                      'Done': 'Выполнено',
                      'None': ''}

        if callable(fn):
            def translated(*args, **kwargs):
                raw = fn(*args, **kwargs)
                if isinstance(raw, list):
                    return [dictionary.get(element, element) for element in raw]
                else:
                    return dictionary.get(raw, raw)

            return translated
        else:
            if isinstance(fn, list):
                return [dictionary.get(element, element) for element in raw]
            else:
                return dictionary.get(fn, fn)

    def get_list_length(self, array):
        if isinstance(array, list):
            return len(array)
        else:
            return "ERR"

    def check_comparation_type(self, lo_limit, hi_limit, comp_type, format_string):
        """
        Функция возвращает словарь из двух отформатированнных пределов измерений, lo_limit - нижний предел, hi_limit - верхний предел.
        Функция нужна для правильного заполения пределов измерений, ввиду того что тестстэнд в случае единичного типа сравнения всегда заполняет только нижний предел.
        :param hi_limit: верхний предел измерения извлеченный из Teststand (строка)
        :param lo_limit: нижний предел измерения извлеченный из Teststand (строка)
        :param comp_type: тип сравнения извлеченный из Teststand (строка)
        :param format_string: строка с модификатором вывода. Например '%.3f'.
        """
        limits = {'hi_limit': ' ', 'lo_limit': ' '}
        if hi_limit == None:
            hi_value = ' --- '
        else:
            hi_value = format_string % (float(hi_limit))
        if lo_limit == None:
            lo_value = ' --- '
        else:
            lo_value = format_string % (float(lo_limit))
        if comp_type == None:
            lo_value = ' --- '
            hi_value = ' --- '
        else:
            if comp_type == 'EQ' or comp_type == 'NE':
                hi_value = lo_value
            else:
                if comp_type == 'LT' or comp_type == 'LE' or comp_type == 'LTGT' or comp_type == 'LEGE' or comp_type == 'LEGT' or comp_type == 'LTGE':
                    dummy = lo_value
                    lo_value = hi_value
                    hi_value = dummy
        limits['lo_limit'] = lo_value
        limits['hi_limit'] = hi_value
        return limits

    def formatting_float_number(self, numb, precision=2, flags='', number_multiplication=1):
        """
        Функция форматированного вывода вещественного числа
        :param numb: форматируемое число (вещественное число, целое число или строка, представляющая собой вещественное число)
        :param precision: количество цифр после запятой (целое число)
        :param flags: флаг форматирования (строка) может принимать значения '-' (выравнивание), '+' (вывод числа со знаком даже при положительных числах), '0' (наличие ведущих модулей)
        :param number_multiplication: число, на которое домножается numb (число)
        """
        result = ('%' + flags + '.' + str(precision) + 'f') % (float(numb) * number_multiplication)
        # удаление знака '-', если округлённое число равно нулю
        if flags == '' and result[0] == '-':
            is_zero = True
            for i in range(1, len(result)):
                if result[i] != '.' and result[i] != '0':
                    is_zero = False
                    break
            if is_zero:
                result = result[1:]
        return result

    def get_multiplication_for_after_comma(self, n):
        '''
        функция преобразования числа знаков после запятой в множитель( 3 -> 0.001)
        :param n: число знаков, необоходимых "после запятой"
        :return: множитель
        '''
        out = 1
        for _ in range(n):
            out *= 0.1
        return self.formatting_float_number(numb=out, precision=n)

    def exist_test(self, seq, index=0):
        """
        Вывод элемента списка или словаря seq[index], если он существует, иначе вывод длинного тире или непустой строки seq
        :param seq: (список)
        :param index: индекс необходимого элемента (целое число) или ключ словаря (неизменяемый тип)
        """
        if isinstance(seq, list):
            if len(seq) > index:
                return seq[index]
            else:
                return '---'
        elif isinstance(seq, dict):
            if index in seq:
                return seq[index]
            else:
                return '---'
        elif isinstance(seq, str):
            if seq == '':
                return '---'
            else:
                return seq
        else:
            return seq

    @translate_en_ru
    @escape
    def exist_result(self, seq, index=0, precision=2, flags='', number_multiplication=1):
        """
        Форматированный вывод элемента списка seq[index], если он существует, иначе форматированный вывод переданного в функцию элемента
        :param seq: (список)
        :param index: индекс необходимого элемента (целое число)
        :param precision: количество цифр после запятой (целое число)
        :param flags: флаг форматирования (строка) может принимать значения '-' (выравнивание), '+' (вывод числа со знаком даже при положительных числах), '0' (наличие ведущих модулей)
        :param number_multiplication: число, на которое домножается числовой элемент списка seq[index] (число)
        """
        number_multiplication = float(number_multiplication)
        dop_numb = self.exist_test(seq, index)
        try:
            numb = self.formatting_float_number(dop_numb, precision, flags, number_multiplication)
        except ValueError:
            numb = dop_numb
        except TypeError:
            numb = dop_numb
        numb = str(numb)
        return numb

    def exist_limits(self, dic, key, precision=2, flags='', number_multiplication=1, up=1):
        """
        Форматированный вывод погрешности или элементов словаря dic
        :param seq: (словарь, имеющий обязательныеельные поля 'hi' и 'lo' для вычисления погрешности)
        :param key: ключ, по которому определяется возвращаемое значение словаря, особое значение 'ocur' означает вывод погрешности значений (строка)
        :param precision: количество цифр после запятой (целое число)
        :param flags: флаг форматирования (строка) может принимать значения '-' (выравнивание), '+' (вывод числа со знаком даже при положительных числах), '0' (наличие ведущих модулей)
        :param number_multiplication: число, на которое домножается считываемый элемент списка предела (число)
        :param up: смещение от номинального значения вверх (число)
        """
        if isinstance(dic, dict):
            if key == 'ocur':
                limit = self.formatting_float_number(abs(dic['hi'] - dic['lo']) / 2, precision, flags,
                                                     number_multiplication)
            elif key == 'modified_comp':
                if dic['comp'] == 'LE':
                    limit = self.formatting_float_number(0.0, precision, flags) + '$\div$'
                else:
                    limit = dic['comp']
            elif key == 'comp' or key == 'units' or key == 'status':
                limit = dic[key]
            elif key == 'median':
                limit = self.formatting_float_number(dic['lo'] + abs(dic['hi'] - dic['lo']) / 2, precision, flags,
                                                     number_multiplication)
            elif key == 'hi-up':
                limit = self.formatting_float_number(dic['hi'] - up, precision, flags, number_multiplication)
            else:
                limit = self.formatting_float_number(dic[key], precision, flags, number_multiplication)
        else:
            limit = '---'
        return limit

    def name_of_table(self, file_name):
        """
        Функция вывода названия
        :param file_name: имя файла, по которому определится название
        :return: название таблицы (строка)
        """
        # если найдет это имя => вернет номер файла, что надо выполнить
        if file_name.find('Load Controller') != -1:
            return 'Load Controller'
        if file_name.find('OneWire') != -1:
            return 'OneWire'
        if file_name.find('RS-485') != -1:
            return 'RS-485'
        if file_name.find('Batteries') != -1:
            return '4'
        if file_name.find('Onboard and technological PSU') != -1:
            return 'Onboard and technological PSU'
        if file_name.find('CAN') != -1:
            return 'Проверка информационной линии CAN'
        if file_name.find('SPI') != -1:
            return 'SPI'
        if file_name.find('ISS') != -1:
            return 'ISS'
        if file_name.find('1S') != -1:
            return '1S'
        if file_name.find('Accumulator cells') != -1:
            return 'Accumulator cells'
        if file_name.find('Commands') != -1:
            return 'Commands'
        if file_name.find('Thermo') != -1:
            return 'Thermo'
        if file_name.find('Pressure') != -1:
            return 'Pressure'
        if file_name.find('PEC') != -1:
            return 'PEC'

        return 'Undefined'

    def number_of_step(self, name_of_step):
        """
        Функция вывода номера шага испытания из его названия
        :param name_of_step: имя шага, по которому определится номер
        :return: номер шага (строка)
        """
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
        number = int(number)

        return str(number)

    def split_name(self, name_of_step):
        """
        функция разделения имени шага на его номер и название
        :param name_of_step: название шага (строка)
        :return: список из имени полного номера и из имени шага без его номера
        """
        index = 0
        res = []
        for i in range(0, len(name_of_step)):
            # if name_of_step[i].isdigit() or name_of_step[i] == '.' or name_of_step[i] == ' '
            if name_of_step[i].isalpha():
                if name_of_step[i - 1].isdigit():
                    index = i - 1
                else:
                    index = i
                break
        if index == 0:
            res.append('0 ')
        else:
            res.append(name_of_step[:index])  # полный номер шага
        res.append(name_of_step[index:])  # имя шага без номера
        for i in range(len(res[0]) - 1, 0, -1):
            if res[0][i].isdigit():
                index = i
                break
        res[0] = res[0][:index + 1]
        return res

    def number_of_decimal_places(self, number):
        """
        Функция подсчёта количества десятичных цифр после запятой
        :param number: интересующее число (целое число, вещественное число (float), строка)
        :return: количество цифр после запятой (целое число)
        """
        if isinstance(number, int):
            return 0
        if isinstance(number, float):
            number = str(number)
        if not isinstance(number, str):
            return -1
        index1 = number.find('.')
        # если дано целое число в виде строки
        if index1 == -1:
            return 0
        index2 = number.find('e')
        length = len(number)
        # если вещественное число представлено не в экспоненциальном виде
        if index2 == -1:
            return length - index1 - 1
        # если вещественное число представлено в экспоненциальном виде
        else:
            return (index2 - index1 - 1) + int(number[index2 + 2:])

    def sort_list_of_steps(self, seq):
        """
        Функция сортировки списка словарей шагов тестирования методом пузырька
        :param seq: список словарей шагов тестирования (список)
        """
        length_of_list = len(seq)
        for j in range(1, length_of_list):
            for i in range(0, length_of_list - j):
                if int(self.number_of_step(seq[i]['step_name'])) > int(self.number_of_step(seq[i + 1]['step_name'])):
                    mem = seq[i + 1].copy()
                    seq[i + 1] = seq[i].copy()
                    seq[i] = mem.copy()

    def split_on_rows(self, text, numb_of_symbols_in_row):
        """
        Функция разбиения предложения на строки по numb_of_symbols_in_row символов без переноса слов
        :param text: предложение для разбиения (строка) не содержит двойных пробелов, пробелов в начале и в конце предложения, символов \t и \n
        :param numb_of_symbols_in_row: максимально возможное количество символов в одной строке
        :return: список, первый элемента которого указывает количество получившихся строк, второй элемент - список из получившихся строк
        """
        length_of_text = len(text)
        if length_of_text <= numb_of_symbols_in_row:
            return [1, [text]]
        else:
            res = [0, []]
            mem_index_down = 0
            mem_index_median = 0
            mem_index_up = 0
            for i in range(0, length_of_text):
                if text[i] == ' ':
                    mem_index_median = mem_index_up
                    mem_index_up = i
                    if mem_index_up - mem_index_down >= numb_of_symbols_in_row:
                        if mem_index_up - mem_index_down == numb_of_symbols_in_row:
                            mem_index_median = mem_index_up
                        else:
                            # когда слово больше заданного количества символов
                            if mem_index_median + 1 == mem_index_down or mem_index_median == mem_index_down:
                                return [-1, []]
                        res[0] += 1
                        res[1].append(text[mem_index_down:mem_index_median])
                        mem_index_down = mem_index_median + 1
                else:
                    if i == length_of_text - 1:
                        # единица прибавляется, так как i и mem_index_down входят в слово
                        if i - mem_index_down + 1 > numb_of_symbols_in_row:
                            # когда самое первое или самое последнее слово больше заданного количества символов
                            if mem_index_up == mem_index_down or i - mem_index_up > numb_of_symbols_in_row:
                                return [-1, []]
                            else:
                                res[0] += 2
                                res[1].append(text[mem_index_down:mem_index_up])
                                res[1].append(text[mem_index_up + 1:])
                        else:
                            res[0] += 1
                            res[1].append(text[mem_index_down:])
            return res

    def add_multirow_command_in_rows(self, list_of_rows):
        """
        Функция добавления команды \multirow к каждому строковому элементу списка, остальные элементы в списке пропускаются
        :param list_of_rows: список, к строковым элементам которого нужно добавить команду \multirow
        """
        if isinstance(list_of_rows, list):
            for i in range(0, len(list_of_rows)):
                if isinstance(list_of_rows[i], str):
                    list_of_rows[i] = '\\multirow{2}{*}{' + list_of_rows[i] + '}'

    def split_on_rows_with_max_count_rows(self, text, numb_of_symbols_in_row, max_count_of_rows):
        """
        Функция разбиения и размещения полученных после разбиения текста text строк среди доступных строк, количество которых равно max_count_of_rows.
        :param text: предложение для разбиения (строка)
        :param numb_of_symbols_in_row: максимально возможное количество символов в одной строке
        :param max_count_of_rows: доступное количество строк
        :return: список, первый элемент которого указывает на необходимость использования \multirow в LaTeX в каждой выводимой строке (при 0 использовать \multirow не нужно,
        при 1 использовать \multirow нужно). Второй элемент состоит из списка строк длиной max_count_of_rows, в которые вводятся строки из text
        """
        internal_split = self.split_on_rows(text, numb_of_symbols_in_row)
        res = [0, []]
        for i in range(0, max_count_of_rows):
            res[1].append('')
        # если text не влазит в доступные строки
        if max_count_of_rows < internal_split[0]:
            res[0] = -1
            return res
        mid_of_available_rows = int((max_count_of_rows - 1) / 2)
        mid_of_text_rows = int((internal_split[0] - 1) / 2)
        offset_from_center = 0
        offset_to_right_of_center = 0
        offset_to_left_of_center = 0
        if internal_split[0] % 2 == 1:
            if max_count_of_rows % 2 == 0:
                res[0] = 1
                self.add_multirow_command_in_rows(internal_split[1])
            res[1][mid_of_available_rows] = internal_split[1][mid_of_text_rows]
            offset_from_center = 1
        elif max_count_of_rows % 2 == 1:
            res[0] = 1
            self.add_multirow_command_in_rows(internal_split[1])
            offset_to_left_of_center = 1
        else:
            offset_to_right_of_center = 1
        for i in range(0, internal_split[0] // 2):
            res[1][mid_of_available_rows - offset_from_center - offset_to_left_of_center] = internal_split[1][
                mid_of_text_rows - offset_from_center]
            res[1][mid_of_available_rows + offset_from_center + offset_to_right_of_center] = internal_split[1][
                mid_of_text_rows + offset_from_center + offset_to_right_of_center + offset_to_left_of_center]
            offset_from_center += 1
        return res

    def clean_date(self, date_and_time):
        """
        В XML файле даты хранятся с английской буквой "T" между датой и временем, а также с миллисекундами.
        Это функция убирает эти данные из строки.
        :param date_and_time: дата и время из XML (строка)
        :return: отформатированнные дата и время
        """
        if isinstance(date_and_time, str):
            date_and_time = date_and_time.replace('T', ' ')
            dot_index = date_and_time.find('.')
            if dot_index != -1:
                date_and_time = date_and_time[:date_and_time.index('.')]
        return date_and_time

    def counter1_value(self):
        self._value1 += 1
        return self._value1

    def counter1_value_re_null(self):
        self._value1 = 0
        return self._value1

    def counter2_value(self):
        self._value2 += 1
        return self._value2

    def counter2_value_re_null(self):
        self._value2 = 0
        return self._value2

    def remainder(self, a, b):
        self._remainder_of_division = a % b
        return self._remainder_of_division
