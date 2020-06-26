#!/usr/bin/env bash
set -euo pipefail

wellmap \
  well_groups.toml \
  x y z u v w \
  -o \$_map.svg

pygmentize \
  -o well_groups_toml.svg \
  well_groups.toml
