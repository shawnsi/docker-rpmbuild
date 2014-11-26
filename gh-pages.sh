#!/bin/bash
cd docs
make html
cd _build/html
touch .nojekyll
git init
git config user.name "Travis-CI"
git config user.email "travis@shawnsi.github.io"
git add .
git commit -m "Deployed to Github Pages"
git push --force --quiet "https://${GH_TOKEN}@${GH_REF}" master:gh-pages > /dev/null 2>&1
