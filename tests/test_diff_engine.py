import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from diff_engine import parse_patch


def run_test(title, patch):

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    changes = parse_patch(patch)

    for change in changes:

        print(f"\nLine {change.line}")

        if change.removed:
            print("\nRemoved:")
            for line in change.removed:
                print(line)

        if change.added:
            print("\nAdded:")
            for line in change.added:
                print(line)


# --------------------------------------------------------
# TEST 1
# Single-line replacement
# --------------------------------------------------------

patch1 = """@@ -1,3 +1,3 @@
-print("Hello")
+print("Hello World")
"""

run_test("TEST 1 - Single Replacement", patch1)


# --------------------------------------------------------
# TEST 2
# Multi-line replacement
# --------------------------------------------------------

patch2 = """@@ -5,3 +5,3 @@
-x = 10
-y = 20
+a = 100
+b = 200
"""

run_test("TEST 2 - Multi-line Replacement", patch2)


# --------------------------------------------------------
# TEST 3
# Pure insertion
# --------------------------------------------------------

patch3 = """@@ -8,2 +8,5 @@
 print("Start")
+name = "Atin"
+age = 22
+city = "Delhi"
 print("End")
"""

run_test("TEST 3 - Pure Insertion", patch3)


# --------------------------------------------------------
# TEST 4
# Pure deletion
# --------------------------------------------------------

patch4 = """@@ -15,5 +15,2 @@
-x = 10
-y = 20
-z = 30
 print("Done")
"""

run_test("TEST 4 - Pure Deletion", patch4)


# --------------------------------------------------------
# TEST 5
# Multiple change blocks
# --------------------------------------------------------

patch5 = """@@ -1,8 +1,8 @@
-print("One")
+print("ONE")

 print("Middle")

-a = 10
+a = 20

 print("End")
"""

run_test("TEST 5 - Multiple Change Blocks", patch5)