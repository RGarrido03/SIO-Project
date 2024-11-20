
# Delivery 1

# Group members
- Rubén Garrido - 107927
- Bruno Lopes - 68264
- André Pedro Ribeiro - 112974
- Violeta Batista Ramos - 113170

# Commands implemented
__Local commands__

- [x] rep_subject_credentials <password> <credentials file>
- [x] rep_decrypt_file <encrypted file> <encryption metadata>

__Commands that use the anonymous API__

- [x] rep_create_org <organization> <username> <name> <email> <public key file>
- [x] rep_list_orgs
- [x] rep_create_session <organization> <username> <password> <credentials file> <session file>
- [x] rep_get_file <file handle> [file]


__Commands that use the authenticated API__

- [x] rep_list_subjects <session file> [username]
- [x] rep_list_docs <session file> [-s username] [-d nt/ot/et date]

__Commands that use the authorized API__

- [x] rep_add_subject <session file> <username> <name> <email> <credentials file> 
- [x] rep_suspend_subject <session file> <username>
- [x] rep_activate_subject <session file> <username>
- [x] rep_add_doc <session file> <document name> <file>
- [x] rep_get_doc_file <session file> <document name> [file]
- [x] rep_delete_doc <session file> <document name>







