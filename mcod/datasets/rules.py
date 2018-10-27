import rules

from mcod.lib.rules import assigned_to_organization, users_is_editor

rules.add_perm('datasets', rules.always_allow)
rules.add_perm('datasets.add_dataset', assigned_to_organization)
rules.add_perm('datasets.view_dataset', assigned_to_organization)
rules.add_perm('datasets.change_dataset', assigned_to_organization)
rules.add_perm('datasets.delete_dataset', users_is_editor)

rules.add_perm('datasets.view_trash', users_is_editor)
rules.add_perm('datasets.change_trash', users_is_editor)
