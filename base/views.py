from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from  django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from  django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task
#Mixins prevent the user from accessing some areas, if the user is to be
#restricted from accessing some sites. eg if allowed to see specific items
#using id and don't see anything else


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('task')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('task')
    #up to this point, the form has been created, but does nothng coz lacks reverse match ie
    #where to be  directed.
    #let's create a function to handle this error by writing a function to handle the registration
    #after this the user will be:-created, saved and redirected.
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    #This fuction here ensures to the user is redirected the above one not working
    #also helps in restricting the user if they are logged in, they cn log in again bt will be
    #directed to their logged in page.
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('task')
        return super(RegisterPage, self).get(*args, **kwargs)




class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    #this def ensures that every person logged in can only see their info! alone, not others.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()#no user 'coz it's filtered by user above.
        #above line filters all incomlete tasks and counts how many they are.

        #here you want to search if a task is availble in the task list
        search_input = self.request.GET.get('search-area') or ''#if this search_input is not empty
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)
        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'



class TaskCreate(LoginRequiredMixin, CreateView):#here all the task shld have all model fields.
    model = Task#template with name task_form will be used defaultly
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('task')

    #here create a method where when adding a task, it will strickly be to person logged in.
    #ie request.user, the method already exist but we can overide it. without db user showing up who is
    #adding
    #to complete this edit the fields by putting the fields u want ['title', 'description', 'complete']
    #same case to taskupdate below
    def form_valid(self, request, form_class):
        if request.method == 'POST':
            form_class = UserCreationForm('request.POST')
            if form_class.is_valid(isinstance=form_class):
                form_class.save(form_class)
                reverse_lazy('task')
            return redirect("task-create")
        else:
            form_class.instance.user = self.request.user
            return super(TaskCreate, self).form_valid(form_class)


class TaskUpdate(LoginRequiredMixin, UpdateView):#this class updates the task to be done
    model = Task
    fields = ['title', 'description', 'complete',]
    success_url = reverse_lazy('task')#returns an object and landing at task


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name ='task'
    success_url = reverse_lazy('task')
