from django.urls import path

from . import views

app_name = 'cpanel'
urlpatterns = [
    path('', views.index, name='index'), 
    path('gcam_view',	views.gcam_view,	name='gcam_view'),
    path('video_play',	views.video_play, 	name='video_play'),
    path('video_record',views.video_record, 	name='video_record'),
    path('setup',	views.setup, 		name='setup'),
    path('setup_update',views.setup_update, 	name='setup_update'),
    path('LED_control',	views.LED_control, 	name='LED_control'),
    path('acc_plot',	views.acc_plot, 	name='acc_plot'),

]
