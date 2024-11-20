
# Delivery 1

# Group members
- Rubén Garrido - 107927
- Bruno Lopes - 68264
- André Pedro Ribeiro - 112974
- Violeta Batista Ramos - 113170

# Commands implemented
### Local commands

- [x] rep_subject_credentials <password> <credentials file>
- [x] rep_decrypt_file <encrypted file> <encryption metadata>

### Commands that use the anonymous API

- [x] rep_create_org <organization> <username> <name> <email> <public key file>
- [x] rep_list_orgs
- [x] rep_create_session <organization> <username> <password> <credentials file> <session file>
- [x] rep_get_file <file handle> [file]

__Extra command__
- [x] rep_get_pub_key <file>


### Commands that use the authenticated API

- [x] rep_list_subjects <session file> [username]
- [x] rep_list_docs <session file> [-s username] [-d nt/ot/et date]

### Commands that use the authorized API

- [x] rep_add_subject <session file> <username> <name> <email> <credentials file> 
- [x] rep_suspend_subject <session file> <username>
- [x] rep_activate_subject <session file> <username>
- [x] rep_add_doc <session file> <document name> <file>
- [x] rep_get_doc_file <session file> <document name> [file]
- [x] rep_delete_doc <session file> <document name>

__Extra command__
- [x] rep_get_doc_metadata <session file> <document name>








