# Test commands

**NOTE**: All commands feature a `--help` flag that can be used to get more information about the command.

## Environment variables

```shell
export ORG_NAME="UA"

export FULL_NAME_1="Alice"
export USERNAME_1="alice"
export PASSWORD_1="PASSWORD_1"
export EMAIL_1="alice@ua.pt"
export PRIVATE_KEY_1="./storage/repository/mykey"
export PUBLIC_KEY_1="./storage/repository/mykey.pub"

export FULL_NAME_2="Bob"
export USERNAME_2="bob"
export PASSWORD_2="PASSWORD_2"
export EMAIL_2="bob@ua.pt"
export PRIVATE_KEY_2="./storage/repository/mykey2"
export PUBLIC_KEY_2="./storage/repository/mykey2.pub"

export FILE_PATH_1="./bolo.txt"
export FILE_NAME_1="bolo"

export FILE_PATH_2="./claudia nayara.txt"
export FILE_NAME_2="claudia nayara"

export ROLE_1="Managers"
export ROLE_2="Employees"

# This can be retrieved using the command rep_get_pub_key
export REP_PUB_KEY="./storage/repository/repo_pub_key.pem"
export REP_ADDRESS="localhost:8000"
```

## Credentials

```shell
python3 main.py rep_subject_credentials $PASSWORD_1 $PRIVATE_KEY_1
python3 main.py rep_subject_credentials $PASSWORD_2 $PRIVATE_KEY_2
```

## Organization

```shell
python3 main.py rep_create_org $ORG_NAME $USERNAME_1 $FULL_NAME_1 $EMAIL_1 $PUBLIC_KEY_1
python3 main.py rep_list_orgs
```

## Sessions

```shell
python3 main.py rep_create_session $ORG_NAME $USERNAME_1 $PASSWORD_1 $PRIVATE_KEY_1
export SESSION_FILE=./storage/sessions/... # Complete with given path

python3 main.py rep_assume_role $SESSION_FILE $ROLE_1
python3 main.py rep_list_roles $SESSION_FILE  # Check Managers role is present
python3 main.py rep_drop_role $SESSION_FILE $ROLE_1
python3 main.py rep_list_roles $SESSION_FILE  # Check no roles are present
python3 main.py rep_assume_role $SESSION_FILE $ROLE_1  # Load it back
```

## Subjects

```shell
python3 main.py rep_add_subject $SESSION_FILE $USERNAME_2 $FULL_NAME_2 $EMAIL_2 $PUBLIC_KEY_2
python3 main.py rep_suspend_subject $SESSION_FILE $USERNAME_2
python3 main.py rep_activate_subject $SESSION_FILE $USERNAME_2
python3 main.py rep_list_subjects $SESSION_FILE
python3 main.py rep_list_subjects $SESSION_FILE $USERNAME_1
```

## Roles

### Organization roles

```shell
python3 main.py rep_list_role_permissions $SESSION_FILE $ROLE_1

python3 main.py rep_add_role $SESSION_FILE $ROLE_2  # Add new role to organization
python3 main.py rep_suspend_role $SESSION_FILE $ROLE_2
python3 main.py rep_reactivate_role $SESSION_FILE $ROLE_2

python3 main.py rep_add_permission $SESSION_FILE $ROLE_2 ROLE_ACL
python3 main.py rep_list_role_permissions $SESSION_FILE $ROLE_2
python3 main.py rep_list_permission_roles $SESSION_FILE ROLE_ACL
python3 main.py rep_remove_permission $SESSION_FILE $ROLE_2 ROLE_ACL
python3 main.py rep_list_role_permissions $SESSION_FILE $ROLE_2  # Confirm it was removed
```

### Subject roles

```shell
python3 main.py rep_add_permission $SESSION_FILE $ROLE_1 $USERNAME_2
python3 main.py rep_add_permission $SESSION_FILE $ROLE_2 $USERNAME_1
python3 main.py rep_list_role_subjects $SESSION_FILE $ROLE_1  # Should list two users
python3 main.py rep_list_subject_roles $SESSION_FILE $USERNAME_1  # Should list two roles
python3 main.py rep_remove_permission $SESSION_FILE $ROLE_2 $USERNAME_1
python3 main.py rep_list_subject_roles $SESSION_FILE $USERNAME_1  # Should list one role
```

## Documents

### Management

```shell
python3 main.py rep_add_doc $SESSION_FILE $FILE_NAME_1 $FILE_PATH_1
python3 main.py rep_add_doc $SESSION_FILE "$FILE_NAME_2" "$FILE_PATH_2"

python3 main.py rep_get_file <replace_with_file_handle>
python3 main.py rep_get_doc_metadata $SESSION_FILE $FILE_NAME_1
python3 main.py rep_decrypt_file $FILE_NAME_1 storage/docs/"$ORG_NAME"/"$FILE_NAME_1".json

python3 main.py rep_get_doc_file $SESSION_FILE $FILE_NAME_1

python3 main.py rep_list_docs $SESSION_FILE
python3 main.py rep_list_docs $SESSION_FILE --username $USERNAME_1
python3 main.py rep_list_docs $SESSION_FILE --date <nt|ot|et> <date>  # Date filtering is not available in these test commands due to obvious reasons

python3 main.py rep_delete_doc $SESSION_FILE $FILE_NAME_1
```

### ACL

```shell
python3 main.py rep_acl_doc $SESSION_FILE $FILE_NAME_1 + $ROLE_1 DOC_DELETE
python3 main.py rep_acl_doc $SESSION_FILE $FILE_NAME_1 + $ROLE_2 DOC_ACL
python3 main.py rep_acl_doc $SESSION_FILE $FILE_NAME_1 - $ROLE_1 DOC_DELETE
```