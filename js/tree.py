# tree.py
import json
import os

CURRENT_DIR = os.path.dirname(__file__)
TREE_JSON = os.path.join(CURRENT_DIR, "decision_tree.json")

with open(TREE_JSON, "r", encoding="utf-8") as f:
    decisionTree = json.load(f)
