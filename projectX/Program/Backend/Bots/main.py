
import os
import sys

# Declare the root folder dynamically
ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

sys.path.append(ROOT_FOLDER)

print(f"Project root folder: {ROOT_FOLDER}")

# Now, you can import other modules from your project
from Program.Backend.Markets.Binance.Tools.functions import print_statement
