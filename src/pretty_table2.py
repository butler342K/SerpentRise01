from prettytable import HRuleStyle, PrettyTable
def wrap_text(text, max_width):
    """
    Разбивает текст на строки заданной максимальной ширины,
    вставляя \n только вместо пробелов (не разрывая слова).
    
    :param text: Исходная строка
    :param max_width: Максимальная ширина строки (N символов)
    :return: Строка с переносами
    """
    if not text or max_width <= 0:
        return text
    
    # Если строка короче максимальной ширины, возвращаем как есть
    if len(text) <= max_width:
        return text
    
    words = text.split()
    if not words:
        return text
    
    lines = []
    current_line = ""
    
    for word in words:
        # Если добавление слова превысит максимальную ширину
        if current_line and len(current_line) + 1 + len(word) > max_width:
            lines.append(current_line)
            current_line = word
        else:
            # Добавляем слово к текущей строке
            if current_line:
                current_line += " " + word
            else:
                current_line = word
    
    # Добавляем последнюю строку
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)

def draw_table(headers, data):
    """
    Generate a formatted table using PrettyTable.

    :param headers (list): Column headers.
    :param data (list of lists): Table rows.
    :param maxcolwidths (list, optional): Max width for each column.
    :param allhlines (bool, optional): Draw horizontal lines for all rows. Default is False.

    :return: PrettyTable: A formatted table.
    """
    # hrules =  if allhlines else HRuleStyle.FRAME

    table = PrettyTable(
        vertical_char="│",
        horizontal_char="─",
        junction_char="┼",
        top_junction_char="┬",
        bottom_junction_char="┴",
        right_junction_char="┤",
        left_junction_char="├",
        top_right_junction_char="╮",
        top_left_junction_char="╭",
        bottom_right_junction_char="╯",
        bottom_left_junction_char="╰",
        hrules=HRuleStyle.ALL,
        align="l",
    )

    table.field_names = headers
    for txt in data:
        # Wrap text for each cell
        wrapped_row = [wrap_text(str(cell), 80) for cell in txt]
        table.add_row(wrapped_row)
    return table




# print_command_list()