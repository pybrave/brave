from enum import Enum

class ScriptName(str,Enum):
    main = "main"
    input_parse = "input_parse"
    output_parse = "output_parse"
