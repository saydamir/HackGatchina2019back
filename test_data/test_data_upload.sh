cd img; for i in `ls`; do curl -s -X POST -H "Content-Type: multipart/form-data" -F "file=@${i}" http://localhost:5000/images ;done ; cd ..

cd test_issues; for i in `ls`; do curl -s -X POST -d "@${i}" http://localhost:5000/issues ;done
