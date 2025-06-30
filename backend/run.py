# # backend/run.py
# #!/usr/bin/env python3
# """
# Network Lab Automation Framework
# Main application entry point
# """

# import os
# from app import create_app, db
# from app.auth.models import User
# from app.devices.models import Device, Port
# from app.provisioning.models import ConfigTemplate

# def create_default_data():
#     """Create default data for development"""
#     try:
#         # Create default admin user
#         admin_user = User.query.filter_by(username='admin').first()
#         if not admin_user:
#             admin_user = User(
#                 username='admin',
#                 email='admin@networklab.com',
#                 role='admin'
#             )
#             admin_user.set_password('admin')
#             db.session.add(admin_user)
#             print("Created default admin user (admin/admin)")
        
#         # Create sample devices
#         if Device.query.count() == 0:
#             sample_devices = [
#                 {'name': 'Core-Router-01', 'device_type': 'router', 'ip_address': '192.168.1.1', 'status': 'active'},
#                 {'name': 'Access-Switch-01', 'device_type': 'switch', 'ip_address': '192.168.1.2', 'status': 'active'},
#                 {'name': 'Distribution-Switch-01', 'device_type': 'switch', 'ip_address': '192.168.1.3', 'status': 'inactive'},
#                 {'name': 'Wireless-AP-01', 'device_type': 'wireless', 'ip_address': '192.168.1.50', 'status': 'active'},
#                 {'name': 'Firewall-01', 'device_type': 'firewall', 'ip_address': '192.168.1.254', 'status': 'active'},
#                 {'name': 'Server-01', 'device_type': 'server', 'ip_address': '192.168.1.10', 'status': 'active'}
#             ]
            
#             for device_data in sample_devices:
#                 device = Device(**device_data)
#                 db.session.add(device)
#                 db.session.flush()  # Get the ID
                
#                 # Add sample ports
#                 if device.device_type == 'router':
#                     ports = [
#                         {'name': 'GigabitEthernet0/0', 'port_type': 'ethernet', 'status': 'up'},
#                         {'name': 'GigabitEthernet0/1', 'port_type': 'ethernet', 'status': 'down'},
#                         {'name': 'Serial0/0/0', 'port_type': 'serial', 'status': 'down'}
#                     ]
#                 elif device.device_type == 'switch':
#                     ports = [
#                         {'name': f'FastEthernet0/{i}', 'port_type': 'ethernet', 'status': 'down'}
#                         for i in range(1, 13)
#                     ]
#                 elif device.device_type == 'server':
#                     ports = [
#                         {'name': 'eth0', 'port_type': 'ethernet', 'status': 'up'},
#                         {'name': 'eth1', 'port_type': 'ethernet', 'status': 'down'}
#                     ]
#                 else:
#                     ports = [
#                         {'name': 'port0', 'port_type': 'ethernet', 'status': 'up'}
#                     ]
                
#                 for port_data in ports:
#                     port = Port(device_id=device.id, **port_data)
#                     db.session.add(port)
            
#             print("Created sample devices")
        
#         # Create sample configuration templates
#         if ConfigTemplate.query.count() == 0:
#             templates = [
#                 {
#                     'name': 'Basic Router Configuration',
#                     'device_type': 'router',
#                     'description': 'Basic router configuration template',
#                     'content': '''!
# hostname {{ hostname }}
# !
# interface GigabitEthernet0/0
#  description {{ wan_description|default('WAN Interface') }}
#  ip address {{ wan_ip }} {{ wan_mask }}
#  no shutdown
# !
# interface GigabitEthernet0/1
#  description {{ lan_description|default('LAN Interface') }}
#  ip address {{ lan_ip }} {{ lan_mask }}
#  no shutdown
# !
# router ospf 1
#  network {{ lan_network }} {{ lan_wildcard }} area 0
# !
# line vty 0 4
#  transport input ssh
#  login local
# !
# end''',
#                     'variables': [
#                         {'name': 'hostname', 'description': 'Device hostname', 'required': True},
#                         {'name': 'wan_ip', 'description': 'WAN IP address', 'required': True},
#                         {'name': 'wan_mask', 'description': 'WAN subnet mask', 'required': True},
#                         {'name': 'lan_ip', 'description': 'LAN IP address', 'required': True},
#                         {'name': 'lan_mask', 'description': 'LAN subnet mask', 'required': True}
#                     ]
#                 },
#                 {
#                     'name': 'Basic Switch Configuration',
#                     'device_type': 'switch',
#                     'description': 'Basic switch configuration template',
#                     'content': '''!
# hostname {{ hostname }}
# !
# vlan {{ vlan_id }}
#  name {{ vlan_name }}
# !
# interface range FastEthernet0/1-24
#  switchport mode access
#  switchport access vlan {{ vlan_id }}
#  no shutdown
# !
# interface GigabitEthernet0/1
#  description {{ uplink_description|default('Uplink') }}
#  switchport mode trunk
#  no shutdown
# !
# spanning-tree mode rapid-pvst
# !
# end''',
#                     'variables': [
#                         {'name': 'hostname', 'description': 'Switch hostname', 'required': True},
#                         {'name': 'vlan_id', 'description': 'VLAN ID', 'required': True},
#                         {'name': 'vlan_name', 'description': 'VLAN name', 'required': True}
#                     ]
#                 }
#             ]
            
