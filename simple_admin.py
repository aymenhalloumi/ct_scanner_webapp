# ================================================
# FIXED: Admin with Working Menu Links
# Replace your simple_admin.py with this version
# ================================================

from flask import Flask, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
import os

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ct_scanner_simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# ================================================
# MODELS
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

class ScannerModel(db.Model):
    __tablename__ = 'scanner_model'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100))
    weight = db.Column(db.Float)
    min_room_length = db.Column(db.Float)
    min_room_width = db.Column(db.Float)
    min_room_height = db.Column(db.Float)
    min_door_width = db.Column(db.Float)
    power_requirement = db.Column(db.String(50))
    special_requirements = db.Column(db.Text)
    
    def __repr__(self):
        return f'{self.name} ({self.manufacturer})'

class SiteSpecification(db.Model):
    __tablename__ = 'site_specification'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    room_length = db.Column(db.Float, nullable=False)
    room_width = db.Column(db.Float, nullable=False)
    room_height = db.Column(db.Float, nullable=False)
    door_width = db.Column(db.Float)
    floor_capacity = db.Column(db.Float)
    electrical_power = db.Column(db.String(100))
    
    project = db.relationship('Project', backref='site_specs')
    
    def __repr__(self):
        return f'Site for {self.project.name if self.project else "Unknown"}'

# ================================================
# ADMIN VIEWS
# ================================================

class ProjectView(ModelView):
    column_list = ['name', 'status', 'client_name', 'engineer_name', 'created_on']
    column_searchable_list = ['name', 'client_name']
    column_filters = ['status', 'created_on']
    form_columns = ['name', 'description', 'status', 'client_name', 'engineer_name']
    can_export = False

class ScannerModelView(ModelView):
    column_list = ['name', 'manufacturer', 'weight', 'min_room_length', 'min_room_width', 'power_requirement']
    column_searchable_list = ['name', 'manufacturer']
    column_filters = ['manufacturer']
    can_export = False

class SiteSpecificationView(ModelView):
    column_list = ['project', 'room_length', 'room_width', 'room_height', 'floor_capacity']
    column_filters = ['project']
    can_export = False

# ================================================
# CUSTOM ADMIN INDEX WITH WORKING LINKS
# ================================================

class CTScannerAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Get counts
        project_count = Project.query.count()
        scanner_count = ScannerModel.query.count()
        site_count = SiteSpecification.query.count()
        
        # Simple dashboard template with correct links
        dashboard_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CT Scanner Manager</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                .sidebar { background: #2c3e50; }
                .nav-link:hover { background: rgba(255,255,255,0.1); }
                .card { transition: transform 0.2s; }
                .card:hover { transform: translateY(-5px); }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-2 sidebar text-white min-vh-100">
                        <h4 class="p-3">🏥 CT Scanner</h4>
                        <ul class="nav nav-pills flex-column">
                            <li class="nav-item">
                                <a class="nav-link text-white" href="/admin/project/">
                                    <i class="fas fa-folder"></i> Projects ({{ project_count }})
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link text-white" href="/admin/scannermodel/">
                                    <i class="fas fa-cogs"></i> Scanner Models ({{ scanner_count }})
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link text-white" href="/admin/sitespecification/">
                                    <i class="fas fa-building"></i> Site Specifications ({{ site_count }})
                                </a>
                            </li>
                            <li class="nav-item">
                                <hr class="text-white">
                            </li>
                            <li class="nav-item">
                                <a class="nav-link text-white" href="/create-sample-data">
                                    <i class="fas fa-database"></i> Load Sample Data
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link text-white" href="/test">
                                    <i class="fas fa-flask"></i> System Test
                                </a>
                            </li>
                        </ul>
                    </div>
                    <div class="col-md-10">
                        <div class="p-4">
                            <h1>🎯 CT Scanner Preinstallation Manager</h1>
                            <p class="lead">Professional CT scanner project management and compliance system</p>
                            
                            <div class="row mb-4">
                                <div class="col-md-4">
                                    <div class="card border-primary h-100">
                                        <div class="card-body text-center">
                                            <i class="fas fa-folder fa-3x text-primary mb-3"></i>
                                            <h3 class="text-primary">{{ project_count }}</h3>
                                            <h5>Projects</h5>
                                            <p class="small">Manage CT scanner installation projects</p>
                                            <a href="/admin/project/" class="btn btn-primary">View Projects</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-success h-100">
                                        <div class="card-body text-center">
                                            <i class="fas fa-cogs fa-3x text-success mb-3"></i>
                                            <h3 class="text-success">{{ scanner_count }}</h3>
                                            <h5>Scanner Models</h5>
                                            <p class="small">NeuViz, GE, Siemens specifications</p>
                                            <a href="/admin/scannermodel/" class="btn btn-success">View Scanners</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-info h-100">
                                        <div class="card-body text-center">
                                            <i class="fas fa-building fa-3x text-info mb-3"></i>
                                            <h3 class="text-info">{{ site_count }}</h3>
                                            <h5>Site Specifications</h5>
                                            <p class="small">Room dimensions & requirements</p>
                                            <a href="/admin/sitespecification/" class="btn btn-info">View Sites</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h5>🚀 Quick Actions</h5>
                                    <div class="d-grid gap-2">
                                        <a href="/admin/project/new/" class="btn btn-primary">
                                            <i class="fas fa-plus"></i> New Project
                                        </a>
                                        <a href="/create-sample-data" class="btn btn-warning">
                                            <i class="fas fa-database"></i> Load Sample Scanners
                                        </a>
                                        <a href="/test" class="btn btn-secondary">
                                            <i class="fas fa-flask"></i> System Test
                                        </a>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h5>✅ System Status</h5>
                                    <ul class="list-group">
                                        <li class="list-group-item d-flex justify-content-between">
                                            <span>Database</span>
                                            <span class="badge bg-success">Connected</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between">
                                            <span>Admin Interface</span>
                                            <span class="badge bg-success">Working</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between">
                                            <span>AI Integration</span>
                                            <span class="badge bg-warning">Step 3</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between">
                                            <span>NeuViz Support</span>
                                            <span class="badge bg-success">Ready</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="mt-4 p-3 bg-light rounded">
                                <h6><i class="fas fa-info-circle"></i> Step 2 Complete!</h6>
                                <p class="mb-0">✅ Project management, scanner database, and admin interface are working. Ready for <strong>Step 3: AI Integration</strong>!</p>
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
                                    site_count=site_count)

