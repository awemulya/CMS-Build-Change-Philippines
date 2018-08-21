import os
import zipfile
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, FormView, ListView
from django.shortcuts import reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.utils import json

from survey.settings import BASE_DIR
from userrole.forms import UserProfileForm
from userrole.models import UserRole
from .models import Project, Site, Category, Material, Step, Report, SiteMaterials, SiteDocument, Checklist
from .forms import ProjectForm, CategoryForm, MaterialForm, SiteForm, SiteMaterialsForm, SiteDocumentForm, \
    UserCreateForm
from .rolemixins import ProjectRoleMixin, SiteRoleMixin, CategoryRoleMixin, ProjectGuidelineRoleMixin, \
    SiteGuidelineRoleMixin, DocumentRoleMixin, ReportRoleMixin
from django.core import serializers


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def token(request):

    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.get(username=username)
        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            project_id, role = user.user_roles.values_list('project_id', 'group__name')[0]
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'project': project_id,
                'group': role
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                 'error': 'Bad password',
                 'msg': 'Invalid Password',
                'data': request.POST
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'error': str(e),
            'msg': 'Invalid Username and Password',
            'data': request.POST
        }, status=status.HTTP_400_BAD_REQUEST)


def project_material_photos(request, project_id):

    response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(response, 'w')
    material_photos = Material.objects.filter(project_id=project_id)
    project = get_object_or_404(Project, id=project_id)

    for filename in material_photos:
        if filename.good_photo:
            zip_file.write(os.path.join(BASE_DIR) + filename.good_photo.url, arcname=filename.good_photo.url)
        if filename.bad_photo:
            zip_file.write(os.path.join(BASE_DIR) + filename.bad_photo.url, arcname=filename.bad_photo.url)

    response['Content-Disposition'] = 'attachment; filename={}MaterialPhotos.zip'.format(project.name)
    return response


def site_documents_zip(request, site_id):

    response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(response, 'w')
    site_documents = SiteDocument.objects.filter(site=site_id)
    site = get_object_or_404(Site, id=site_id)

    for filename in site_documents:
        if filename.file:
            zip_file.write(os.path.join(BASE_DIR) + filename.file.url, arcname=filename.file.url)

    response['Content-Disposition'] = 'attachment; filename={}Documents.zip'.format(site.name)
    return response


class SuperAdminMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.group.name == "Super Admin":
                return super(SuperAdminMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


class ManagerSuperAdminMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            if request.group.name == "Super Admin" or request.group.name == "Project Manager":
                return super(ManagerSuperAdminMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied


class ProjectMixin(object):
    model = Project
    form_class = ProjectForm
    context_object_name = 'projects'

    def get_success_url(self):
        if self.request.group.name == "Project Manager":
            project_id = Project.objects.get(project_roles__user=self.request.user).pk
            return reverse('core:project_dashboard', kwargs={'project_id': project_id})
        elif self.request.group.name == "Super Admin":
            return reverse('core:admin_dashboard')


class ProjectCreateView(SuperAdminMixin, ProjectMixin, CreateView):
    """
    Project CreateView
    """
    template_name = "core/project_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.group.name == "Super Admin":
            context['projects'] = Project.objects.all()
            return context
        elif self.request.group.name == "Project Manager":
            context['project'] = Project.objects.get(project_roles__user=self.request.user)
            return context


class ProjectDetailView(SuperAdminMixin, ProjectMixin, DetailView):
    """
    Project DetailView
    """
    template_name = "core/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        context['materials_list'] = Project.objects.filter(pk=self.kwargs['pk'])\
                                .prefetch_related('material')\
                                .values_list('material__id','material__title', 'material__category',\
                                             'material__category__name',\
                                             'material__good_photo', 'material__bad_photo')
        context['if_material'] = Material.objects.filter(project=self.kwargs['pk']).count()
        context['category_list'] = Project.objects.filter(pk=self.kwargs['pk'])\
                                .prefetch_related('category')\
                                .values_list('category', 'category__name')
        context['if_category'] = Category.objects.filter(project=self.kwargs['pk']).count()
        return context


class ProjectUpdateView(ProjectMixin, ProjectRoleMixin, UpdateView):
    """
    Project UpdateView
    """
    template_name = "core/project_form.html"
    model = Project
    context_object_name = 'project'


class ProjectDeleteView(SuperAdminMixin, ProjectMixin, DeleteView):
    """
    Project DeleteView
    """
    template_name = "core/project_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.group.name == "Super Admin":
            context['projects'] = Project.objects.all()
            return context
        elif self.request.group.name == "Project Manager":
            context['project'] = Project.objects.get(project_roles__user=self.request.user)
            return context


class UserCreateView(SuperAdminMixin, CreateView):
    """
    User SignUp form
    """
    form_class = UserProfileForm
    template_name = 'registration/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['users'] = User.objects.all()
        return context

    def get_success_url(self):
        return reverse('core:admin_dashboard')


class UserListView(SuperAdminMixin, ListView):
    model = User
    template_name = 'registration/user_list.html'
    context_object_name = "users"


class ProjectDashboard(ProjectRoleMixin, TemplateView):
    """
    dashboard for Project Manager
    """

    template_name = "core/project_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['materials_list'] = Material.objects.filter(project=self.kwargs['project_id'])
        context['users'] = User.objects.filter(user_roles__project__id=self.kwargs['project_id'],\
                                               user_roles__group__name__exact="Project Manager")[:5]
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_id'])
        context['category_list'] = Category.objects.filter(project=self.kwargs['project_id'])
        context['total_reports'] = Report.objects.filter(checklist__step__site__project__id=self.kwargs['project_id']).count()
        context['assigned_manager'] = User.objects.filter(user_roles__project=self.kwargs['project_id']).first()
        site_geojson = Site.objects.filter(\
            project__id=self.kwargs['project_id']).exclude(location__isnull=True)
        if site_geojson.exists():
            context['locations'] = serializers.serialize('geojson', site_geojson, fields=('location'))
        else:
            context['locations'] =  [[]]
        site_address = Site.objects.exclude(location__isnull=True).filter(project__id=self.kwargs['project_id']).values_list('address', flat=True)
        json_site_address = json.dumps(list(site_address))
        context['site_address'] = json_site_address
        site_latlong_object = Site.objects.exclude(location__isnull=True).filter(project__id=self.kwargs['project_id']).values_list('location', flat=True)
        context['site_latlong'] = json.dumps([[l.x, l.y] for l in site_latlong_object])
        context['recent_activities_report'] = Report.objects.select_related('user', 'checklist__step__site').order_by('-date')[:5]
        if self.request.group.name == "Super Admin":
            context['projects'] = Project.objects.all()
            return context
        return context


class RecentUpdates(ProjectRoleMixin, TemplateView):
    """
    Recent Updates
    """

    template_name = "core/recent_updates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.kwargs['project_id']
        context['recent_activities_report'] = Report.objects.select_related('user', 'checklist__step__site').order_by('-date')
        return context


class Dashboard(SuperAdminMixin, TemplateView):
    """
    dashboard for Super Admin
    """
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['total_projects'] = Project.objects.all().count()
        context['users'] = User.objects.all()[:20]
        context['total_project_managers'] = User.objects.filter(user_roles__group__name='Project Manager').count()
        return context


class SiteCreateView(SiteRoleMixin, CreateView):
    """
    Site Create Form
    """

    template_name = "core/site_create.html"
    model = Site
    form_class = SiteForm

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url

        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url


class SiteListView(ManagerSuperAdminMixin, ListView):
    """
    Site List View
    """

    template_name = "core/site_list.html"
    model = Site
    paginate_by = 100


class SiteDetailView(SiteRoleMixin, DetailView):
    """
    Site Detail View
    """
    template_name = "core/site_detail.html"
    model = Site
    context_object_name = 'site'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step_list'] = Step.objects.filter(site=self.kwargs['pk'])[:10]
        context['site_materials'] = SiteMaterials.objects.filter(site=self.kwargs['pk'])[:5]
        context['site_reports'] = Report.objects.filter(checklist__step__site=self.kwargs['pk'])[:10]
        context['project'] = Project.objects.get(sites=self.kwargs['pk'])
        context['site_engineers'] = UserRole.objects.filter(site__id=self.kwargs['pk'], group__name='Field Engineer')\
                                    .values_list('user__username', flat=True)
        context['site_documents'] = SiteDocument.objects.filter(site__id=self.kwargs['pk'])[:6]
        context['site_pictures'] = Report.objects.filter(checklist__step__site__id=self.kwargs['pk']).values_list('photo')
        checklist_status_true_count = Checklist.objects.filter(step__site__id=self.kwargs['pk'], status=True).count()
        total_site_checklist_count = Checklist.objects.filter(step__site__id=self.kwargs['pk']).count()
        if total_site_checklist_count:
            context['progress'] = round((checklist_status_true_count/total_site_checklist_count)*100)
        else:
            context['progress'] = 0
        return context


class SiteDetailTemplateView(TemplateView):

    template_name = 'core/site_detail_js.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = Project.objects.get(sites=self.kwargs['site_pk'])
        context['site_id'] = self.kwargs['site_pk']
        context['site'] = serializers.serialize('json', [Site.objects.get(id=self.kwargs['site_pk'])], ensure_ascii=False)[1:-1]
        context['document_url'] = reverse('core:document_list',  kwargs={'site_id': self.kwargs['site_pk']})
        context['add_user_url'] = reverse('userrole:project_user_create',  kwargs={'project_id': project.id})
        context['people_url'] = reverse('userrole:field_engineer_create',  kwargs={'site_id': self.kwargs['site_pk']})
        context['site_edit_url'] = reverse('core:site_update',  kwargs={'pk': self.kwargs['site_pk']})
        context['site_delete_url'] = reverse('core:site_delete',  kwargs={'pk': self.kwargs['site_pk']})

        return context


class SiteUpdateView(SiteRoleMixin, UpdateView):
    """
    Site Update View
    """
    template_name = "core/site_create.html"
    model = Site
    form_class = SiteForm

    def form_valid(self, form):
        form.instance.site = get_object_or_404(Site, pk=self.kwargs['pk'])
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(sites=self.kwargs['pk'])
        return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:site_detail', args=(self.object.pk,))
            return success_url

        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:site_detail', args=(self.object.pk,))
            return success_url


class SiteDeleteView(SiteRoleMixin, DeleteView):
    """
    Site Delete View
    """
    model = Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(sites=self.kwargs['pk'])

        return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url

        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:project_dashboard')
            return success_url


class SiteStepsView(ManagerSuperAdminMixin, TemplateView):
    """
    Site Steps View
    """
    template_name = "core/site_steps.html"
    # template_name = "_base.html"
    # template_name = "_dashboard.html"

    def get_context_data(self, **kwargs):
        data = super(SiteStepsView, self).get_context_data(**kwargs)
        if data['is_project'] == 0:
            project = Site.objects.get(pk=data['pk']).project.id
            data['project'] = project
            data['site'] = Site.objects.select_related().get(id=self.kwargs['pk'])
            if self.request.user.is_superuser:
                data['dashboard_url'] = reverse('core:admin_dashboard')
            else:
                data['dashboard_url'] = reverse('core:project_dashboard',  kwargs={'project_id': project})
        else:
            data['project'] = data['pk']
            if self.request.user.is_superuser:
                data['dashboard_url'] = reverse('core:admin_dashboard')
            else:
                data['dashboard_url'] = reverse('core:project_dashboard',  kwargs={'project_id': data['pk']})
        return data


class CategoryFormView(CategoryRoleMixin, FormView):
    """
    Category Form View
    """
    template_name = "core/category_create.html"
    form_class = CategoryForm
    model = Category

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.save()
        return super(). form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])

        return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:project_dashboard', args=(self.kwargs['project_id'],))
            return success_url
        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:project_dashboard', args=(self.kwargs['project_id'],))
            return success_url


