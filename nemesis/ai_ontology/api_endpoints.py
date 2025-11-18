"""
API Endpoints for AI-Powered Threat Intelligence
RESTful API for accessing ABC AI ontology capabilities
"""

from typing import List, Dict, Any, Optional
from dataclasses import asdict
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Fix imports to work both as module and standalone script
# When run as module: use relative imports
# When run as script (Docker): use ai_ontology.* imports (PYTHONPATH=/app)
# When run locally: try relative, fall back to direct imports
try:
    from .integration_layer import ABCIntegrationLayer
    from .natural_language_interface import NaturalLanguageInterface
    from .threat_dossier_generator import ThreatDossierGenerator
except ImportError:
    # Running as standalone script - try absolute imports
    try:
        from ai_ontology.integration_layer import ABCIntegrationLayer
        from ai_ontology.natural_language_interface import NaturalLanguageInterface
        from ai_ontology.threat_dossier_generator import ThreatDossierGenerator
    except ImportError:
        # Last resort: direct imports (when running from same directory)
        from integration_layer import ABCIntegrationLayer
        from natural_language_interface import NaturalLanguageInterface
        from threat_dossier_generator import ThreatDossierGenerator

app = Flask(__name__)
CORS(app)

# Initialize integration layer (with error handling)
try:
    abc = ABCIntegrationLayer()
    nl_interface = NaturalLanguageInterface()
    dossier_gen = ThreatDossierGenerator()
except Exception as e:
    # Log initialization error but allow server to start
    print(f"Warning: Failed to initialize some components: {e}")
    abc = None
    nl_interface = None
    dossier_gen = None


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "GH Systems ABC AI Ontology",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/intelligence/process', methods=['POST'])
def process_intelligence():
    """
    Process raw intelligence through AI pipeline
    
    Request body:
    {
        "intelligence": [
            {"text": "Lazarus Group activity detected...", "source": "twitter"},
            ...
        ],
        "transaction_data": [...] (optional)
    }
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400
    
    data = request.json or {}
    intelligence = data.get('intelligence', [])
    transaction_data = data.get('transaction_data')
    
    if not intelligence:
        return jsonify({
            "status": "error",
            "message": "intelligence field is required"
        }), 400
    
    if abc is None:
        return jsonify({
            "status": "error",
            "message": "Integration layer not initialized"
        }), 500
    
    try:
        result = abc.process_intelligence_feed(intelligence, transaction_data)
        return jsonify({
            "status": "success",
            "result": result
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/actors/<actor_id>/targeting-package', methods=['GET'])
def get_targeting_package(actor_id: str):
    """
    Generate targeting package for an actor
    
    Query params:
    - include_dossier: boolean (default: false)
    """
    include_dossier = request.args.get('include_dossier', 'false').lower() == 'true'
    
    if abc is None:
        return jsonify({
            "status": "error",
            "message": "Integration layer not initialized"
        }), 500
    
    # This would normally fetch from database
    # For now, return structure
    try:
        # Mock intelligence package (would come from database)
        intelligence_package = {
            "behavioral_signatures": {},
            "threat_forecasts": {}
        }
        
        package = abc.generate_targeting_package(actor_id, intelligence_package)
        
        if not include_dossier and 'dossier' in package:
            package.pop('dossier', None)
        
        return jsonify({
            "status": "success",
            "package": package
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/query', methods=['POST'])
def natural_language_query():
    """
    Process natural language query
    
    Request body:
    {
        "query": "Who is coordinating with Lazarus Group?",
        "user": "analyst_123" (optional)
    }
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400
    
    data = request.json or {}
    query = data.get('query')
    user = data.get('user')
    
    if not query:
        return jsonify({
            "status": "error",
            "message": "Query is required"
        }), 400
    
    if abc is None:
        return jsonify({
            "status": "error",
            "message": "Integration layer not initialized"
        }), 500
    
    try:
        result = abc.query_natural_language(query, user)
        return jsonify({
            "status": "success",
            "result": result
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/actors/<actor_id>/dossier', methods=['GET'])
def get_threat_dossier(actor_id: str):
    """
    Generate threat dossier for an actor
    
    Query params:
    - format: "json" or "markdown" (default: json)
    """
    format_type = request.args.get('format', 'json').lower()
    
    if dossier_gen is None:
        return jsonify({
            "status": "error",
            "message": "Dossier generator not initialized"
        }), 500
    
    try:
        # Mock data (would come from database)
        dossier = dossier_gen.generate_dossier(
            actor_id=actor_id,
            actor_name=f"Actor_{actor_id}",
            behavioral_signature={},
            network_data={},
            threat_forecast={},
            transaction_history=[],
            historical_patterns=None
        )
        
        if format_type == 'markdown':
            markdown = dossier_gen.export_dossier_markdown(dossier)
            return markdown, 200, {'Content-Type': 'text/markdown'}
        else:
            return jsonify({
                "status": "success",
                "dossier": asdict(dossier)
            }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/feedback', methods=['POST'])
def record_feedback():
    """
    Record feedback for continuous learning
    
    Request body:
    {
        "feedback_type": "true_positive",
        "entity_id": "actor_123",
        "actual_outcome": {...},
        "predicted_outcome": {...} (optional)
    }
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400
    
    data = request.json or {}
    feedback_type = data.get('feedback_type')
    entity_id = data.get('entity_id')
    actual_outcome = data.get('actual_outcome')
    predicted_outcome = data.get('predicted_outcome')
    
    if not all([feedback_type, entity_id, actual_outcome]):
        return jsonify({
            "status": "error",
            "message": "feedback_type, entity_id, and actual_outcome are required"
        }), 400
    
    if abc is None:
        return jsonify({
            "status": "error",
            "message": "Integration layer not initialized"
        }), 500
    
    try:
        feedback = abc.record_feedback(
            feedback_type=feedback_type,
            entity_id=entity_id,
            actual_outcome=actual_outcome,
            predicted_outcome=predicted_outcome
        )
        return jsonify({
            "status": "success",
            "feedback": asdict(feedback)
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/v1/learning/report', methods=['GET'])
def get_learning_report():
    """Get continuous learning performance report"""
    if abc is None or not hasattr(abc, 'learning_system'):
        return jsonify({
            "status": "error",
            "message": "Learning system not available"
        }), 500
    
    try:
        report = abc.learning_system.generate_learning_report()
        return jsonify({
            "status": "success",
            "report": report
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

