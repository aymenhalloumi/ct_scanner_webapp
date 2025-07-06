from flask import render_template, redirect, url_for
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi, BaseView, expose
from flask_appbuilder.security.decorators import has_access

from . import appbuilder, db
from .models import Project

"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)


    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

# ================================================
# CT Scanner Views
# ================================================

class CTScannerHomeView(BaseView):
    """Home page for CT Scanner application"""
    
    @expose('/')
    @has_access
    def home(self):
        """Home page"""
        return self.render_template(
            'ct_scanner_home.html',
            title="CT Scanner Preinstallation Manager"
        )

class ProjectView(BaseView):
    """Project management view"""
    
    @expose('/projects')
    @has_access
    def projects(self):
        """Projects list page"""
        return self.render_template(
            'projects.html',
            title="Projects"
        )

class SiteSpecificationView(BaseView):
    """Site specification view"""
    
    @expose('/site-specs')
    @has_access
    def site_specs(self):
        """Site specifications page"""
        return self.render_template(
            'site_specs.html',
            title="Site Specifications"
        )

class ProjectModelView(ModelView):
    datamodel = SQLAInterface(Project)
    list_columns = ['name', 'status']
    add_columns = ['name', 'description', 'status']
    edit_columns = ['name', 'description', 'status']
    show_columns = ['name', 'description', 'status']

# ================================================
# Register Views
# ================================================

appbuilder.add_view(
    CTScannerHomeView(),
    "Home",
    icon="fa-home",
    category="CT Scanner"
)

appbuilder.add_view(
    ProjectModelView(),
    "Projects",
    icon="fa-folder",
    category="CT Scanner"
)

appbuilder.add_view(
    SiteSpecificationView(),
    "Site Specifications",
    icon="fa-building",
    category="CT Scanner"
)

# ================================================
# Error Handlers
# ================================================

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )

db.create_all()
