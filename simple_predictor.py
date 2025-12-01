import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
import random

class SimpleTrafficPredictor:
    def __init__(self):
        print("🚀 Simple Traffic Predictor Started!")
        self.traffic_history = []
        self.max_history = 100
        
    def add_traffic_data(self, current_traffic):
        """Add current traffic data to history"""
        timestamp = datetime.now()
        self.traffic_history.append({
            'timestamp': timestamp,
            'traffic': current_traffic,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        })
        
        # Keep only recent history
        if len(self.traffic_history) > self.max_history:
            self.traffic_history.pop(0)
    
    def predict_next_traffic(self):
        """Simple prediction based on time patterns"""
        if len(self.traffic_history) < 10:
            return random.uniform(50, 150)  # Default prediction
            
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Simple pattern recognition
        recent_traffic = [item['traffic'] for item in self.traffic_history[-10:]]
        avg_recent = sum(recent_traffic) / len(recent_traffic)
        
        # Time-based adjustments
        if current_hour >= 9 and current_hour <= 17:  # Business hours
            prediction = avg_recent * 1.3
        elif current_hour >= 18 and current_hour <= 22:  # Evening peak
            prediction = avg_recent * 1.5
        else:  # Night time
            prediction = avg_recent * 0.7
            
        # Weekend adjustment
        if current_day >= 5:  # Weekend
            prediction = prediction * 0.8
            
        return max(10, prediction)  # Ensure positive value
    
    def detect_spike(self, current_traffic):
        """Detect if current traffic is unusually high"""
        if len(self.traffic_history) < 5:
            return False
            
        recent_avg = sum([item['traffic'] for item in self.traffic_history[-5:]]) / 5
        
        # If current traffic is 50% higher than recent average, it's a spike
        return current_traffic > recent_avg * 1.5