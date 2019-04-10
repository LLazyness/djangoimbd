import django
from django.shortcuts import render, redirect
from core.models import Movie, Person, Vote, MovieImage, UserMovieList
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from django.contrib.auth.mixins import (LoginRequiredMixin, )
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import VoteForm, MovieImageForm
from django.core.exceptions import (PermissionDenied)
from core.mixins import (VaryCacheOnCookieMixin)
from django.core.cache import cache
from django.http import HttpResponse
import json


# Create your views here.
class Movies(ListView):
    model = Movie

    def get_context_data(self, **kwargs):
        #create movie's list of current user
        user = User.objects.get(pk=self.request.user.id)
        user_related_movies = UserMovieList.objects.filter(user=user).select_related('movie')
        user_movies = []
        for i in user_related_movies:
            user_movies.append(i.movie)

        movie_list_ordered_by_four = []
        group_movie_list = []
        movies = Movie.object.all().exclude(title__contains = 'todo')
        counter = 0
        for i in movies:
            counter += 1
            group_movie_list.append(i)
            if len(group_movie_list) == 4:
                movie_list_ordered_by_four.append(group_movie_list)
                group_movie_list = []
            elif counter == len(movies):
                movie_list_ordered_by_four.append(group_movie_list)



        context = super().get_context_data(**kwargs)
        context['default_image'] = MovieImage.objects.get(pk=42)
        context['user_movies'] = user_movies
        context['movie_list_ordered_by_four'] = movie_list_ordered_by_four

        #context['user_movie_list'] =

        return context

    def get_queryset(self):
        queryset = super(Movies, self).get_queryset()
        queryset = Movie.object.filter()
        return queryset





def AddToWatchedList(request):
    if request.method == 'GET':

        data = request.GET
        user_id = data.get("user", "0")
        movie_id = data.get("movie", "0")

        user = User.objects.get(pk=user_id)
        movie = Movie.object.get(pk=movie_id)

        try:
            UserMovieList.objects.create(movie=movie, user=user).save()
            status = True
        except:
            status = False

        return HttpResponse(
            json.dumps({'status': status}),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"status": false}),
            content_type="application/json"
        )


class UserMovies(VaryCacheOnCookieMixin, ListView):
    model = UserMovieList
    template_name = 'core/user_movie_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image'] = MovieImage.objects.get(pk=42)
        return context

    def get_queryset(self):
        queryset = super(UserMovies, self).get_queryset()
        queryset = UserMovieList.objects.filter(user=self.request.user)
        return queryset


class TopMovies(ListView):
    template_name = 'core/top_movies_list.html'

    def get_queryset(self):
        limit = 10
        key = 'top_movies_%s' % limit
        cached_qs = cache.get(key)
        if cached_qs:
            same_django = cached_qs._django_version == django.get_version()
            if same_django:
                return cached_qs
        qs = Movie.object.top_movies(
            limit=limit
        )
        cache.set(key, qs)
        return qs


class MovieImageUpload(LoginRequiredMixin, CreateView):
    form_class = MovieImageForm

    # base function
    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user.id
        initial['movie'] = self.kwargs['movie_id']
        return initial

    # base function
    def render_to_response(self, context, **response_kwargs):
        movie_id = self.kwargs['movie_id']
        movie_details_url = reverse('core:MovieDetail', kwargs={'pk': movie_id})
        return redirect(to=movie_details_url)

    # base function
    def get_success_url(self):
        movie_id = self.kwargs['movie_id']
        movie_detail_url = reverse(
            'core:MovieDetail',
            kwargs={'pk': movie_id})
        return movie_detail_url


class MovieDetail(DetailView):
    queryset = (Movie.object.all_with_related_persons_and_score())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['image_form'] = self.movie_image_form()
        if self.request.user.is_authenticated:
            vote = Vote.objects.get_vote_or_unsaved_blank_vote(
                movie=self.object,
                user=self.request.user
            )
            if vote.id:
                vote_form_url = reverse(
                    'core:UpdateVote',
                    kwargs={
                        'movie_id': vote.movie.id,
                        'pk': vote.id})
            else:
                vote_form_url = (
                    reverse(
                        'core:CreateVote',
                        kwargs={
                            'movie_id': self.object.id}
                    )
                )
            vote_form = VoteForm(instance=vote)
            ctx['vote_form'] = vote_form
            ctx['vote_form_url'] = vote_form_url
        return ctx

    def movie_image_form(self):
        if self.request.user.is_authenticated:
            return MovieImageForm
        return None


class PersonDetail(DetailView):
    queryset = Person.objects.all_with_prefetch_movies()


class CreateVote(LoginRequiredMixin, CreateView):
    form_class = VoteForm

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user.id
        initial['movie'] = self.kwargs['movie_id']
        return initial

    def get_success_ur(self):
        movie_id = self.object.movie.id
        return reverse(
            'core:MovieDetail',
            kwargs={
                'pk': movie_id
            }
        )

    def render_to_response(self, context, **response_kwargs):
        movie_id = context['object'].id
        movie_detail_url = reverse(
            'core:MovieDetail',
            kwargs={'pk': movie_id}
        )
        return redirect(
            to=movie_detail_url
        )


class UpdateVote(LoginRequiredMixin, UpdateView):
    form_class = VoteForm
    queryset = Vote.objects.all()

    def get_object(self, queryset=None):
        vote = super().get_object(queryset)
        user = self.request.user
        if vote.user != user:
            raise PermissionDenied(
                'cannot change another '
                'user vote'
            )
        return vote

    def get_success_url(self):
        movie_id = self.object.movie.id
        return reverse(
            'core:MovieDetail',
            kwargs=({'pk': movie_id})
        )

    def render_to_response(self, context, **response_kwargs):
        movie_id = context['object'].id
        movie_detail_url = reverse(
            'core:MovieDetail',
            kwargs={'pk': movie_id}
        )
        return redirect(
            to=movie_detail_url
        )