#             for template_data in templates:
#                 variables = template_data.pop('variables', [])
#                 template = ConfigTemplate(
#                     **template_data,
#                     variables=json.dumps(variables),
#                     created_by=admin_user.id
#                 )
#                 db.session.add(template)
            
#             print("Created sample configuration templates")
        
#         db.session.commit()
#         print("Default data creation completed")
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"Error creating default data: {str(e)}")

# def main():
#     """Main application entry point"""
#     # Create Flask application
#     app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    
#     with app.app_context():
#         # Create database tables
#         db.create_all()
        
#         # Create default data for development
#         if app.config.get('FLASK_ENV') == 'development':
#             create_default_data()
    
#     # Run the application
#     host = os.getenv('FLASK_HOST', '0.0.0.0')
#     port = int(os.getenv('FLASK_PORT', 5000))
#     debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
#     print(f"""
#     ╔═══════════════════════════════════════════════════════════════╗
#     ║              Network Lab Automation Framework                 ║
#     ║                                                               ║
#     ║  API Server: http://{host}:{port}                              ║
#     ║  Health Check: http://{host}:{port}/api/health                 ║
#     ║  Frontend: http://localhost:3232                              ║
#     ║                                                               ║
#     ║  Default Login: admin / admin                                 ║
#     ╚═══════════════════════════════════════════════════════════════╝
#     """)
    
#     app.run(host=host, port=port, debug=debug)




# if __name__ == '__main__':
#     main()


#  This is the new code

# backend/run.py (UPDATED VERSION)
# ===================================

# import os
# import json
# from app import create_app, db

# def create_default_data():
#     """Create default data for development"""
#     try:
#         # Import models here to avoid circular imports
#         from app.auth.models import User
#         from app.devices.models import Device, Port
        
#         # Create default admin user
#         admin_user = User.query.filter_by(username='admin').first()
#         if not admin_user:
#             admin_user = User(
#                 username='admin',
#                 email='admin@networklab.com',
#                 role='admin'
#             )
#             admin_user.set_password('admin')
#             db.session.add(admin_user)
#             print("✅ Created default admin user (admin/admin)")
        
#         # Create sample devices
#         if Device.query.count() == 0:
#             sample_devices = [
#                 {'name': 'Core-Router-01', 'device_type': 'router', 'ip_address': '192.168.1.1', 'status': 'active'},
#                 {'name': 'Access-Switch-01', 'device_type': 'switch', 'ip_address': '192.168.1.2', 'status': 'active'},
#                 {'name': 'Distribution-Switch-01', 'device_type': 'switch', 'ip_address': '192.168.1.3', 'status': 'inactive'},
#                 {'name': 'Wireless-AP-01', 'device_type': 'wireless', 'ip_address': '192.168.1.50', 'status': 'active'},
#                 {'name': 'Firewall-01', 'device_type': 'firewall', 'ip_address': '192.168.1.254', 'status': 'active'},
#                 {'name': 'Server-01', 'device_type': 'server', 'ip_address': '192.168.1.10', 'status': 'active'}
#             ]
            
#             for device_data in sample_devices:
#                 device = Device(**device_data)
#                 db.session.add(device)
#                 db.session.flush()  # Get the ID
                
#                 # Add sample ports based on device type
#                 if device.device_type == 'router':
#                     ports = [
#                         {'name': 'GigabitEthernet0/0', 'port_type': 'ethernet', 'status': 'up'},
#                         {'name': 'GigabitEthernet0/1', 'port_type': 'ethernet', 'status': 'down'},
#                         {'name': 'Serial0/0/0', 'port_type': 'serial', 'status': 'down'}
#                     ]
#                 elif device.device_type == 'switch':
#                     ports = [
#                         {'name': f'FastEthernet0/{i}', 'port_type': 'ethernet', 'status': 'down'}
#                         for i in range(1, 13)
#                     ]
#                 elif device.device_type == 'server':
#                     ports = [
#                         {'name': 'eth0', 'port_type': 'ethernet', 'status': 'up'},
#                         {'name': 'eth1', 'port_type': 'ethernet', 'status': 'down'}
#                     ]
#                 else:
#                     ports = [
#                         {'name': 'port0', 'port_type': 'ethernet', 'status': 'up'}
#                     ]
                
#                 for port_data in ports:
#                     port = Port(device_id=device.id, **port_data)
#                     db.session.add(port)
            
#             print("✅ Created sample devices with ports")
        
#         db.session.commit()
#         print("✅ Default data creation completed successfully")
        
#     except Exception as e:
#         db.session.rollback()
#         print(f"❌ Error creating default data: {str(e)}")
#         import traceback
#         traceback.print_exc()

# def main():
#     """Main application entry point"""
#     # Create Flask application
#     app = create_app()
    
#     with app.app_context():
#         try:
#             # Create database tables
#             print("🔄 Creating database tables...")
#             db.create_all()
#             print("✅ Database tables created")
            
