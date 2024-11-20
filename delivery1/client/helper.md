```bash
export REP_ADDRESS=localhost:8000
export REP_PUB_KEY=./storage/repository/repo_pub_key.pem
export SESSION_FILE=./storage/sessions/...

python3 main.py  rep_subject_credentials password storage/repository/mykey
python3 main.py rep_create_org UA andre Andre andre@andre.pt ./storage/repository/mykey.pub
python3 main.py rep_create_session UA andre password ./storage/repository/mykey
python3 main.py rep_add_doc storage/sessions/UA/.b2affb4e73c45145916f2fadb8b82dda30151c2ce894af070d29da9548e2270281449accf2366a7b4aa638e21b49b05a96027ea69a84d9af52cf642863dcf8a9 filename ./output.txt
python3 main.py rep_get_file 4c50648a1548fe60334ebbf3e5706d45d555553e96e649732744bbbdeea2ccf2 
python3 main.py rep_get_doc_metadata $SESSION_FILE filename
python3 main.py rep_decrypt_file filename storage/docs/UA/filename.json


```

```bash
#All commandos
# local
@app.command("rep_subject_credentials") X
@app.command("rep_decrypt_file")

#anonymous
@app.command("rep_create_org") X
@app.command("rep_list_orgs") X
@app.command("rep_create_session") X
@app.command("rep_get_file")
@app.command("rep_get_pub_key") X
@app.command("rep_ping") X

#authenticated
@app.command("rep_list_subjects") X
@app.command("rep_list_docs") X

#authorized
@app.command("rep_add_doc") X
@app.command("rep_get_doc_metadata") X
@app.command("rep_get_doc_file") X
@app.command("rep_delete_doc") X
@app.command("rep_add_subject") X
@app.command("rep_suspend_subject") X
@app.command("rep_activate_subject") X

```