class CategoryListView(CategoryRoleMixin, ListView):
    """
    Category ListView
    """
    template_name = "core/category_list.html"
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        context['category_list'] = Category.objects.filter(project=self.kwargs['project_id'])

        return context


class CategoryUpdateView(CategoryRoleMixin, UpdateView):
    """
    Category UpdateView
    """
    template_name = "core/category_create.html"
    form_class = CategoryForm
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_roles.filter(group__name="Super Admin"):
            context['projects'] = Project.objects.all()
            return context
        elif self.request.user.user_roles.filter(group__name="Project Manager"):
            context['project'] = Project.objects.get(project_roles__user=self.request.user)
            # context['project_id'] = self.kwargs['project_id']
            return context

    def get_success_url(self):
        if self.request.user.user_roles.filter(group__name="Super Admin"):
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url
        elif self.request.user.user_roles.filter(group__name="Project Manager"):
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url


class CategoryDeleteView(CategoryRoleMixin, DeleteView):
    """
    Category DeleteView
    """
    model = Category
    template_name = "core/category_confirm_delete.html"

    def get_success_url(self):
        if self.request.user.user_roles.filter(group__name="Super Admin"):
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url

        elif self.request.user.user_roles.filter(group__name="Project Manager"):
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url


class MaterialFormView(ProjectGuidelineRoleMixin, FormView):
    """
    Material From View
    """
    template_name = "core/material_form.html"
    form_class = MaterialForm

    def get_form(self, form_class=None):
        form = super(MaterialFormView, self).get_form(form_class=self.form_class)
        form.fields['category'].queryset = form.fields['category'].queryset.filter(project=self.kwargs['project_id'])
        return form

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.created_by = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:project_dashboard', args=(self.kwargs['project_id'],))
            return success_url
        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:project_dashboard', args=(self.kwargs['project_id'],))
            return success_url


