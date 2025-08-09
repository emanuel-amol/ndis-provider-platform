#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys

class NDISPlatformRunner:
    def __init__(self):
        self.processes = []
    
    def start_database(self):
        """Start PostgreSQL database"""
        print("🗄️ Starting database...")
        try:
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
        except subprocess.CalledProcessError:
            print("ℹ️ Database container might already be running")
    
    def setup_database(self):
        """Initialize database with schema and sample data"""
        print("📊 Setting up database schema...")
        try:
            # Run init script
            subprocess.run([
                "docker", "exec", "-i", "ndis-postgres",
                "psql", "-U", "postgres", "-d", "ndis_platform"
            ], input=open("database/init.sql", "r").read(), text=True, check=True)
            
            # Insert sample data
            subprocess.run([
                "docker", "exec", "-i", "ndis-postgres", 
                "psql", "-U", "postgres", "-d", "ndis_platform"
            ], input=open("database/sample_data.sql", "r").read(), text=True, check=True)
            
            print("✅ Database schema and sample data loaded")
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
    
    def start_backend(self):
        """Start Flask backend"""
        print("🐍 Starting backend API...")
        os.chdir("backend")
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.processes.append(process)
        os.chdir("..")
        print("✅ Backend API starting on http://localhost:5000")
        return process
    
    def start_frontend(self):
        """Start React frontend"""
        print("⚛️ Starting frontend...")
        os.chdir("frontend")
        process = subprocess.Popen([
            "npm", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.processes.append(process)
        os.chdir("..")
        print("✅ Frontend starting on http://localhost:3000")
        return process
    
    def start_automation(self):
        """Start automation workflows"""
        print("🤖 Starting automation workflows...")
        os.chdir("automation")
        process = subprocess.Popen([
            sys.executable, "notification_workflows.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.processes.append(process)
        os.chdir("..")
        print("✅ Automation workflows started")
        return process
    
    def monitor_processes(self):
        """Monitor all processes"""
        print("\n🔍 Monitoring all services...")
        print("📱 Access the application at: http://localhost:3000")
        print("🔐 Demo login: admin@ndis.com / admin123")
        print("\n⌨️ Press Ctrl+C to stop all services\n")
        
        try:
            while True:
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"❌ Process {i} has stopped")
                        return
                time.sleep(2)
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Stop database container
        try:
            subprocess.run(["docker", "stop", "ndis-postgres"], check=True)
            subprocess.run(["docker", "rm", "ndis-postgres"], check=True)
        except subprocess.CalledProcessError:
            pass
        
        print("✅ All services stopped")
    
    def run(self):
        """Run the entire platform"""
        try:
            self.start_database()
            self.setup_database()
            
            print("⏳ Waiting for services to start...")
            time.sleep(3)
            
            self.start_backend()
            time.sleep(2)
            
            self.start_frontend()
            time.sleep(2)
            
            self.start_automation()
            time.sleep(2)
            
            self.monitor_processes()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.stop_all()
        except KeyboardInterrupt:
            self.stop_all()

if __name__ == "__main__":
    runner = NDISPlatformRunner()
    runner.run()