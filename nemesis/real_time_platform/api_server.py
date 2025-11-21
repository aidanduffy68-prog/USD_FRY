"""
Real-Time Threat Intelligence Platform API
WebSocket and REST API for real-time threat intelligence delivery

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from nemesis.compilation_engine import ABCCompilationEngine, CompiledIntelligence
from nemesis.signal_intake.federal_ai_monitor import FederalAIMonitor, monitor_federal_ai_systems


app = Flask(__name__)
app.config['SECRET_KEY'] = 'gh-systems-abc-platform'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize engines
compilation_engine = ABCCompilationEngine()
federal_monitor = FederalAIMonitor()


# REST API Endpoints

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/v1/compile', methods=['POST'])
def compile_intelligence():
    """
    Compile intelligence through Hades → Echo → Nemesis pipeline
    
    Request body:
    {
        "actor_id": "lazarus_001",
        "actor_name": "Lazarus Group",
        "raw_intelligence": [...],
        "transaction_data": [...],
        "network_data": {...}
    }
    """
    try:
        data = request.json or {}
        
        actor_id = data.get('actor_id')
        actor_name = data.get('actor_name', actor_id)
        raw_intelligence = data.get('raw_intelligence', [])
        transaction_data = data.get('transaction_data')
        network_data = data.get('network_data')
        
        if not actor_id:
            return jsonify({"error": "actor_id is required"}), 400
        
        # Compile intelligence
        compiled = compilation_engine.compile_intelligence(
            actor_id=actor_id,
            actor_name=actor_name,
            raw_intelligence=raw_intelligence,
            transaction_data=transaction_data,
            network_data=network_data,
            generate_receipt=True
        )
        
        # Emit real-time update via WebSocket
        socketio.emit('intelligence_compiled', {
            "compilation_id": compiled.compilation_id,
            "actor_id": compiled.actor_id,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "timestamp": compiled.compiled_at.isoformat()
        })
        
        # Return compiled intelligence
        return jsonify({
            "status": "success",
            "compilation_id": compiled.compilation_id,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "targeting_package": compiled.targeting_package,
            "receipt": compiled.targeting_package.get("receipt")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/federal-ai/scan', methods=['POST'])
def scan_federal_ai():
    """
    Scan federal AI systems for vulnerabilities
    
    Request body (optional):
    {
        "agencies": ["NASA", "DoD", "DHS"]  # If not provided, scans all
    }
    """
    try:
        data = request.json or {}
        agencies = data.get('agencies', ['NASA', 'DoD', 'DHS'])
        
        systems = []
        if 'NASA' in agencies:
            systems.extend(federal_monitor.scan_nasa_systems())
        if 'DoD' in agencies:
            systems.extend(federal_monitor.scan_dod_systems())
        if 'DHS' in agencies:
            systems.extend(federal_monitor.scan_dhs_systems())
        
        # Extract vulnerabilities
        vulnerabilities = federal_monitor.extract_vulnerabilities(systems)
        
        # Generate intelligence feed
        intelligence_feed = federal_monitor.generate_intelligence_feed(systems)
        
        # Emit real-time update
        socketio.emit('federal_ai_scan_complete', {
            "systems_scanned": len(systems),
            "vulnerabilities_found": len(vulnerabilities),
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "status": "success",
            "systems_scanned": len(systems),
            "vulnerabilities_found": len(vulnerabilities),
            "systems": [
                {
                    "agency": s.agency,
                    "system_name": s.system_name,
                    "system_type": s.system_type,
                    "vulnerability_count": len(s.vulnerabilities)
                }
                for s in systems
            ],
            "vulnerabilities": [
                {
                    "vulnerability_id": v.vulnerability_id,
                    "system_id": v.system_id,
                    "type": v.vulnerability_type,
                    "severity": v.severity,
                    "confidence": v.confidence
                }
                for v in vulnerabilities
            ],
            "intelligence_feed": intelligence_feed
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/federal-ai/compile', methods=['POST'])
def compile_federal_ai_intelligence():
    """
    Compile federal AI security intelligence
    
    Request body:
    {
        "target_agency": "NASA",
        "ai_system_data": {...},
        "vulnerability_data": [...]
    }
    """
    try:
        data = request.json or {}
        
        target_agency = data.get('target_agency')
        ai_system_data = data.get('ai_system_data', {})
        vulnerability_data = data.get('vulnerability_data', [])
        
        if not target_agency:
            return jsonify({"error": "target_agency is required"}), 400
        
        # Compile federal AI intelligence
        compiled = compilation_engine.compile_federal_ai_intelligence(
            target_agency=target_agency,
            ai_system_data=ai_system_data,
            vulnerability_data=vulnerability_data,
            generate_receipt=True
        )
        
        # Emit real-time update
        socketio.emit('federal_ai_intelligence_compiled', {
            "compilation_id": compiled.compilation_id,
            "target_agency": target_agency,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "timestamp": compiled.compiled_at.isoformat()
        })
        
        return jsonify({
            "status": "success",
            "compilation_id": compiled.compilation_id,
            "target_agency": target_agency,
            "compilation_time_ms": compiled.compilation_time_ms,
            "confidence_score": compiled.confidence_score,
            "targeting_package": compiled.targeting_package,
            "receipt": compiled.targeting_package.get("receipt")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to ABC Real-Time Platform'})
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to real-time updates"""
    subscription_type = data.get('type', 'all')  # all, federal_ai, specific_actor
    emit('subscribed', {'type': subscription_type})


if __name__ == '__main__':
    print("Starting ABC Real-Time Threat Intelligence Platform...")
    print("API: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

