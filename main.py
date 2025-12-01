from load_balancer import app

if __name__ == '__main__':
    print("🎯 Starting Predictive Load Balancer...")
    print("📍 Access the dashboard at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True)