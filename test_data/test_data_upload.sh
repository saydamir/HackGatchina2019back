cd img; for i in `ls`; do curl -s -X POST -H "Content-Type: multipart/form-data" -F "file=@${i}" $1/images ;done ; cd ..

cd test_issues; for i in `ls`; do curl -s -H "Content-Type: application/json" -X POST -d "@${i}" $1/issues ;done