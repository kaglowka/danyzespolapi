# -*- coding: utf-8 -*-
# from mcod.tools.resources import PingResource

from mcod.applications import views as app_views
from mcod.articles import views as article_views
from mcod.datasets import views as dataset_views
from mcod.organizations import views as org_views
from mcod.resources import views as res_views
from mcod.tools import views as tools_views
from mcod.users import views as user_views
from mcod.following import views as following_views
from mcod.histories import views as history_views
from mcod.searchhistories import views as searchhistory_views

routes = [
    # Tools & utilities
    ('/stats', tools_views.StatsView()),
    ('/cluster/health', tools_views.ClusterHealthView()),
    ('/cluster/explain', tools_views.ClusterAllocationView()),
    ('/cluster/state', tools_views.ClusterStateView()),
    # User
    ('/auth/login', user_views.LoginView()),
    ('/auth/logout', user_views.LogoutView()),
    ('/auth/password/reset', user_views.ResetPasswordView()),
    ('/auth/password/reset/{token:uuid}/', user_views.ConfirmResetPasswordView()),
    ('/auth/password/change', user_views.ChangePasswordView()),
    ('/auth/user', user_views.AccountView()),
    ('/auth/registration', user_views.RegistrationView()),
    ('/auth/registration/verify-email/{token:uuid}/', user_views.VerifyEmailView()),
    ('/auth/registration/resend-email', user_views.ResendActivationEmailView()),
    ('/applications', app_views.ApplicationsView()),
    ('/applications/{id:int}', app_views.ApplicationView()),
    ('/applications/{id:int}/history', app_views.ApplicationHistoryView()),
    ('/applications/{id:int}/datasets', app_views.ApplicationDatasetsView()),
    ('/applications/{id:int}/follow', following_views.FollowApplication()),
    ('/applications/followed', following_views.ListOfFollowedApplications()),
    ('/applications/propose', app_views.ApplicationProposalForm()),
    ('/articles', article_views.ArticlesView()),
    ('/articles/{id:int}', article_views.ArticleView()),
    ('/articles/{id:int}/datasets', article_views.ArticleDatasetsView()),
    ('/articles/{id:int}/follow', following_views.FollowArticle()),
    ('/articles/followed', following_views.ListOfFollowedArticles()),
    ('/institutions', org_views.InstitutionsView()),
    ('/institutions/{id:int}', org_views.InstitutionView()),
    ('/institutions/{id:int}/datasets', org_views.InstitutionDatasetsView()),
    ('/datasets', dataset_views.DatasetsView()),
    ('/datasets/{id:int}', dataset_views.DatasetView()),
    ('/datasets/{id:int}/resources', dataset_views.DatasetResourcesView()),
    ('/datasets/{id:int}/resources/{resource_id:int}', dataset_views.DatasetResourceView()),
    ('/datasets/{id:int}/follow', following_views.FollowDataset()),
    ('/datasets/followed', following_views.ListOfFollowedDatasets()),
    ('/datasets/{id:int}/reportcomment', dataset_views.ReportCommentsView()),
    ('/resources/', res_views.ResourcesView()),
    ('/resources/{id:int}', res_views.ResourceView()),
    ('/resources/{id:int}/data', res_views.ResourceDataView()),
    ('/resources/{id:int}/incr_download_count', res_views.ResourceDownloadCounter()),
    ('/histories/', history_views.HistoriesView()),
    ('/histories/{id:int}', history_views.HistoryView()),
    ('/searchhistories/', searchhistory_views.SearchHistoriesView()),

    # Package
    # ('/packages', PackageListResource()),
    # ('/packages/{package_id:uuid}', PackageResource()),
    # ('/groups', GroupListResource()),
    # ('/groups/{group_id:uuid}', GroupResource()),

    # ('/api/action/package_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/package_search', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/package_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/package_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/package_patch', PingResource(), {'PATCH': 'get_pong'}),
    # ('/api/action/package_delete', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/package_autocomplete', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/current_package_list_with_resources', PingResource),
    # ('/api/action/package_create_default_resource_view', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/package_resource_reorder', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/package_owner_org_update', PingResource(), {'UPDATE': 'get_pong'}),
    #
    # # Package revision
    # ('/api/action/package_revision_list', PingResource),
    #
    # # Package activity
    # ('/api/action/package_activity_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/recently_changed_packages_activity_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/package_activity_list_html', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/recently_changed_packages_activity_list_html', PingResource(), {'GET': 'get_pong'}),
    #
    # # Package relationships
    # ('/api/action/package_relationships_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/package_relationship_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/package_relationship_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/package_relationship_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # # Group
    # ('/api/action/group_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_list_authz', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_revision_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_package_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_activity_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_activity_list_html', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_follower_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_follower_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_followee_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_followee_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/group_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/group_delete', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/group_member_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/group_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/group_patch', PingResource(), {'PATCH': 'get_pong'}),
    # ('/api/action/group_purge', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/group_member_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # # Organization
    # ('/api/action/organization_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_list_for_user', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_revision_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_activity_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_activity_list_htmk', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_follower_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_follower_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_followee_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/organization_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/organization_member_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/organization_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/organization_patch', PingResource(), {'PATCH': 'get_pong'}),
    # ('/api/action/organization_delete', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/organization_purge', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/organization_member_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # # Resource
    # ('/api/action/resource_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/resource_view_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/resource_view_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/resource_status_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/resource_search', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/resource_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/resource_view_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/resource_create_default_resource_view', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/resource_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/resource_view_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/resource_view_reorder', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/resource_patch', PingResource(), {'PATCH': 'get_pong'}),
    # ('/api/action/resource_delete', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/resource_view_delete', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/resource_view_clear', PingResource(), {'DELETE': 'get_pong'}),
    #
    # # User
    # ('/api/action/user_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_autocomplete', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_activity_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_activity_list_html', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_follower_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_follower_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_followee_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_followee_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/user_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/user_invite', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/user_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/user_generate_apikey', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/user_role_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/user_role_bulk_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/user_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/am_following_user', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/am_following_dataset', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/am_following_group', PingResource(), {'GET': 'get_pong'}),
    #
    # ('/api/action/follow_user', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/follow_dataset', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/follow_group', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/unfollow_user', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/unfollow_dataset', PingResource(), {'DELETE': 'get_pong'}),
    # ('/api/action/unfollow_group', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/tag_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/tag_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/tag_search', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/tag_autocomplete', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/tag_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/tag_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/related_show', PingResource),
    # ('/api/action/related_list', PingResource),
    # ('/api/action/related_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/related_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/related_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/task_status_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/task_status_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/task_status_update_many', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/task_status_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/member_list', PingResource),
    # ('/api/action/member_roles_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/member_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/member_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/vocabulary_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/vocabulary_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/vocabulary_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/vocalulary_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/vocabulary_delete', PingResource(), {'DELETE': 'get_pong'}),
    #
    # ('/api/action/revision_list', PingResource),
    # ('/api/action/revision_show', PingResource(), {'GET': 'get_pong'}),
    #
    # ('/api/action/dataste_follower_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/dataset_follower_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/dataset_followee_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/dataset_followee_list', PingResource(), {'GET': 'get_pong'}),
    #
    # ('/api/action/dashboard_activity_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/dashboard_activity_list_html', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/dashboard_new_activities_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/dashboard_mark_activities_old', PingResource(), {'UPDATE': 'get_pong'}),
    #
    # ('/api/action/bulk_update_private', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/bulk_update_public', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/bulk_update_delete', PingResource(), {'UPDATE': 'get_pong'}),
    #
    # ('/api/action/followee_count', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/followee_list', PingResource(), {'GET': 'get_pong'}),
    #
    # ('/api/action/site_read', PingResource),
    # ('/api/action/get_site_user', PingResource(), {'GET': 'get_pong'}),
    #
    # ('/api/action/term_translation_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/term_translation_update', PingResource(), {'UPDATE': 'get_pong'}),
    # ('/api/action/term_translation_update_many', PingResource(), {'UPDATE': 'get_pong'}),
    #
    # ('/api/action/activity_detail_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/activity_create', PingResource(), {'CREATE': 'get_pong'}),
    #
    # ('/api/action/license_list', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/roles_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/status_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/help_show', PingResource(), {'GET': 'get_pong'}),
    # ('/api/action/rating_create', PingResource(), {'CREATE': 'get_pong'}),
    # ('/api/action/send_email_notification', PingResource(), {'UPDATE': 'get_pong'}),

]
