from enum import Enum
from typing import List
import re
import os
import glob


class MatchingPattern(Enum):
    EXACT = "EXACT"
    GLOB = "GLOB"
    REGEX = "REGEX"


def find_paths_by_pattern(paths: List[str], pattern: MatchingPattern) -> List[str]:
    if not isinstance(pattern, MatchingPattern):
        pattern = MatchingPattern(pattern)
    matched_paths = []

    for path_pattern in paths:
        if pattern == MatchingPattern.EXACT:
            if os.path.exists(path_pattern):
                matched_paths.append(os.path.abspath(path_pattern))

        elif pattern == MatchingPattern.GLOB:
            glob_matches = glob.glob(path_pattern, recursive=True)
            matched_paths.extend([os.path.abspath(match) for match in glob_matches])

        elif pattern == MatchingPattern.REGEX:
            for root, dirs, files in os.walk('.'):
                for item in files + dirs:
                    full_path = os.path.join(root, item)
                    if re.search(path_pattern, item) or re.search(path_pattern, full_path):
                        matched_paths.append(os.path.abspath(full_path))

    return list(dict.fromkeys(matched_paths))
