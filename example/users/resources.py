# -*- coding: utf-8 -*-

from dagny import Resource, action
from dagny.renderer import Skip
from django.contrib.auth import forms, models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
import simplejson


class User(Resource):

    template_path_prefix = 'auth/'

    @action
    def index(self):
        self.users = models.User.objects.all()

    @index.render.json
    def index(self):
        return json_response([user_to_dict(user) for user in self.users])

    # Stub to test that skipping works.
    @index.render.xml
    def index(self):
        raise Skip

    @action
    def new(self):
        self.form = forms.UserCreationForm()

    @action
    def create(self):
        self.form = forms.UserCreationForm(self.request.POST)
        if self.form.is_valid():
            self.user = self.form.save()
            return redirect('User#show', str(self.user.id))

        return self.new.render(status=403)

    @action
    def show(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))

    @show.render.json
    def show(self):
        return json_response(user_to_dict(self.user))

    @action
    def edit(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
        self.form = forms.UserChangeForm(instance=self.user)

    @action
    def update(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
        self.form = forms.UserChangeForm(self.request.POST, instance=self.user)
        if self.form.is_valid():
            self.form.save()
            return redirect('User#show', str(self.user.id))

        return self.edit.render(status=403)

    @action
    def destroy(self, user_id):
        self.user = get_object_or_404(models.User, id=int(user_id))
        self.user.delete()
        return redirect('User#index')


# A stub resource for the routing tests.
class Account(Resource):

    template_path_prefix = 'auth/'

    @action
    @action.deco(login_required)
    def show(self):
        return

    @show.render.json
    def show(self):
        return json_response({'username': self.request.user.username})


def json_response(data):
    return HttpResponse(content=simplejson.dumps(data),
                        content_type='application/json')

def user_to_dict(user):
    return {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
