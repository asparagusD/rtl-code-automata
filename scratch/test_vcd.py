import sys
from pyDigitalWaveTools.vcd.parser import VcdParser

parser = VcdParser()
with open('examples/counter_debug.vcd', 'r') as f:
    parser.parse(f)

for name, child in parser.scope.children['counter_debug'].children.items():
    print(f"{name}:")
    print(f"  type: {type(child).__name__}")
    if hasattr(child, 'data'):
        print(f"  data: {child.data[:3] if child.data else 'empty'}")
    if hasattr(child, 'size'):
        print(f"  size: {child.size}")
