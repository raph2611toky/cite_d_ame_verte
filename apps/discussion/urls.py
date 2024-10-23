from django.urls import path
from apps.discussion.views import (
    PlanningFamilialeListView,
    PlanningFamilialeFilterView,
    PlanningFamilialeNewView,
    PlanningFamilialeDeleteView,
    DiscussionListView,
    DiscussionFilterView,
    DiscussionNewView,
    DiscussionDeleteView,
    MessageNewView,
    FindOneDiscussionView
)

urlpatterns = [
    path('planning_familiale/', PlanningFamilialeListView.as_view(), name='planning_familiale_list'),
    path('planning_familiale/filter/', PlanningFamilialeFilterView.as_view(), name='planning_familiale_filter'),
    path('planning_familiale/new/', PlanningFamilialeNewView.as_view(), name='planning_familiale_new'),
    path('planning_familiale/delete/<int:pk>/', PlanningFamilialeDeleteView.as_view(), name='planning_familiale_delete'),
    
    path('discussions/', DiscussionListView.as_view(), name='discussion_list'),
    path('discussions/filter/', DiscussionFilterView.as_view(), name='discussion_filter'),
    path('discussions/new/', DiscussionNewView.as_view(), name='discussion_new'),
    path('discussions/delete/<int:pk>/', DiscussionDeleteView.as_view(), name='discussion_delete'),
    
    path('messages/new/', MessageNewView.as_view(), name='message_new'),
    path('discussions/<int:pk>/', FindOneDiscussionView.as_view(), name='find_one_discussion'),
]
