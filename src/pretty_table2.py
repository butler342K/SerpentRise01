from prettytable import HRuleStyle, PrettyTable
def wrap_text(text, max_width):
    """
    Splits the text into lines of a given maximum width,
    inserting \n only at spaces (without breaking words).
    
    :param text: Input string
    :param max_width: Maximum line width (N characters)
    :return: String with line breaks
    """
    if not text or max_width <= 0:
        return text
    
    if len(text) <= max_width:
        return text
    
    words = text.split()
    if not words:
        return text
    
    lines = []
    current_line = ""
    
    for word in words:
        # If adding the word exceeds the maximum width
        if current_line and len(current_line) + 1 + len(word) > max_width:
            lines.append(current_line)
            current_line = word
        else:
            # Add the word to the current line
            if current_line:
                current_line += " " + word
            else:
                current_line = word
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)

def draw_table(headers, data, maxcolwidths=80):
    """
    Generate a formatted table using PrettyTable.

    :param headers (list): Column headers.
    :param data (list of lists): Table rows.
    :param maxcolwidths (list, optional): Max width for each column.
    :param allhlines (bool, optional): Draw horizontal lines for all rows. Default is False.

    :return: PrettyTable: A formatted table.
    """
    # maxcolumn width depends on the terminal size
    col_widths = maxcolwidths // 4

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
        wrapped_row = [wrap_text(str(cell), col_widths) for cell in txt]
        table.add_row(wrapped_row)
    return table