class MaterialUpdateView(ProjectGuidelineRoleMixin, UpdateView):
    """
    Category UpdateView
    """
    template_name = "core/material_form.html"
    form_class = MaterialForm
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_roles.filter(group__name="Super Admin"):
            context['projects'] = Project.objects.all()
            return context
        elif self.request.user.user_roles.filter(group__name="Project Manager"):
            context['project'] = Project.objects.get(project_roles__user=self.request.user)
            # context['project_id'] = self.kwargs['project_id']
            return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url
        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url


class MaterialDeleteView(ProjectGuidelineRoleMixin, DeleteView):
    """
    Category DeleteView
    """
    model = Material
    template_name = "core/material_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(material=self.kwargs['pk'])
        return context

    def get_success_url(self):
        if self.request.group.name == "Super Admin":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url

        elif self.request.group.name == "Project Manager":
            success_url = reverse_lazy('core:project_dashboard', args=(self.object.project.pk,))
            return success_url


class MaterialDetailView(ProjectGuidelineRoleMixin, DetailView):
    """
    Category UpdateView
    """
    template_name = "core/material_detail.html"
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(material=self.kwargs['pk'])

        return context


class MaterialListView(ManagerSuperAdminMixin, ListView):
    """
    Category UpdateView
    """
    template_name = "core/material_list.html"
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_roles.filter(group__name="Super Admin"):
            context['projects'] = Project.objects.all()
            context['project'] = Project.objects.get(pk=self.kwargs['pk'])
            context['materials_list'] = Material.objects.filter(project=self.kwargs['pk'])
            context['if_material'] = Material.objects.filter(project=self.kwargs['pk']).count()
            return context
        elif self.request.user.user_roles.filter(group__name="Project Manager"):
            context['project'] = Project.objects.get(project_roles__user=self.request.user)
            context['materials_list'] = Material.objects.filter(project__project_roles__user=self.request.user)
            context['project_id'] = self.kwargs['pk']
            return context

        else:
            raise PermissionDenied


class SiteMaterialFormView(SiteGuidelineRoleMixin, CreateView):
    model = SiteMaterials
    form_class = SiteMaterialsForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class=self.form_class)
        form.fields['materials'].queryset = form.fields['materials'].queryset.filter(project__sites=self.kwargs['site_id'])\
                                            .distinct()
        return form

    def form_valid(self, form):
        form.instance.site = get_object_or_404(Site, pk=self.kwargs['site_id'])
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('core:site_detail', args=(self.object.site.pk,))
        return success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(sites=self.kwargs['site_id'])
        return context


class SiteMaterialListView(SiteGuidelineRoleMixin, ListView):
    model = SiteMaterials
    form_class = SiteMaterialsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_materials'] = SiteMaterials.objects.filter(site=self.kwargs['site_id'])
        context['site'] = Site.objects.get(id=self.kwargs['site_id'])

        return context


