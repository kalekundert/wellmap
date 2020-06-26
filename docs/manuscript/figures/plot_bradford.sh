#!/usr/bin/env bash
set -euo pipefail

wellmap \
  bradford_assay.toml \
  ug_mL sample dilution \
  -o \$_map.svg

for f in {bradford_assay.toml,std.toml}; do
  pygmentize \
    -o ${f%.toml}_toml.svg \
    $f
done
    