#             # Create default data for development
#             if os.getenv('FLASK_ENV', 'development') == 'development':
#                 print("🔄 Creating default development data...")
#                 create_default_data()
                
#         except Exception as e:
#             print(f"❌ Database initialization error: {str(e)}")
#             import traceback
#             traceback.print_exc()
    
#     # Run the application
#     host = os.getenv('FLASK_HOST', '0.0.0.0')
#     port = int(os.getenv('FLASK_PORT', 5000))
#     debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
#     print(f"""
#     ╔═══════════════════════════════════════════════════════════════╗
#     ║              Network Lab Automation Framework                 ║
#     ║                                                               ║
#     ║  🌐 API Server: http://{host}:{port:<44} ║
#     ║  ❤️  Health Check: http://{host}:{port}/api/health{' ' * 25} ║
#     ║  🎨 Frontend: http://localhost:3232{' ' * 31} ║
#     ║                                                               ║
#     ║  👤 Default Login: admin / admin{' ' * 29} ║
#     ║  📊 Environment: {os.getenv('FLASK_ENV', 'development'):<44} ║
#     ╚═══════════════════════════════════════════════════════════════╝
#     """)
    
#     app.run(host=host, port=port, debug=debug)

# if __name__ == '__main__':
#     main()





import os
import sys
from flask import Flask
from sqlalchemy import text

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/network_lab')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
    
    # Initialize extensions
    from app.extensions import db, migrate, jwt, limiter
    from flask_cors import CORS
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app, origins=["http://localhost:3232", "http://127.0.0.1:3232"])
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.devices.routes import devices_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(devices_bp, url_prefix='/api/devices')
    
    # ROOT ROUTE (FIX FOR ISSUE 1)
    @app.route('/')
    def root():
        return {
            'message': 'Network Lab Automation Framework API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/login',
                'devices': '/api/devices'
            }
        }, 200
    
    # Health check route (FIX FOR ISSUE 2)
    @app.route('/api/health')
    def health_check():
        try:
            # Test database connection using text() for SQLAlchemy
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return {
            'status': 'healthy',
            'service': 'backend',
            'database': db_status,
            'environment': os.getenv('FLASK_ENV', 'development'),
            'timestamp': str(datetime.utcnow())
        }, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found', 'available_endpoints': [
            '/', '/api/health', '/api/auth/login', '/api/devices'
        ]}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    # Create tables and sample data
    with app.app_context():
        try:
            print("🔄 Creating database tables...")
            db.create_all()
            print("✅ Database tables created")
            
            # Create sample data for development
            if os.getenv('FLASK_ENV', 'development') == 'development':
                create_sample_data()
                
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
    
    return app

def create_sample_data():
    """Create sample data for development"""
    try:
        from app.extensions import db
        from app.models import User, Device, Port
        
        # Create default admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@networklab.com',
                role='admin'
            )
            admin_user.set_password('admin')
            db.session.add(admin_user)
            print("✅ Created default admin user (admin/admin)")
        
        # Create sample devices
        if Device.query.count() == 0:
            sample_devices = [
                {'name': 'Core-Router-01', 'device_type': 'router', 'ip_address': '192.168.1.1', 'status': 'active'},
                {'name': 'Access-Switch-01', 'device_type': 'switch', 'ip_address': '192.168.1.2', 'status': 'active'},
                {'name': 'Server-01', 'device_type': 'server', 'ip_address': '192.168.1.10', 'status': 'active'}
            ]
            
            for device_data in sample_devices:
                device = Device(**device_data)
                db.session.add(device)
                db.session.flush()  # Get the ID
                
                # Add sample ports
                if device.device_type == 'router':
                    ports = [
                        {'name': 'GigabitEthernet0/0', 'port_type': 'ethernet', 'status': 'up'},
                        {'name': 'GigabitEthernet0/1', 'port_type': 'ethernet', 'status': 'down'}
                    ]
                elif device.device_type == 'switch':
                    ports = [
                        {'name': f'FastEthernet0/{i}', 'port_type': 'ethernet', 'status': 'down'}
                        for i in range(1, 5)
                    ]
                else:
                    ports = [
                        {'name': 'eth0', 'port_type': 'ethernet', 'status': 'up'}
                    ]
                
                for port_data in ports:
                    port = Port(device_id=device.id, **port_data)
                    db.session.add(port)
            
            print("✅ Created sample devices with ports")
        
        db.session.commit()
        print("✅ Sample data creation completed")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main application entry point"""
    app = create_app()
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║              Network Lab Automation Framework                 ║
    ║                                                               ║
    ║  🌐 Root URL: http://{host}:{port}                            ║
    ║  ❤️  Health Check: http://{host}:{port}/api/health            ║
    ║  🔑 Login: http://{host}:{port}/api/auth/login                ║
    ║  📱 Devices: http://{host}:{port}/api/devices                 ║
    ║  🎨 Frontend: http://localhost:3232                          ║
    ║                                                               ║
    ║  👤 Default Login: admin / admin                             ║
    ║  📊 Environment: {os.getenv('FLASK_ENV', 'development')}     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    from datetime import datetime
    main()