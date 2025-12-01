import json
import random
from datetime import datetime
#Created a class to monitor server health and predict overload risks.
class ServerHealthMonitor:
    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.server_metrics = {}
        print("🏥 Server Health Monitor Started!")
        
    def update_server_metrics(self, server_id, metrics):
        """Update metrics for a specific server"""
        self.server_metrics[server_id] = {
            **metrics,
            'last_update': datetime.now(),
            'health_score': self.calculate_health_score(metrics)
        }
    
    def calculate_health_score(self, metrics):
        """Calculate a simple health score (0-100)"""
        scores = []
        
        # CPU Score (lower usage = better)
        cpu_score = max(0, 100 - (metrics.get('cpu_usage', 0) * 100))
        scores.append(cpu_score)
        
        # Memory Score
        memory_score = max(0, 100 - (metrics.get('memory_usage', 0) * 100))
        scores.append(memory_score)
        
        # Response Time Score (faster = better)
        response_time = metrics.get('response_time', 0)
        response_score = max(0, 100 - (response_time * 10))  # 0.1s = 99, 1s = 90, 10s = 0
        scores.append(response_score)
        
        # Error Rate Score
        error_rate = metrics.get('error_rate', 0)
        error_score = max(0, 100 - (error_rate * 1000))  # 0.01 = 90, 0.1 = 0
        scores.append(error_score)
        
        # Average the scores
        avg_score = sum(scores) / len(scores)
        return avg_score
    
    def get_best_server(self):
        """Get the healthiest server"""
        if not self.server_metrics:
            return None
            
        # Find server with highest health score
        best_server = max(self.server_metrics.items(), key=lambda x: x[1]['health_score'])
        return best_server[0]  # Return server ID
    
    def is_server_overloaded(self, server_id):
        """Check if a server is overloaded"""
        if server_id not in self.server_metrics:
            return True  # If we don't know, assume it's bad
            
        metrics = self.server_metrics[server_id]
        
        # Check thresholds from config
        thresholds = self.config['overload_thresholds']
        if (metrics.get('cpu_usage', 0) > thresholds['cpu_usage'] or
            metrics.get('memory_usage', 0) > thresholds['memory_usage'] or
            metrics.get('response_time', 0) > thresholds['response_time'] or
            metrics.get('error_rate', 0) > thresholds['error_rate']):
            return True
            
        return False
    
    def predict_overload_risk(self, server_id, predicted_traffic):
        """Simple overload risk prediction"""
        if server_id not in self.server_metrics:
            return "unknown"
            
        current_metrics = self.server_metrics[server_id]
        current_traffic = current_metrics.get('request_rate', 1)
        
        # Simple calculation: if predicted traffic is much higher, risk is high
        traffic_increase = predicted_traffic / max(1, current_traffic)
        
        if traffic_increase > 2.0:
            return "high"
        elif traffic_increase > 1.5:
            return "medium"
        else:
            return "low"
