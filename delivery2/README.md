
# Delivery 2

# Group members
- Rubén Garrido - 107927
- Bruno Lopes - 68264
- André Pedro Ribeiro - 112974
- Violeta Batista Ramos - 113170

# Commands implemented

### Commands that use the authenticated API

- [ ] rep_assume_role <session file> <role>
- [ ] rep_drop_role <session file> <role>
- [ ] rep_list_roles <session file> <role>
- [ ] rep_list_role_subjects <session file> <role>
- [ ] rep_list_subject_roles <session file> <username>
- [ ] rep_list_role_permissions <session file> <role>
- [ ] rep_list_permission_roles <session file> <permission>


### Commands that use the authorized API

- [ ] rep_add_role <session file> <role>
- [ ] rep_suspend_role <session file> <role>
- [ ] rep_reactivate_role <session file> <role>
- [ ] rep_add_permission <session file> <role> <username>
- [ ] rep_remove_permission <session file> <role> <username>
- [ ] rep_add_permission <session file> <role> <permission>
- [ ] rep_remove_permission <session file> <role> <permission>
- [ ] rep_acl_doc <session file> <document name> [+/-] <role> <permission>


# How to run the delivery

```shell
# at the directory delivery1
docker compose -f compose.prod.yaml up 

```

# How to test the delivery

```shell
# at the directory delivery1
cd client
pytest

```

# How to use each command

```shell
# at the directory delivery1
cd client/exec_commands
command <args>
```