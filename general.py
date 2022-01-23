import yaml

def isTicket(catid):
    all_ticket_cat_ids = open_yaml("categories")
    isTicketBool = False

    for ticket_cat_id in all_ticket_cat_ids:
        if catid == ticket_cat_id:
            isTicketBool = True
            
    return isTicketBool

def open_yaml(name):
    stream = open('settings/general.yaml', 'r')
    yaml_content = yaml.safe_load(stream)
    return yaml_content[name]

def get_next_category(current_category):
    yaml_content = open_yaml("categories")
    current_index = yaml_content.index(current_category)

    if current_index != 0:
        return yaml_content[current_index - 1]

def return_role_id(role_name):
    yaml_content = open_yaml("permissions")
    return yaml_content['all_roles'][role_name.lower()]

def return_log_channel_id(log_perm):
    yaml_content = open_yaml("permissions")
    return yaml_content['log_channels'][log_perm.lower()]

def check_perms(roles, ctx):
    yaml_content = open_yaml("permissions")
    setting_roles = yaml_content[roles]
    tmp_roles = ctx.author.roles
    roles = []
    for value in tmp_roles:
        roles.append(value.id)

    has_perms = False
    for x in setting_roles:
        for y in roles:
            if x == y:
                has_perms = True
                break
        else:
            continue
        break
    
    return has_perms;