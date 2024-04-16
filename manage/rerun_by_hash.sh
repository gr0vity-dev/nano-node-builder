hash=$1
git pull
rm $(find . -name "$hash*")
git add . -u
git commit -m "Re-run testsuite on $hash"
git push