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
        self.npm_cmd = "npm"  # Default, will be updated in check_prerequisites
    
    def cleanup_ports(self):
        """Clean up any processes using our ports"""
        print("🧹 Cleaning up ports...")
        
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'node.exe'], 
                         capture_output=True, check=False, timeout=10)
        except:
            pass
        
        print("✅ Ports cleaned up")
    
    def check_prerequisites(self):
        """Check if all required tools are available"""
        print("🔍 Checking prerequisites...")
        
        # Check Docker
        if not shutil.which("docker"):
            print("❌ Docker not found. Please install Docker Desktop.")
            return False
        
        # Check Node.js and npm - try different ways on Windows
        node_cmd = shutil.which("node")
        if not node_cmd:
            print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
            return False
        
        # Try to find npm - on Windows it might be npm.cmd
        npm_cmd = shutil.which("npm") or shutil.which("npm.cmd")
        if not npm_cmd:
            print("❌ npm not found. Please install Node.js from https://nodejs.org/")
            return False
        
        # Store the correct npm command for later use
        self.npm_cmd = npm_cmd
        
        # Check Python
        if not shutil.which("python"):
            print("❌ Python not found.")
            return False
        
        print("✅ All prerequisites found")
        return True
    
    def install_dependencies(self):
        """Install Python and Node.js dependencies"""
        print("📦 Installing dependencies...")
        
        # Install Python dependencies
        try:
            print("🐍 Installing Python dependencies...")
            essential_packages = [
                "Flask", "Flask-CORS", "Flask-JWT-Extended", 
                "python-dotenv", "bcrypt", "requests", "sqlalchemy"
            ]
            
            for package in essential_packages:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], check=True, capture_output=True, text=True)
                except:
                    print(f"⚠️ Failed to install {package}, but continuing...")
            
            print("✅ Python dependencies installed")
        except Exception as e:
            print(f"⚠️ Some Python dependencies failed: {e}")
        
        # Install Node.js dependencies
        try:
            print("⚛️ Installing Node.js dependencies...")
            original_dir = os.getcwd()
            os.chdir("frontend")
            
            # Remove node_modules if it exists and is problematic
            if os.path.exists("node_modules"):
                try:
                    shutil.rmtree("node_modules")
                    print("🗑️ Removed existing node_modules")
                except:
                    pass
            
            # Remove package-lock.json if it exists
            if os.path.exists("package-lock.json"):
                try:
                    os.remove("package-lock.json")
                    print("🗑️ Removed package-lock.json")
                except:
                    pass
            
            # Install with npm
            result = subprocess.run([self.npm_cmd, "install"], 
                                  capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print("✅ Node.js dependencies installed")
            else:
                print(f"⚠️ npm install had issues: {result.stderr}")
                # Try with legacy peer deps
                subprocess.run([self.npm_cmd, "install", "--legacy-peer-deps"], 
                             capture_output=True, text=True, timeout=180)
                print("✅ Node.js dependencies installed with legacy-peer-deps")
                
            os.chdir(original_dir)
        except Exception as e:
            print(f"⚠️ Node.js dependency installation error: {e}")
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
                "psql", "-U", "postgres", "-d", "postgres"
            ], input=init_sql, text=True, check=True, capture_output=True)
            
            # Insert sample data
            with open("database/sample_data.sql", "r") as f:
                sample_sql = f.read()
                
            subprocess.run([
                "docker", "exec", "-i", "ndis-postgres", 
                "psql", "-U", "postgres", "-d", "ndis_platform"
            ], input=sample_sql, text=True, check=True, capture_output=True)
            
            print("✅ Database schema and sample data loaded")
        except:
            print("⚠️ Database setup warning, but continuing...")
        return True
    
    def start_backend(self):
        """Start Flask backend"""
        print("🐍 Starting backend API...")
        try:
            original_dir = os.getcwd()
            os.chdir("backend")
            
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
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "BROWSER": "none",
                "CI": "false"
            })
            
            process = subprocess.Popen([
                self.npm_cmd, "start"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=env)
            
            self.processes.append(('frontend', process))
            os.chdir(original_dir)
            print("✅ Frontend starting on http://localhost:3000")
            
            time.sleep(10)  # Give frontend time to start
            return process
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            os.chdir(original_dir)
            return None
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to start...")
        
        # Wait for backend
        backend_ready = False
        for i in range(30):
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
        except:
            print("⚠️ Database was not running")
        
        print("✅ All services stopped")
    
    def run(self):
        """Run the entire platform"""
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Install dependencies
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
            
            time.sleep(3)
            
            # Start frontend
            frontend_process = self.start_frontend()
            if not frontend_process:
                return False
            
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