from llama_index.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.tools.tool_spec.base import BaseToolSpec
from typing import Optional

class MultiplySpec(BaseToolSpec):

    spec_functions = ["multiply"]

    def multiply(self, a: Optional[int] = 6, b: Optional[int] = 2):
        "A tool for multipleing two numbers"
        return a * b

# multiply_tool = [
#     FunctionTool.from_defaults(
#         fn=multiply,
#         tool_metadata=ToolMetadata(
#             name="multiply_tool",
#             description=(
#                 "Provides the tool for multiplying"
#             )
#         )
#     )
# ]

