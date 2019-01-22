import django.urls
from . import views
from django.urls import path

app_name = 'core'
urlpatterns = [
    path('movies',
         views.MovieList.as_view(),
         name='MovieList'),
    path('movies/top', views.TopMovies.as_view(), name='TopMovies'),
    path('movie/<int:pk>', views.MovieDetail.as_view(), name='MovieDetail'),
    path('movie/<int:movie_id>/vote', views.CreateVote.as_view(), name='CreateVote'),
    path('movie/<int:movie_id>/vote/<int:pk>', views.UpdateVote.as_view(), name='UpdateVote'),
    path('movie/<int:movie_id>/image/upload', views.MovieImageUpload.as_view(), name='MovieImageUpload')
]
