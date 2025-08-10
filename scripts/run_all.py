#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys
import shutil

class NDISPlatformRunner:
    def __init__(self):
        self.processes = []
    
    def cleanup_ports(self):
        """Clean up any processes using our ports"""
        print("🧹 Cleaning up ports...")
        
        try:
            # Kill Node.js processes (more specific)
            subprocess.run(['taskkill', '/F', '/IM', 'node.exe'], 
                         capture_output=True, check=False, timeout=10)
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        try:
            # Find and kill process on port 3000
            result = subprocess.run(['netstat', '-ano'], 
                                  capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if ':3000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                     capture_output=True, check=False, timeout=5)
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        print("✅ Ports cleaned up")
    
    def check_prerequisites(self):
        """Check if all required tools are available"""
        print("🔍 Checking prerequisites...")
        
        # Check Docker
        if not shutil.which("docker"):
            print("❌ Docker not found. Please install Docker Desktop.")
            return False
        
        # Check Node.js and npm
        if not shutil.which("node"):
            print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
            return False
            
        if not shutil.which("npm"):
            print("❌ npm not found. Please install Node.js from https://nodejs.org/")
            return False
        
        # Check Python
        if not shutil.which("python"):
            print("❌ Python not found.")
            return False
        
        print("✅ All prerequisites found")
        return True
    
    def install_dependencies(self):
        """Install Python and Node.js dependencies"""
        print("📦 Installing dependencies...")
        
        # Install Python dependencies (skip problematic ones)
        try:
            print("🐍 Installing Python dependencies...")
            # Install essential packages individually
            essential_packages = [
                "Flask", "Flask-CORS", "Flask-JWT-Extended", 
                "python-dotenv", "bcrypt", "requests", "sqlalchemy"
            ]
            
            for package in essential_packages:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to install {package}, but continuing...")
            
            # Install requests for health checks
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "requests"
                ], check=True, capture_output=True, text=True)
            except:
                pass
            
            # psycopg2-binary was already installed successfully
            print("✅ Python dependencies installed")
        except Exception as e:
            print(f"⚠️ Some Python dependencies failed, but continuing: {e}")
        
        # Install Node.js dependencies
        try:
            print("⚛️ Installing Node.js dependencies...")
            original_dir = os.getcwd()
            os.chdir("frontend")
            
            # Check if node_modules exists
            if not os.path.exists("node_modules"):
                subprocess.run(["npm", "install"], check=True, capture_output=True, text=True)
                print("✅ Node.js dependencies installed")
            else:
                print("✅ Node.js dependencies already installed")
                
            os.chdir(original_dir)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Node.js dependencies failed, but continuing: {e}")
            os.chdir(original_dir)
        except Exception as e:
            print(f"⚠️ Error during Node.js dependency installation: {e}")
            os.chdir(original_dir)
        
        return True
    
    def start_database(self):
        """Start PostgreSQL database"""
        print("🗄️ Starting database...")
        try:
            # Stop existing container if running
            subprocess.run(["docker", "stop", "ndis-postgres"], 
                         capture_output=True, check=False)
            subprocess.run(["docker", "rm", "ndis-postgres"], 
                         capture_output=True, check=False)
            
            # Start new container
            subprocess.run([
                "docker", "run", "-d",
                "--name", "ndis-postgres",
                "-e", "POSTGRES_DB=ndis_platform",
                "-e", "POSTGRES_USER=postgres", 
                "-e", "POSTGRES_PASSWORD=password",
                "-p", "5432:5432",
                "postgres:15"
            ], check=True)
            print("✅ Database started")
            time.sleep(5)  # Wait for database to initialize
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start database: {e}")
            return False
        return True
    
    def setup_database(self):
        """Initialize database with schema and sample data"""
        print("📊 Setting up database schema...")
        try:
            # Run init script
            with open("database/init.sql", "r") as f:
                init_sql = f.read()
            
            subprocess.run([
                "docker", "exec", "-i", "ndis-postgres",
                "psql", "-U", "postgres", "-d", "ndis_platform"
            ], input=init_sql, text=True, check=True, capture_output=True)
            
            # Insert sample data
            with open("database/sample_data.sql", "r") as f:
                sample_sql = f.read()
                
            subprocess.run([
                "docker", "exec", "-i", "ndis-postgres", 
                "psql", "-U", "postgres", "-d", "ndis_platform"
            ], input=sample_sql, text=True, check=True, capture_output=True)
            
            print("✅ Database schema and sample data loaded")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Database setup warning: {e}")
        except FileNotFoundError as e:
            print(f"❌ Database setup failed: {e}")
            return False
        return True
    
    def start_backend(self):
        """Start Flask backend"""
        print("🐍 Starting backend API...")
        try:
            original_dir = os.getcwd()
            os.chdir("backend")
            
            # Use full path to python executable
            process = subprocess.Popen([
                sys.executable, "app.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes.append(('backend', process))
            os.chdir(original_dir)
            print("✅ Backend API starting on http://localhost:5000")
            return process
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            os.chdir(original_dir)
            return None
    
    def start_frontend(self):
        """Start React frontend"""
        print("⚛️ Starting frontend...")
        try:
            original_dir = os.getcwd()
            os.chdir("frontend")
            
            # Use full path to npm
            npm_path = shutil.which("npm")
            if not npm_path:
                print("❌ npm not found in PATH")
                os.chdir(original_dir)
                return None
            
            # Set environment variables to prevent auto-opening browser and other issues
            env = os.environ.copy()
            env.update({
                "BROWSER": "none",
                "CI": "true",
                "FORCE_COLOR": "0",
                "NODE_ENV": "development"
            })
            
            process = subprocess.Popen([
                npm_path, "start"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=env, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
            
            self.processes.append(('frontend', process))
            os.chdir(original_dir)
            print("✅ Frontend starting on http://localhost:3000")
            
            # Give frontend time to start
            time.sleep(10)
            return process
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            os.chdir(original_dir)
            return None
    
    def start_automation(self):
        """Start automation workflows"""
        print("🤖 Starting automation workflows...")
        try:
            original_dir = os.getcwd()
            os.chdir("automation")
            
            process = subprocess.Popen([
                sys.executable, "notification_workflows.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes.append(('automation', process))
            os.chdir(original_dir)
            print("✅ Automation workflows started")
            return process
        except Exception as e:
            print(f"❌ Failed to start automation: {e}")
            os.chdir(original_dir)
            return None
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to start...")
        
        # Wait for backend
        backend_ready = False
        for i in range(30):  # Try for 30 seconds
            try:
                import requests
                response = requests.get("http://localhost:5000/api/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Backend is responding")
                    backend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not backend_ready:
            print("⚠️ Backend health check failed")
            return False
        
        # Wait for frontend
        frontend_ready = False
        for i in range(30):  # Try for 30 seconds
            try:
                import requests
                response = requests.get("http://localhost:3000", timeout=2)
                if response.status_code == 200:
                    print("✅ Frontend is responding")
                    frontend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not frontend_ready:
            print("⚠️ Frontend may still be starting...")
            
        return True
    
    def monitor_processes(self):
        """Monitor all processes"""
        print("\n🔍 Monitoring all services...")
        print("📱 Access the application at: http://localhost:3000")
        print("🔐 Demo login: admin@ndis.com / admin123")
        print("\n⌨️ Press Ctrl+C to stop all services\n")
        
        try:
            while True:
                all_running = True
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"❌ {name} process has stopped")
                        all_running = False
                        break
                
                if not all_running:
                    print("❌ A service has stopped. Shutting down...")
                    return
                
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all services...")
        
        # Stop all processes
        for name, process in self.processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"Error stopping {name}: {e}")
        
        # Stop database container
        try:
            subprocess.run(["docker", "stop", "ndis-postgres"], 
                         check=True, capture_output=True)
            subprocess.run(["docker", "rm", "ndis-postgres"], 
                         check=True, capture_output=True)
            print("✅ Database stopped")
        except subprocess.CalledProcessError:
            print("⚠️ Database was not running")
        
        print("✅ All services stopped")
    
    def run(self):
        """Run the entire platform"""
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Install dependencies (continue even if some fail)
            self.install_dependencies()
            
            # Start database
            if not self.start_database():
                return False
            
            # Setup database
            if not self.setup_database():
                return False
            
            # Start backend
            backend_process = self.start_backend()
            if not backend_process:
                return False
            
            time.sleep(3)  # Give backend time to start
            
            # Start frontend
            frontend_process = self.start_frontend()
            if not frontend_process:
                return False
            
            time.sleep(2)  # Give frontend time to start
            
            # Start automation
            automation_process = self.start_automation()
            if not automation_process:
                print("⚠️ Automation failed to start, but continuing...")
            
            # Wait for services and monitor
            self.wait_for_services()
            self.monitor_processes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.stop_all()
            return False
        except KeyboardInterrupt:
            self.stop_all()
            return True

if __name__ == "__main__":
    print("🚀 NDIS Platform Startup Script")
    print("=" * 50)
    
    runner = NDISPlatformRunner()
    success = runner.run()
    
    if not success:
        print("\n❌ Platform failed to start completely")
        sys.exit(1)
    else:
        print("\n✅ Platform shutdown complete")
        sys.exit(0)