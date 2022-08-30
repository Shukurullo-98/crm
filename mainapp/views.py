from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lead, Agent, Category
from django.views import generic
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, CategoryModelForm,LeadCategoryUpdateForm
from agents.mixins import OrganisorLoginRequeredMixinis
import datetime
import logging


class SignUpView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('login')


class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'


class LeadListView(OrganisorLoginRequeredMixinis, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=False
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
                agent__isnull=False
            )
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        return context


class LeadDetailView(OrganisorLoginRequeredMixinis, generic.DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user
        if user.is_agent:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
        queryset = queryset.filter(agent__user=user)
        return queryset


class LeadCreateView(OrganisorLoginRequeredMixinis, generic.CreateView):
    template_name = 'leads/lead_create.html'
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead_list")

    def form_valid(self, form):
        #TODO send mail
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="tbekamov@gmail.com",
            recipient_list=['sh.rakhmatovv@gmail.com']
        )
        return super(LeadCreateView, self).form_valid(form)


class LeadUpdateView(OrganisorLoginRequeredMixinis, generic.UpdateView):
    template_name = 'leads/lead_list.html'
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead_list")


class LeadDeleteView(OrganisorLoginRequeredMixinis, generic.DeleteView):
    template_name = 'leads/lead_delete.html'

    def get_queryset(self):
        user = self.request.user
        queryset = Lead.objects.filter(organisation=user.userprofile)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead_list")


class AssignAgentView(OrganisorLoginRequeredMixinis, generic.FormView):
    template_name = 'leads/assign_agent.html'
    form_class = AssignAgentForm

    def get_success_url(self):
        return reverse('leads:lead_list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        agent = form.cleaned_data['agent']
        lead = Lead.objects.get(id=self.kwargs['pk'])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
            )

        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryDetailView(OrganisorLoginRequeredMixinis, generic.DetailView):
    template_name = 'leads/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        leads = self.get_object().leads.all()
        context.update(
            {
                'leads': leads
            }
        )
        return leads

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
        return queryset


class CategoryUpdateView(OrganisorLoginRequeredMixinis, generic.UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})

    def form_valid(self, form):
        lead_before_update = self.get_object()
        instance = form.save(commit=False)
        converted_category = Category.objects.get(name="Converted")
        if form.cleaned_data["category"] == converted_category:
            # update the date at which this lead was converted
            if lead_before_update.category != converted_category:
                # this lead has now been converted
                instance.converted_date = datetime.datetime.now()
        instance.save()
        return super(LeadCategoryUpdateView, self).form_valid(form)
