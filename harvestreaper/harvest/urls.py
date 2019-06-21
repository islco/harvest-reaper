from django.urls import path

from harvestreaper.harvest.views import (HarvestOAuthView, HarvestOAuthSuccessView,
                                         HarvestTimeSubmitView)

urlpatterns = [
    path('', HarvestOAuthView.as_view(), name='harvest_auth'),
    path('o-auth', HarvestOAuthSuccessView.as_view(), name='harvest_oauth_success'),

    path('submit-time', HarvestTimeSubmitView.as_view(), name='harvest_time_submit')
]