class SiteMaterialDetailView(SiteGuidelineRoleMixin, DetailView):
    model = SiteMaterials
    form_class = SiteMaterialsForm
    context_object_name = 'site_material'


class SiteMaterialDeleteView(SiteGuidelineRoleMixin, DeleteView):
    model = SiteMaterials
    form_class = SiteMaterialsForm

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        materials = self.object.materials.all()
        site = Site.objects.get(site_site_materials=self.model.pk)
        sitematerials = SiteMaterials.objects.filter(site=site)
        sitematerials_list=[]
        [sitematerials_list.append(sm.materials.all()) for sm in sitematerials]
        print(sitematerials_list)
        import ipdb
        ipdb.set_trace()
        success_url = reverse_lazy('core:site_material_list', args=(self.object.site.pk,))
        self.object.materials.remove(materials)
        return HttpResponseRedirect(success_url)


class ReportListView(ReportRoleMixin, ListView):
    """
    Report List
    """
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = Report.objects.filter(checklist__step__site=self.kwargs['site_pk'])
        context['site'] = Site.objects.get(id=self.kwargs['site_pk'])
        context['project'] = Project.objects.get(sites=self.kwargs['site_pk'])
        return context


class ReportDetailView(ReportRoleMixin, DetailView):
    """
    Report detail
    """
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = Site.objects.get(steps__checklist_steps__checklist_report=self.kwargs['pk'])
        return context


class UserProfileView(CreateView):
    
    template_name = "core/user_profile.html"
    model = User
    form_class = UserCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(pk=self.kwargs['pk'])
        if self.request.user.user_roles.filter(group__name="Project Manager"):
            context['project_id'] = Project.objects.get(project_roles__user=self.request.user).pk
            return context
        return context
        

class SiteDocumentFormView(DocumentRoleMixin, FormView):
    """
    Site Document Form
    """
    form_class = SiteDocumentForm
    template_name = 'core/sitedocument_form.html'

    def post(self, request, *args, **kwargs):
        site = get_object_or_404(Site, pk=self.kwargs['site_id'])

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file')
        doc = request.POST.get('document_name')
        if form.is_valid():
            for file in files:
                SiteDocument.objects.create(file=file, site=site, document_name=doc)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)
        context['site'] = Site.objects.get(id=self.kwargs['site_id'])
        context['project'] = Project.objects.get(sites=self.kwargs['site_id'])
        return context

    def get_success_url(self):
        success_url = reverse_lazy('core:document_list', args=(self.kwargs['site_id'],))
        return success_url


class SiteDocumentListView(DocumentRoleMixin, ListView):
    """
        List of Site Documents
    """
    model = SiteDocument
    template_name = "core/sitedocument_list.html"
    form_class = SiteDocumentForm
    context_object_name = 'documents'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        return SiteDocument.objects.filter(site=self.kwargs['site_id'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = Site.objects.get(id=self.kwargs['site_id'])
        context['project'] = Project.objects.get(sites=self.kwargs['site_id'])
        return context


class SiteDocumentDeleteView(DocumentRoleMixin, DeleteView):
    """
        Delete Site Document
    """
    model = SiteDocument
    form_class = SiteDocumentForm

    def get_success_url(self):
        success_url = reverse_lazy('core:document_list', args=(self.object.site.id,))
        return success_url

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)
        context['site'] = Site.objects.get(site_document=self.kwargs['pk'])
        context['project'] = Project.objects.get(sites__site_document=self.kwargs['pk'])
        return context

    
class UserProfileUpdateView(UpdateView):
    """
    User Profile Update View
    """

    template_name = "core/user_profile.html"
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy("home")

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)
        if not self.request.group.name == 'Super Admin':
            context['project_id'] = self.request.project.pk
        return context


class UserProfileDetailView(DetailView):
    """
    User Profile detail view
    """
    template_name = "core/user_profile_detail.html"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(pk=self.kwargs['pk'])
        if self.request.user.user_roles.filter(group__name="Project Manager"):
            context['project'] = Project.objects.get(project_roles__user=self.request.user)
            return context
        return context
