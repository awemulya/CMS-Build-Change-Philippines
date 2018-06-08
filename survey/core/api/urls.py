from django.urls import path, include

from rest_framework import routers

from . import viewset
from .. import views

router = routers.DefaultRouter()

router.register(r'users', viewset.UserViewSet)
router.register(r'project', viewset.ProjectViewSet, base_name='project-list')
router.register(r'checklist', viewset.ChecklistViewset, base_name='checklist-api')
router.register(r'step', viewset.StepViewset, base_name='step-api')
router.register(r'material', viewset.MaterialViewset, base_name='material-api')
router.register(r'report', viewset.ReportViewset, base_name='checklist-report')


urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', views.token),
    path('list-steps/<int:is_project>/<int:pk>/',
         viewset.ProjectSiteStepsViewSet.as_view({'get':  'list'})),
    path('step-list/<int:site>/', viewset.StepViewset.as_view({'get': 'list',}), name="api_steps"),
    path('checklist-list/<int:step>/', viewset.ChecklistViewset.as_view({'get': 'list', }), name="api_checklist"),
    path('material-list/<int:project>/', viewset.MaterialViewset.as_view({'get': 'list', }), name="api_materials"),
    path('material-photos/', viewset.MaterialPhotosViewset.as_view({'get': 'list', }), name="materials_photos"),
    path('site-materials-list/<int:site>/', viewset.SiteMaterialViewSet.as_view({'get': 'list', }), name="api_site_materials"),
    path('site-report-list/<int:site>/', viewset.SiteReportViewSet.as_view({'get': 'list', }),
         name="api_site_report"),
    path('site-engineers/<int:site>/', viewset.SiteEngineerViewSet.as_view({'get': 'list', }),
         name="api_site_engineers"),
    path('site-documents/<int:site>/', viewset.SiteDocumentViewSet.as_view({'get': 'list', }), name="api_site_documents"),
    path('category-list/', viewset.CategoryViewSet.as_view({'get': 'list'})),

]