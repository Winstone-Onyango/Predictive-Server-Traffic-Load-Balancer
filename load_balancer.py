from flask import Flask, request, jsonify, render_template_string
import threading
import time
import random
import json
from datetime import datetime
import math

# ========== IMPROVED UI HTML TEMPLATE ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Predictive Load Balancer Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3B82F6',
                        success: '#10B981',
                        warning: '#F59E0B',
                        danger: '#EF4444',
                        dark: '#1F2937'
                    }
                }
            }
        }
    </script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .server-card {
            transition: all 0.3s ease;
            border-left: 4px solid;
        }
        .server-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        .health-bar {
            transition: width 0.5s ease-in-out;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .traffic-gauge {
            background: conic-gradient(#10B981 0% 25%, #F59E0B 25% 75%, #EF4444 75% 100%);
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="bg-white/20 p-3 rounded-full">
                        <i class="fas fa-brain text-2xl"></i>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold">Predictive Load Balancer</h1>
                        <p class="text-blue-100">AI-Powered Traffic Management System</p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-sm opacity-90" id="currentTime">Loading...</div>
                    <div class="text-xs opacity-75" id="systemStatus">System: <span class="font-semibold text-green-300">Operational</span></div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Dashboard -->
    <main class="container mx-auto px-4 py-8">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-primary">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Current Traffic</p>
                        <p class="text-3xl font-bold text-gray-800" id="currentTraffic">0</p>
                        <p class="text-sm text-gray-500">requests/sec</p>
                    </div>
                    <div class="bg-blue-100 p-3 rounded-full">
                        <i class="fas fa-traffic-light text-blue-600 text-xl"></i>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-warning">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Predicted Traffic</p>
                        <p class="text-3xl font-bold text-gray-800" id="predictedTraffic">0</p>
                        <p class="text-sm text-gray-500">in 30 minutes</p>
                    </div>
                    <div class="bg-yellow-100 p-3 rounded-full">
                        <i class="fas fa-chart-line text-yellow-600 text-xl"></i>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-success">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Healthy Servers</p>
                        <p class="text-3xl font-bold text-gray-800" id="healthyServers">0</p>
                        <p class="text-sm text-gray-500">of <span id="totalServers">0</span> total</p>
                    </div>
                    <div class="bg-green-100 p-3 rounded-full">
                        <i class="fas fa-server text-green-600 text-xl"></i>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-danger">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Spike Detection</p>
                        <p class="text-3xl font-bold text-gray-800" id="spikeStatus">No</p>
                        <p class="text-sm text-gray-500">traffic normal</p>
                    </div>
                    <div class="bg-red-100 p-3 rounded-full">
                        <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Traffic Visualization -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <!-- Traffic Gauge -->
            <div class="bg-white rounded-xl shadow-md p-6 lg:col-span-1">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Traffic Load</h3>
                <div class="flex justify-center">
                    <div class="relative w-48 h-48">
                        <div class="traffic-gauge w-full h-full rounded-full flex items-center justify-center">
                            <div class="bg-white w-3/4 h-3/4 rounded-full flex items-center justify-center">
                                <div class="text-center">
                                    <div id="gaugeValue" class="text-2xl font-bold text-gray-800">0%</div>
                                    <div class="text-sm text-gray-600">Load</div>
                                </div>
                            </div>
                        </div>
                        <div id="gaugeNeedle" class="absolute top-0 left-1/2 w-1 h-24 bg-gray-800 transform origin-bottom transition-transform duration-1000" style="transform: translateX(-50%) rotate(0deg);"></div>
                    </div>
                </div>
            </div>

            <!-- Server Health Overview -->
            <div class="bg-white rounded-xl shadow-md p-6 lg:col-span-2">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Server Health Overview</h3>
                <div id="serverHealthBars" class="space-y-4">
                    <!-- Server health bars will be populated by JavaScript -->
                    <div class="text-center text-gray-500 py-8">
                        <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                        <p>Loading server data...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Server Cards -->
        <div class="mb-8">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Server Details</h3>
            <div id="serverCards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Server cards will be populated by JavaScript -->
                <div class="text-center text-gray-500 py-8 col-span-full">
                    <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                    <p>Loading server information...</p>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-xl shadow-md p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
            <div class="flex flex-wrap gap-4">
                <button onclick="routeRequest()" class="bg-primary hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition duration-200 flex items-center space-x-2">
                    <i class="fas fa-route"></i>
                    <span>Test Route Request</span>
                </button>
                <button onclick="refreshData()" class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition duration-200 flex items-center space-x-2">
                    <i class="fas fa-sync-alt"></i>
                    <span>Refresh Data</span>
                </button>
                <button onclick="simulateSpike()" class="bg-warning hover:bg-yellow-600 text-white px-6 py-3 rounded-lg font-medium transition duration-200 flex items-center space-x-2">
                    <i class="fas fa-bolt"></i>
                    <span>Simulate Traffic Spike</span>
                </button>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white py-6 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p class="text-gray-400">Predictive Load Balancer Dashboard • Built with Flask & Machine Learning</p>
            <p class="text-gray-500 text-sm mt-2">Real-time monitoring and predictive analytics for optimal performance</p>
        </div>
    </footer>

    <!-- JavaScript for real-time updates -->
    <script>
        let updateInterval;

        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleString();
        }

        function loadGauge(value) {
            // Convert value to degrees (-135deg to 135deg)
            const degrees = (value / 100) * 270 - 135;
            document.getElementById('gaugeNeedle').style.transform = `translateX(-50%) rotate(${degrees}deg)`;
            document.getElementById('gaugeValue').textContent = Math.round(value) + '%';
        }

        function updateDashboard() {
            fetch('/dashboard_data')
                .then(response => response.json())
                .then(data => {
                    // Update stats
                    document.getElementById('currentTraffic').textContent = Math.round(data.current_traffic);
                    document.getElementById('predictedTraffic').textContent = Math.round(data.predicted_traffic);
                    document.getElementById('healthyServers').textContent = data.healthy_servers;
                    document.getElementById('totalServers').textContent = data.total_servers;
                    document.getElementById('spikeStatus').textContent = data.traffic_spike ? 'Yes' : 'No';
                    document.getElementById('spikeStatus').className = data.traffic_spike ? 
                        'text-3xl font-bold text-red-600 pulse' : 'text-3xl font-bold text-green-600';

                    // Update gauge (0-100 scale)
                    const loadPercentage = Math.min(100, (data.current_traffic / 500) * 100);
                    loadGauge(loadPercentage);

                    // Update server health bars
                    updateServerHealthBars(data.servers);

                    // Update server cards
                    updateServerCards(data.servers);
                })
                .catch(error => {
                    console.error('Error fetching dashboard data:', error);
                });
        }

        function updateServerHealthBars(servers) {
            const container = document.getElementById('serverHealthBars');
            container.innerHTML = '';

            Object.entries(servers).forEach(([serverId, server]) => {
                const health = server.health_score;
                let color = 'bg-green-500';
                if (health < 60) color = 'bg-yellow-500';
                if (health < 40) color = 'bg-red-500';

                const bar = `
                    <div class="flex items-center justify-between">
                        <span class="text-sm font-medium text-gray-700 w-20">${serverId}</span>
                        <div class="flex-1 mx-4">
                            <div class="w-full bg-gray-200 rounded-full h-3">
                                <div class="health-bar h-3 rounded-full ${color} transition-all duration-500" 
                                     style="width: ${health}%"></div>
                            </div>
                        </div>
                        <span class="text-sm font-semibold w-12 text-right ${health < 60 ? 'text-red-600' : 'text-green-600'}">
                            ${Math.round(health)}%
                        </span>
                    </div>
                `;
                container.innerHTML += bar;
            });
        }

        function updateServerCards(servers) {
            const container = document.getElementById('serverCards');
            container.innerHTML = '';

            Object.entries(servers).forEach(([serverId, server]) => {
                const isOverloaded = server.cpu_usage > 0.8 || server.memory_usage > 0.85;
                const borderColor = isOverloaded ? 'border-red-500' : 'border-green-500';
                const statusColor = isOverloaded ? 'text-red-600' : 'text-green-600';
                const statusIcon = isOverloaded ? 'fa-exclamation-circle' : 'fa-check-circle';

                const card = `
                    <div class="server-card bg-white rounded-lg shadow-md p-6 ${borderColor}">
                        <div class="flex items-center justify-between mb-4">
                            <h4 class="font-bold text-lg text-gray-800">${serverId.toUpperCase()}</h4>
                            <i class="fas ${statusIcon} ${statusColor}"></i>
                        </div>
                        
                        <div class="space-y-3">
                            <div class="flex justify-between items-center">
                                <span class="text-gray-600">CPU Usage:</span>
                                <span class="font-semibold ${server.cpu_usage > 0.7 ? 'text-red-600' : 'text-green-600'}">
                                    ${Math.round(server.cpu_usage * 100)}%
                                </span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-gray-600">Memory:</span>
                                <span class="font-semibold ${server.memory_usage > 0.8 ? 'text-red-600' : 'text-green-600'}">
                                    ${Math.round(server.memory_usage * 100)}%
                                </span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-gray-600">Response Time:</span>
                                <span class="font-semibold ${server.response_time > 1.0 ? 'text-red-600' : 'text-green-600'}">
                                    ${server.response_time.toFixed(2)}s
                                </span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-gray-600">Error Rate:</span>
                                <span class="font-semibold ${server.error_rate > 0.05 ? 'text-red-600' : 'text-green-600'}">
                                    ${Math.round(server.error_rate * 100)}%
                                </span>
                            </div>
                        </div>

                        <div class="mt-4 pt-4 border-t border-gray-200">
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-600">Health Score:</span>
                                <span class="font-bold text-lg ${server.health_score < 60 ? 'text-red-600' : 'text-green-600'}">
                                    ${Math.round(server.health_score)}%
                                </span>
                            </div>
                            <div class="flex justify-between items-center mt-2">
                                <span class="text-sm text-gray-600">Risk Level:</span>
                                <span class="font-semibold ${server.risk_level === 'high' ? 'text-red-600' : server.risk_level === 'medium' ? 'text-yellow-600' : 'text-green-600'}">
                                    ${server.risk_level.toUpperCase()}
                                </span>
                            </div>
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            });
        }

        // Action functions
        function routeRequest() {
            fetch('/route')
                .then(response => response.json())
                .then(data => {
                    alert(`Request routed to: ${data.server}\n${data.message}`);
                });
        }

        function refreshData() {
            updateDashboard();
            showNotification('Data refreshed successfully!', 'success');
        }

        function simulateSpike() {
            fetch('/simulate_spike', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    showNotification('Traffic spike simulated!', 'warning');
                    updateDashboard();
                });
        }

        function showNotification(message, type = 'info') {
            // Simple notification - you can enhance this with a proper notification library
            alert(`${type.toUpperCase()}: ${message}`);
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            updateTime();
            updateDashboard();
            setInterval(updateTime, 1000);
            setInterval(updateDashboard, 2000); // Update every 2 seconds
        });
    </script>
</body>
</html>
"""

# ========== KEEP ALL THE EXISTING CLASSES THE SAME ==========
class SimpleTrafficPredictor:
    def __init__(self):
        print("🚀 Simple Traffic Predictor Started!")
        self.traffic_history = []
        self.max_history = 100
        
    def add_traffic_data(self, current_traffic):
        timestamp = datetime.now()
        self.traffic_history.append({
            'timestamp': timestamp,
            'traffic': current_traffic,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        })
        
        if len(self.traffic_history) > self.max_history:
            self.traffic_history.pop(0)
    
    def predict_next_traffic(self):
        if len(self.traffic_history) < 10:
            return random.uniform(50, 150)
            
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        recent_traffic = [item['traffic'] for item in self.traffic_history[-10:]]
        avg_recent = sum(recent_traffic) / len(recent_traffic)
        
        if current_hour >= 9 and current_hour <= 17:
            prediction = avg_recent * 1.3
        elif current_hour >= 18 and current_hour <= 22:
            prediction = avg_recent * 1.5
        else:
            prediction = avg_recent * 0.7
            
        if current_day >= 5:
            prediction = prediction * 0.8
            
        return max(10, prediction)
    
    def detect_spike(self, current_traffic):
        if len(self.traffic_history) < 5:
            return False
            
        recent_avg = sum([item['traffic'] for item in self.traffic_history[-5:]]) / 5
        return current_traffic > recent_avg * 1.5

class ServerHealthMonitor:
    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.server_metrics = {}
        print("🏥 Server Health Monitor Started!")
        
    def update_server_metrics(self, server_id, metrics):
        self.server_metrics[server_id] = {
            **metrics,
            'last_update': datetime.now(),
            'health_score': self.calculate_health_score(metrics)
        }
    
    def calculate_health_score(self, metrics):
        scores = []
        
        cpu_score = max(0, 100 - (metrics.get('cpu_usage', 0) * 100))
        scores.append(cpu_score)
        
        memory_score = max(0, 100 - (metrics.get('memory_usage', 0) * 100))
        scores.append(memory_score)
        
        response_time = metrics.get('response_time', 0)
        response_score = max(0, 100 - (response_time * 10))
        scores.append(response_score)
        
        error_rate = metrics.get('error_rate', 0)
        error_score = max(0, 100 - (error_rate * 1000))
        scores.append(error_score)
        
        avg_score = sum(scores) / len(scores)
        return avg_score
    
    def get_best_server(self):
        if not self.server_metrics:
            return None
            
        best_server = max(self.server_metrics.items(), key=lambda x: x[1]['health_score'])
        return best_server[0]
    
    def is_server_overloaded(self, server_id):
        if server_id not in self.server_metrics:
            return True
            
        metrics = self.server_metrics[server_id]
        
        thresholds = self.config['overload_thresholds']
        if (metrics.get('cpu_usage', 0) > thresholds['cpu_usage'] or
            metrics.get('memory_usage', 0) > thresholds['memory_usage'] or
            metrics.get('response_time', 0) > thresholds['response_time'] or
            metrics.get('error_rate', 0) > thresholds['error_rate']):
            return True
            
        return False
    
    def predict_overload_risk(self, server_id, predicted_traffic):
        if server_id not in self.server_metrics:
            return "unknown"
            
        current_metrics = self.server_metrics[server_id]
        current_traffic = current_metrics.get('request_rate', 1)
        
        traffic_increase = predicted_traffic / max(1, current_traffic)
        
        if traffic_increase > 2.0:
            return "high"
        elif traffic_increase > 1.5:
            return "medium"
        else:
            return "low"

class PredictiveLoadBalancer:
    def __init__(self):
        print("🔀 Starting Predictive Load Balancer...")
        
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.predictor = SimpleTrafficPredictor()
        self.health_monitor = ServerHealthMonitor()
        self.current_traffic = 100
        
        self.initialize_servers()
        self.setup_background_tasks()
        
        print("✅ Load Balancer Ready!")
    
    def initialize_servers(self):
        for server_id in self.config['servers']:
            self.health_monitor.update_server_metrics(server_id, {
                'cpu_usage': random.uniform(0.1, 0.4),
                'memory_usage': random.uniform(0.3, 0.6),
                'response_time': random.uniform(0.1, 0.5),
                'error_rate': random.uniform(0.0, 0.02),
                'request_rate': random.uniform(80, 120)
            })
    
    def setup_background_tasks(self):
        def traffic_simulator():
            while True:
                base_traffic = 100
                hour = time.localtime().tm_hour
                
                if 9 <= hour <= 17:
                    self.current_traffic = random.randint(150, 300)
                elif 18 <= hour <= 22:
                    self.current_traffic = random.randint(200, 400)
                else:
                    self.current_traffic = random.randint(50, 150)
                
                if random.random() < 0.1:
                    self.current_traffic = random.randint(500, 800)
                    print("🚨 TRAFFIC SPIKE DETECTED!")
                
                self.predictor.add_traffic_data(self.current_traffic)
                time.sleep(5)
        
        def metrics_updater():
            while True:
                for server_id in self.config['servers']:
                    traffic_per_server = self.current_traffic / len(self.config['servers'])
                    
                    cpu_usage = min(0.95, (traffic_per_server / 100) * 0.3 + random.uniform(0.1, 0.3))
                    memory_usage = min(0.95, 0.4 + random.uniform(0.1, 0.3))
                    response_time = max(0.1, (traffic_per_server / 100) * 0.2 + random.uniform(0.1, 0.4))
                    error_rate = max(0.0, (traffic_per_server / 500) * 0.1 + random.uniform(0.0, 0.05))
                    
                    self.health_monitor.update_server_metrics(server_id, {
                        'cpu_usage': cpu_usage,
                        'memory_usage': memory_usage,
                        'response_time': response_time,
                        'error_rate': error_rate,
                        'request_rate': traffic_per_server
                    })
                
                time.sleep(10)
        
        def predictor_display():
            while True:
                prediction = self.predictor.predict_next_traffic()
                spike_detected = self.predictor.detect_spike(self.current_traffic)
                
                print(f"\n📊 Current Traffic: {self.current_traffic:.0f} req/s")
                print(f"🔮 Predicted Traffic: {prediction:.0f} req/s")
                print(f"🚨 Spike Detected: {spike_detected}")
                
                for server_id in self.config['servers']:
                    health = self.health_monitor.server_metrics[server_id]['health_score']
                    overloaded = self.health_monitor.is_server_overloaded(server_id)
                    risk = self.health_monitor.predict_overload_risk(server_id, prediction)
                    status = "❌ OVERLOADED" if overloaded else "✅ HEALTHY"
                    print(f"   {server_id}: Health={health:.1f}% Risk={risk.upper()} {status}")
                
                time.sleep(30)
        
        threading.Thread(target=traffic_simulator, daemon=True).start()
        threading.Thread(target=metrics_updater, daemon=True).start() 
        threading.Thread(target=predictor_display, daemon=True).start()
    
    def get_best_server(self):
        predicted_traffic = self.predictor.predict_next_traffic()
        
        healthy_servers = []
        for server_id in self.config['servers']:
            if not self.health_monitor.is_server_overloaded(server_id):
                risk = self.health_monitor.predict_overload_risk(server_id, predicted_traffic)
                if risk != "high":
                    healthy_servers.append(server_id)
        
        if not healthy_servers:
            return self.health_monitor.get_best_server()
        
        return random.choice(healthy_servers)

    def get_dashboard_data(self):
        """Get all data needed for the dashboard"""
        predicted_traffic = self.predictor.predict_next_traffic()
        spike_detected = self.predictor.detect_spike(self.current_traffic)
        
        # Count healthy servers
        healthy_count = 0
        for server_id in self.config['servers']:
            if not self.health_monitor.is_server_overloaded(server_id):
                healthy_count += 1
        
        # Prepare server data for UI
        servers_data = {}
        for server_id in self.config['servers']:
            server_metrics = self.health_monitor.server_metrics.get(server_id, {})
            risk_level = self.health_monitor.predict_overload_risk(server_id, predicted_traffic)
            
            servers_data[server_id] = {
                'cpu_usage': server_metrics.get('cpu_usage', 0),
                'memory_usage': server_metrics.get('memory_usage', 0),
                'response_time': server_metrics.get('response_time', 0),
                'error_rate': server_metrics.get('error_rate', 0),
                'health_score': server_metrics.get('health_score', 0),
                'risk_level': risk_level
            }
        
        return {
            'current_traffic': self.current_traffic,
            'predicted_traffic': predicted_traffic,
            'traffic_spike': spike_detected,
            'healthy_servers': healthy_count,
            'total_servers': len(self.config['servers']),
            'servers': servers_data
        }

# Create Flask app
app = Flask(__name__)
load_balancer = PredictiveLoadBalancer()

@app.route('/')
def home():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/dashboard_data')
def dashboard_data():
    """API endpoint for dashboard data"""
    data = load_balancer.get_dashboard_data()
    return jsonify(data)

@app.route('/route', methods=['GET'])
def route_request():
    best_server = load_balancer.get_best_server()
    
    if not best_server:
        return jsonify({'error': 'No healthy servers available'}), 503
    
    return jsonify({
        'server': best_server,
        'strategy': 'predictive_load_balancing',
        'current_traffic': load_balancer.current_traffic,
        'message': f'Request routed to {best_server}'
    })

@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(load_balancer.health_monitor.server_metrics)

@app.route('/predict', methods=['GET'])
def get_prediction():
    prediction = load_balancer.predictor.predict_next_traffic()
    spike = load_balancer.predictor.detect_spike(load_balancer.current_traffic)
    
    return jsonify({
        'current_traffic': load_balancer.current_traffic,
        'predicted_traffic': prediction,
        'traffic_spike_detected': spike
    })

@app.route('/simulate_spike', methods=['POST'])
def simulate_spike():
    """Simulate a traffic spike for testing"""
    load_balancer.current_traffic = random.randint(600, 900)
    return jsonify({
        'message': 'Traffic spike simulated',
        'new_traffic': load_balancer.current_traffic
    })

if __name__ == '__main__':
    print("🌟 Starting Predictive Load Balancer Server...")
    print("📡 Beautiful Dashboard available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True)
