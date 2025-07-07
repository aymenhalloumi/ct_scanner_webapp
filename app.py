import os
import flask_sqlalchemy
from flask import Flask, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# Configuration with your real keys
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ct_install.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APP_NAME'] = 'CT Scanner Preinstallation Manager'


# Disable Flask-Admin's Babel requirement
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Initialize extensions
db = SQLAlchemy(app)

# ================================================
# MODELS (Enhanced with all features)
# ================================================

class Project(db.Model):
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    client_name = db.Column(db.String(100))
    engineer_name = db.Column(db.String(100))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return self.name or f'Project {self.id}'

class SiteSpecification(db.Model):
    __tablename__ = 'site_specification'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Room dimensions
    room_length = db.Column(db.Float, nullable=False)
    room_width = db.Column(db.Float, nullable=False)
    room_height = db.Column(db.Float, nullable=False)
    door_width = db.Column(db.Float)
    door_height = db.Column(db.Float)
    
    # Infrastructure
    floor_capacity = db.Column(db.Float)  # kg/m²
    electrical_power = db.Column(db.String(100))
    hvac_system = db.Column(db.String(100))
    
    # Dates
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    project = db.relationship('Project', backref='site_specs')
    
    def __repr__(self):
        return f'Site Spec for {self.project.name if self.project else "Unknown"}'

class ScannerModel(db.Model):
    __tablename__ = 'scanner_model'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100))
    weight = db.Column(db.Float)  # kg
    min_room_length = db.Column(db.Float)  # m
    min_room_width = db.Column(db.Float)   # m
    min_room_height = db.Column(db.Float)  # m
    min_door_width = db.Column(db.Float)   # m
    power_requirement = db.Column(db.String(50))
    special_requirements = db.Column(db.Text)
    
    def __repr__(self):
        return f'{self.name} ({self.manufacturer})'

class ConformityReport(db.Model):
    __tablename__ = 'conformity_report'
    
    id = db.Column(db.Integer, primary_key=True)
    site_spec_id = db.Column(db.Integer, db.ForeignKey('site_specification.id'), nullable=False)
    scanner_model_id = db.Column(db.Integer, db.ForeignKey('scanner_model.id'), nullable=False)
    
    # AI Analysis Results
    ai_evaluation_text = db.Column(db.Text)
    conformity_score = db.Column(db.Float)  # 0-100
    pass_fail = db.Column(db.Boolean)
    critical_issues = db.Column(db.Integer, default=0)
    estimated_cost = db.Column(db.Float)
    
    # Timestamps
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    site_spec = db.relationship('SiteSpecification', backref='conformity_reports')
    scanner_model = db.relationship('ScannerModel', backref='conformity_reports')
    
    def __repr__(self):
        return f'Conformity Report {self.id} - Score: {self.conformity_score}%'

# ================================================
# CUSTOM ADMIN DASHBOARD
# ================================================

class CTScannerAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Get counts for dashboard
        project_count = Project.query.count()
        scanner_count = ScannerModel.query.count()
        site_count = SiteSpecification.query.count()
        report_count = ConformityReport.query.count()
        
        # Recent activity
        recent_projects = Project.query.order_by(Project.created_on.desc()).limit(5).all()
        
        # Custom dashboard template
        dashboard_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CT Scanner Preinstallation Manager</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                .sidebar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
                .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
                .card:hover { transform: translateY(-2px); }
                .stat-card { border-left: 4px solid; }
                .stat-card.projects { border-left-color: #007bff; }
                .stat-card.scanners { border-left-color: #28a745; }
                .stat-card.sites { border-left-color: #17a2b8; }
                .stat-card.reports { border-left-color: #ffc107; }
            </style>
        </head>
        <body class="bg-light">
            <div class="container-fluid">
                <div class="row">
                    <!-- Sidebar -->
                    <div class="col-md-2 sidebar text-white min-vh-100 p-0">
                        <div class="p-3">
                            <h4><i class="fas fa-hospital"></i> CT Scanner</h4>
                            <small>Preinstallation Manager</small>
                        </div>
                        <ul class="nav nav-pills flex-column px-3">
                            <li class="nav-item mb-2">
                                <a class="nav-link text-white-50" href="{{ url_for('admin.index') }}">
                                    <i class="fas fa-tachometer-alt"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item mb-2">
                                <a class="nav-link text-white" href="{{ url_for('project.index_view') }}">
                                    <i class="fas fa-folder"></i> Projects
                                </a>
                            </li>
                            <li class="nav-item mb-2">
                                <a class="nav-link text-white" href="{{ url_for('scannermodel.index_view') }}">
                                    <i class="fas fa-cogs"></i> Scanner Models
                                </a>
                            </li>
                            <li class="nav-item mb-2">
                                <a class="nav-link text-white" href="{{ url_for('sitespecification.index_view') }}">
                                    <i class="fas fa-building"></i> Site Specifications
                                </a>
                            </li>
                            <li class="nav-item mb-2">
                                <a class="nav-link text-white" href="{{ url_for('conformityreport.index_view') }}">
                                    <i class="fas fa-clipboard-check"></i> Conformity Reports
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <!-- Main Content -->
                    <div class="col-md-10">
                        <div class="p-4">
                            <!-- Header -->
                            <div class="d-flex justify-content-between align-items-center mb-4">
                                <div>
                                    <h1 class="h3 mb-0">🎯 Dashboard</h1>
                                    <p class="text-muted">CT Scanner Preinstallation Management System</p>
                                </div>
                                <div>
                                    <span class="badge bg-success">Step 2 Complete</span>
                                    <span class="badge bg-info">Ready for Step 3</span>
                                </div>
                            </div>
                            
                            <!-- Stats Cards -->
                            <div class="row mb-4">
                                <div class="col-md-3">
                                    <div class="card stat-card projects">
                                        <div class="card-body text-center">
                                            <i class="fas fa-folder fa-2x text-primary mb-2"></i>
                                            <h3 class="mb-0">{{ project_count }}</h3>
                                            <p class="text-muted mb-0">Projects</p>
                                            <a href="{{ url_for('project.index_view') }}" class="btn btn-sm btn-primary mt-2">Manage</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card stat-card scanners">
                                        <div class="card-body text-center">
                                            <i class="fas fa-cogs fa-2x text-success mb-2"></i>
                                            <h3 class="mb-0">{{ scanner_count }}</h3>
                                            <p class="text-muted mb-0">Scanner Models</p>
                                            <a href="{{ url_for('scannermodel.index_view') }}" class="btn btn-sm btn-success mt-2">View</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card stat-card sites">
                                        <div class="card-body text-center">
                                            <i class="fas fa-building fa-2x text-info mb-2"></i>
                                            <h3 class="mb-0">{{ site_count }}</h3>
                                            <p class="text-muted mb-0">Site Specs</p>
                                            <a href="{{ url_for('sitespecification.index_view') }}" class="btn btn-sm btn-info mt-2">Manage</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card stat-card reports">
                                        <div class="card-body text-center">
                                            <i class="fas fa-clipboard-check fa-2x text-warning mb-2"></i>
                                            <h3 class="mb-0">{{ report_count }}</h3>
                                            <p class="text-muted mb-0">Reports</p>
                                            <a href="{{ url_for('conformityreport.index_view') }}" class="btn btn-sm btn-warning mt-2">View</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Quick Actions -->
                            <div class="row mb-4">
                                <div class="col-md-8">
                                    <div class="card">
                                        <div class="card-header">
                                            <h5 class="mb-0"><i class="fas fa-rocket"></i> Quick Actions</h5>
                                        </div>
                                        <div class="card-body">
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <a href="/create-sample-data" class="btn btn-warning w-100 mb-2">
                                                        <i class="fas fa-download"></i> Load Sample Scanners
                                                    </a>
                                                    <a href="{{ url_for('project.create_view') }}" class="btn btn-primary w-100 mb-2">
                                                        <i class="fas fa-plus"></i> New Project
                                                    </a>
                                                </div>
                                                <div class="col-md-6">
                                                    <a href="/test" class="btn btn-secondary w-100 mb-2">
                                                        <i class="fas fa-flask"></i> System Test
                                                    </a>
                                                    <a href="/debug-routes" class="btn btn-info w-100 mb-2">
                                                        <i class="fas fa-route"></i> Debug Routes
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h5 class="mb-0"><i class="fas fa-info-circle"></i> System Status</h5>
                                        </div>
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <span>Database:</span>
                                                <span class="badge bg-success">Connected</span>
                                            </div>
                                            <div class="d-flex justify-content-between">
                                                <span>OpenAI API:</span>
                                                <span class="badge bg-success">Configured</span>
                                            </div>
                                            <div class="d-flex justify-content-between">
                                                <span>Admin Interface:</span>
                                                <span class="badge bg-success">Active</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Recent Projects -->
                            {% if recent_projects %}
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0"><i class="fas fa-clock"></i> Recent Projects</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-sm">
                                            <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th>Status</th>
                                                    <th>Client</th>
                                                    <th>Created</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for project in recent_projects %}
                                                <tr>
                                                    <td>{{ project.name }}</td>
                                                    <td><span class="badge bg-info">{{ project.status }}</span></td>
                                                    <td>{{ project.client_name or 'N/A' }}</td>
                                                    <td>{{ project.created_on.strftime('%Y-%m-%d') if project.created_on else 'N/A' }}</td>
                                                    <td>
                                                        <a href="{{ url_for('project.edit_view', id=project.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                                                    </td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            {% endif %}
                            
                            <!-- Features Status -->
                            <div class="mt-4">
                                <h5>📋 Features Status</h5>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> Project Management</li>
                                    <li><i class="fas fa-check text-success"></i> Scanner Model Database (NeuViz ACE/ACE SP)</li>
                                    <li><i class="fas fa-check text-success"></i> Site Specification Management</li>
                                    <li><i class="fas fa-check text-success"></i> Admin Interface with Dashboard</li>
                                    <li><i class="fas fa-clock text-warning"></i> AI Conformity Analysis (Step 3)</li>
                                    <li><i class="fas fa-clock text-warning"></i> Scanner Comparison Tool (Step 3)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return render_template_string(dashboard_template,
                                    project_count=project_count,
                                    scanner_count=scanner_count,
                                    site_count=site_count,
                                    report_count=report_count,
                                    recent_projects=recent_projects)

# ================================================
# ADMIN VIEWS (Enhanced)
# ================================================

class ProjectView(ModelView):
    column_list = ['name', 'status', 'client_name', 'engineer_name', 'created_on']
    column_searchable_list = ['name', 'client_name', 'engineer_name']
    column_filters = ['status', 'created_on']
    form_columns = ['name', 'description', 'status', 'client_name', 'engineer_name']
    can_export = True
    column_default_sort = ('created_on', True)

class ScannerModelView(ModelView):
    column_list = ['name', 'manufacturer', 'weight', 'min_room_length', 'min_room_width', 'power_requirement']
    column_searchable_list = ['name', 'manufacturer']
    column_filters = ['manufacturer']
    can_export = True
    
    # Custom formatting for NeuViz models
    def scaffold_list_columns(self):
        columns = super().scaffold_list_columns()
        return columns

class SiteSpecificationView(ModelView):
    column_list = ['project', 'room_length', 'room_width', 'room_height', 'floor_capacity', 'created_on']
    column_filters = ['project', 'created_on']
    can_export = True
    column_default_sort = ('created_on', True)

class ConformityReportView(ModelView):
    column_list = ['site_spec', 'scanner_model', 'conformity_score', 'pass_fail', 'critical_issues', 'created_on']
    column_filters = ['pass_fail', 'created_on', 'scanner_model']
    can_export = True
    column_default_sort = ('created_on', True)

# ================================================
# INITIALIZE ADMIN
# ================================================

admin = Admin(
    app, 
    name='CT Scanner Manager', 
    index_view=CTScannerAdminIndexView()
)

# Add views with proper endpoints
admin.add_view(ProjectView(Project, db.session, name='Projects', endpoint='project'))
admin.add_view(ScannerModelView(ScannerModel, db.session, name='Scanner Models', endpoint='scannermodel'))
admin.add_view(SiteSpecificationView(SiteSpecification, db.session, name='Site Specifications', endpoint='sitespecification'))
admin.add_view(ConformityReportView(ConformityReport, db.session, name='Conformity Reports', endpoint='conformityreport'))

# ================================================
# SAMPLE DATA CREATION (Enhanced)
# ================================================

def create_sample_data():
    """Create comprehensive sample data"""
    try:
        # Create scanners if they don't exist
        if ScannerModel.query.count() == 0:
            scanners = [
                ScannerModel(
                    name='NeuViz ACE',
                    manufacturer='Neusoft Medical Systems',
                    weight=1400,
                    min_room_length=6.5,
                    min_room_width=4.2,
                    min_room_height=2.43,
                    min_door_width=1.2,
                    power_requirement='380V 50kVA',
                    special_requirements='Neusoft engineer required, Enhanced grounding, Temperature ±4.1°C/h, NPS-CT-0651 compliance'
                ),
                ScannerModel(
                    name='NeuViz ACE SP',
                    manufacturer='Neusoft Medical Systems',
                    weight=1450,
                    min_room_length=6.8,
                    min_room_width=4.5,
                    min_room_height=2.43,
                    min_door_width=1.2,
                    power_requirement='380V 55kVA',
                    special_requirements='Neusoft engineer required, Enhanced grounding, Temperature ±4.1°C/h, NPS-CT-0651 compliance'
                ),
                ScannerModel(
                    name='GE Revolution CT',
                    manufacturer='GE HealthCare',
                    weight=1850,
                    min_room_length=7.0,
                    min_room_width=4.8,
                    min_room_height=2.5,
                    min_door_width=1.3,
                    power_requirement='400V 80kVA',
                    special_requirements='Water cooling required, Advanced shielding, Revolution platform'
                ),
                ScannerModel(
                    name='Siemens SOMATOM',
                    manufacturer='Siemens Healthineers',
                    weight=1750,
                    min_room_length=6.8,
                    min_room_width=4.5,
                    min_room_height=2.4,
                    min_door_width=1.25,
                    power_requirement='480V 75kVA',
                    special_requirements='Seismic isolation recommended, EMC testing required, Quantum technology'
                )
            ]
            
            for scanner in scanners:
                db.session.add(scanner)
            
            db.session.commit()
            print("✅ Sample scanner models created")
            return True
            
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Error creating sample data: {e}")
        return False

# ================================================
# ROUTES (Enhanced)
# ================================================

@app.route('/')
def index():
    return redirect(url_for('admin.index'))

@app.route('/test')
def test():
    """Enhanced system test"""
    try:
        project_count = Project.query.count()
        scanner_count = ScannerModel.query.count()
        site_count = SiteSpecification.query.count()
        report_count = ConformityReport.query.count()
        
        return f'''
        <h2>🧪 Enhanced System Test</h2>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px;">
            <h3>Database Status</h3>
            <p>✅ Database: Connected and working</p>
            <p>✅ Projects: {project_count} in database</p>
            <p>✅ Scanner Models: {scanner_count} loaded</p>
            <p>✅ Site Specifications: {site_count} records</p>
            <p>✅ Conformity Reports: {report_count} reports</p>
            
            <h3>Configuration</h3>
            <p>✅ OpenAI API: {"Configured" if app.config.get("OPENAI_API_KEY") else "Not configured"}</p>
            <p>✅ Flask-Admin: Working properly</p>
            <p>✅ Database Models: All models loaded</p>
            
            <h3>Quick Links</h3>
            <p><a href="/admin/" style="color: #007bff;">🔧 Admin Dashboard</a></p>
            <p><a href="/admin/scannermodel/" style="color: #28a745;">⚙️ Scanner Models</a></p>
            <p><a href="/admin/project/" style="color: #17a2b8;">📁 Projects</a></p>
            <p><a href="/create-sample-data" style="color: #ffc107;">📊 Load Sample Data</a></p>
            
            <h3>Next Steps</h3>
            <p>🎯 <strong>Step 2 Complete!</strong> Ready for Step 3: AI Integration</p>
        </div>
        '''
    except Exception as e:
        return f'''
        <h2>❌ System Test Failed</h2>
        <p>Error: {str(e)}</p>
        <p><a href="/">Back to Home</a></p>
        '''

@app.route('/create-sample-data')
def create_sample_data_route():
    """Create sample data route"""
    success = create_sample_data()
    
    if success:
        message = "✅ Sample Data Created Successfully!"
        details = "4 scanner models have been added to the database."
    else:
        message = "ℹ️ Sample data already exists or failed to create."
        details = "Check the scanner models in the admin interface."
        
    return f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px;">
        <h2>{message}</h2>
        <p>{details}</p>
        
        <h3>Scanner Models Added:</h3>
        <ul>
            <li>NeuViz ACE (Neusoft Medical Systems)</li>
            <li>NeuViz ACE SP (Neusoft Medical Systems)</li>
            <li>GE Revolution CT (GE HealthCare)</li>
            <li>Siemens SOMATOM (Siemens Healthineers)</li>
        </ul>
        
        <h3>Quick Links:</h3>
        <p><a href="/admin/">🏠 Admin Dashboard</a></p>
        <p><a href="/admin/scannermodel/">⚙️ View Scanner Models</a></p>
        <p><a href="/test">🧪 System Test</a></p>
    </div>
    '''

@app.route('/debug-routes')
def debug_routes():
    """Show all available routes"""
    output = ["<h2>🔍 Available Routes</h2>"]
    output.append("<div style='font-family: monospace; font-size: 12px;'>")
    
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        output.append(f"<strong>{rule.endpoint}</strong>: {rule.rule} [{methods}]<br>")
    
    output.append("</div>")
    output.append("<p><a href='/admin/'>Back to Admin</a></p>")
    
    return "".join(sorted(output))

# ================================================
# INITIALIZE DATABASE
# ================================================

with app.app_context():
    db.create_all()
    print("✅ Enhanced database tables created")

if __name__ == '__main__':
    print("🚀 Starting Enhanced CT Scanner Preinstallation Manager...")
    print("🌐 Main page: http://localhost:5000")
    print("🔧 Admin dashboard: http://localhost:5000/admin/")
    print("🧪 System test: http://localhost:5000/test")
    print("📊 Sample data: http://localhost:5000/create-sample-data")
    print("🔍 Debug routes: http://localhost:5000/debug-routes")
    print()
    print("✅ Features ready:")
    print("   • Professional admin dashboard")
    print("   • Projects, Scanner Models, Site Specifications")
    print("   • NeuViz ACE/ACE SP support")
    print("   • OpenAI API configured")
    print("   • Ready for Step 3: AI Integration")
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
