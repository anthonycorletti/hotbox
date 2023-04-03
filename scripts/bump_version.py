#!/usr/bin/env python

from enum import Enum, unique

from packaging.version import Version

from hotbox import __version__


@unique
class BumpType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    MICRO = "micro"


def bump_version(version: str, bump: BumpType) -> str:
    """Bump a version string.

    Args:
        version (str): The version string to bump.
        bump (str): The type of bump to perform.

    Returns:
        str: The bumped version string.
    """
    v = Version(version)
    if bump == BumpType.MAJOR:
        v = Version(f"{v.major + 1}.0.0")
    elif bump == BumpType.MINOR:
        v = Version(f"{v.major}.{v.minor + 1}.0")
    elif bump == BumpType.MICRO:
        v = Version(f"{v.major}.{v.minor}.{v.micro + 1}")
    else:
        raise ValueError(f"Invalid bump type: {bump}")
    return str(v)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Bump the version string.",
    )
    parser.add_argument(
        "-b",
        dest="bump",
        type=BumpType,
        default="micro",
        help="The type of bump to perform. One of "
        f"{list(map(lambda x: x.value, BumpType))}.",
    )
    args = parser.parse_args()
    print(f"Current version: {__version__}")
    new_version = bump_version(__version__, args.bump)
    print(f"New version: {new_version}")
    # write new version to the file
    with open("hotbox/__init__.py", "r") as f:
        lines = f.readlines()
    with open("hotbox/__init__.py", "w") as f:
        for line in lines:
            if line.startswith("__version__"):
                f.write(f'__version__ = "{new_version}"')
            else:
                f.write(line)
