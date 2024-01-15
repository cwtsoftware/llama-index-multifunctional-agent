from llama_index.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.tools.tool_spec.base import BaseToolSpec
import re

class CalendarSpec(BaseToolSpec):

    spec_functions = ["calendar"]

    def calendar(self):
        "A tool for creating calendar input"
        calendar_html = """
            <form action="/action_page.php">
                <label for="birthday">Birthday:</label>
                <input type="date" id="birthday" name="birthday">
                <input type="submit">
            </form>     
        """
        return re.sub(r'\s{2,}', ' ', calendar_html).replace('\n', '').strip()