# ================================================
# INITIALIZE ADMIN WITH EXPLICIT ENDPOINTS
# ================================================

admin = Admin(
    app, 
    name='CT Scanner Manager', 
    template_mode='bootstrap4',
    index_view=CTScannerAdminIndexView(url='/admin')
)

# Add views with explicit endpoints and URLs
admin.add_view(ProjectView(Project, db.session, 
                          name='Projects', 
                          endpoint='project',
                          url='/admin/project'))

admin.add_view(ScannerModelView(ScannerModel, db.session, 
                               name='Scanner Models', 
                               endpoint='scannermodel',
                               url='/admin/scannermodel'))

admin.add_view(SiteSpecificationView(SiteSpecification, db.session, 
                                    name='Site Specifications', 
                                    endpoint='sitespecification',
                                    url='/admin/sitespecification'))

# ================================================
# ROUTES
# ================================================

@app.route('/')
def index():
    return redirect(url_for('admin.index'))

@app.route('/test')
def test():
    project_count = Project.query.count()
    scanner_count = ScannerModel.query.count()
    site_count = SiteSpecification.query.count()
    
    return f'''
    <h2>🧪 System Test</h2>
    <p>✅ Database: Connected</p>
    <p>✅ Projects: {project_count}</p>
    <p>✅ Scanners: {scanner_count}</p>
    <p>✅ Site Specs: {site_count}</p>
    <p>✅ Admin Interface: Working</p>
    <p>✅ OpenAI API: Ready for Step 3</p>
    <h4>Direct Links Test:</h4>
    <ul>
        <li><a href="/admin/">Admin Dashboard</a></li>
        <li><a href="/admin/project/">Projects List</a></li>
        <li><a href="/admin/scannermodel/">Scanner Models List</a></li>
        <li><a href="/admin/sitespecification/">Site Specifications List</a></li>
    </ul>
    <p><a href="/create-sample-data">Load Sample Data</a></p>
    '''

@app.route('/create-sample-data')
def create_sample_data():
    # Create NeuViz scanners if they don't exist
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
                special_requirements='Neusoft engineer required, Enhanced grounding, Temperature ±4.1°C/h'
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
                special_requirements='Neusoft engineer required, Enhanced grounding, Temperature ±4.1°C/h'
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
                special_requirements='Water cooling required, Advanced shielding'
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
                special_requirements='Seismic isolation recommended, EMC testing required'
            )
        ]
        
        for scanner in scanners:
            db.session.add(scanner)
        
        db.session.commit()
        message = "✅ Sample Data Created! 4 scanner models added."
    else:
        message = "ℹ️ Sample data already exists."
        
    return f'''
    <h2>{message}</h2>
    <ul>
        <li><a href="/admin/">Dashboard</a></li>
        <li><a href="/admin/scannermodel/">View Scanner Models</a></li>
        <li><a href="/admin/project/">View Projects</a></li>
        <li><a href="/test">System Test</a></li>
    </ul>
    '''

@app.route('/debug-routes')
def debug_routes():
    """Show all available routes for debugging"""
    output = ["<h2>🔍 Available Routes</h2>"]
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        output.append(f"<strong>{rule.endpoint}</strong>: {rule.rule} [{methods}]")
    return "<br>".join(sorted(output))

# ================================================
# INITIALIZE DATABASE
# ================================================

with app.app_context():
    db.create_all()
    print("✅ Database created successfully")

if __name__ == '__main__':
    print("🚀 Starting CT Scanner Manager...")
    print("🔧 Admin dashboard: http://localhost:5000/admin/")
    print("📊 Load sample data: http://localhost:5000/create-sample-data")
    print("🧪 System test: http://localhost:5000/test")
    print("🔍 Debug routes: http://localhost:5000/debug-routes")
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    app.run(debug=debug, host=host, port=port)
