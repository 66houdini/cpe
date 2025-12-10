import csv
import json
import io
from typing import Dict, List
from datetime import datetime


class ExportService:
    """Service for exporting scenario data in various formats"""
    
    @staticmethod
    def export_scenario_to_csv(scenario: Dict) -> str:
        """
        Export a single scenario to CSV format
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write metadata
        writer.writerow(['Scenario Export'])
        writer.writerow(['Generated', datetime.utcnow().isoformat()])
        writer.writerow([])
        
        # Write scenario info
        writer.writerow(['Scenario Information'])
        writer.writerow(['ID', scenario.get('id', 'N/A')])
        writer.writerow(['Name', scenario.get('name', 'Unnamed')])
        writer.writerow(['Description', scenario.get('description', '')])
        writer.writerow(['Created', scenario.get('created_at', 'N/A')])
        writer.writerow([])
        
        # Write parameters
        writer.writerow(['Parameters'])
        writer.writerow(['Parameter', 'Value'])
        parameters = scenario.get('parameters', {})
        for key, value in parameters.items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Write results
        writer.writerow(['Results'])
        writer.writerow(['Metric', 'Value'])
        results = scenario.get('results', {})
        
        # Exclude uncertainties from main results
        for key, value in results.items():
            if key != 'uncertainties':
                writer.writerow([key, value])
        writer.writerow([])
        
        # Write uncertainties if available
        uncertainties = results.get('uncertainties', {})
        if uncertainties:
            writer.writerow(['Uncertainty Bands'])
            writer.writerow(['Metric', 'P10', 'P50', 'P90'])
            for metric, bands in uncertainties.items():
                writer.writerow([
                    metric,
                    bands.get('p10', ''),
                    bands.get('p50', ''),
                    bands.get('p90', '')
                ])
        
        return output.getvalue()
    
    @staticmethod
    def export_comparison_to_csv(scenarios: List[Dict]) -> str:
        """
        Export scenario comparison to CSV format
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Scenario Comparison'])
        writer.writerow(['Generated', datetime.utcnow().isoformat()])
        writer.writerow([])
        
        if not scenarios:
            writer.writerow(['No scenarios to compare'])
            return output.getvalue()
        
        # Write parameters comparison
        writer.writerow(['Parameters Comparison'])
        header = ['Parameter'] + [s.get('name', f"Scenario {s.get('id')}") for s in scenarios]
        writer.writerow(header)
        
        # Get all unique parameters
        all_params = set()
        for scenario in scenarios:
            all_params.update(scenario.get('parameters', {}).keys())
        
        for param in sorted(all_params):
            row = [param]
            for scenario in scenarios:
                row.append(scenario.get('parameters', {}).get(param, 'N/A'))
            writer.writerow(row)
        writer.writerow([])
        
        # Write results comparison
        writer.writerow(['Results Comparison'])
        header = ['Metric'] + [s.get('name', f"Scenario {s.get('id')}") for s in scenarios]
        writer.writerow(header)
        
        # Get all unique metrics
        all_metrics = set()
        for scenario in scenarios:
            results = scenario.get('results', {})
            all_metrics.update(k for k in results.keys() if k != 'uncertainties')
        
        for metric in sorted(all_metrics):
            row = [metric]
            for scenario in scenarios:
                row.append(scenario.get('results', {}).get(metric, 'N/A'))
            writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def export_sensitivity_to_csv(sensitivity_data: Dict) -> str:
        """
        Export sensitivity analysis to CSV format
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Sensitivity Analysis'])
        writer.writerow(['Generated', datetime.utcnow().isoformat()])
        writer.writerow([])
        
        # Write baseline
        baseline = sensitivity_data.get('baseline', {})
        writer.writerow(['Baseline Parameters'])
        for key, value in baseline.get('parameters', {}).items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Write analysis for each parameter
        analysis = sensitivity_data.get('analysis', {})
        for param_name, param_data in analysis.items():
            writer.writerow([f'Sensitivity Analysis: {param_name}'])
            writer.writerow([])
            
            # Write variations
            variations = param_data.get('variations', [])
            if variations:
                # Get metrics from first variation
                first_results = variations[0].get('results', {})
                metrics = [k for k in first_results.keys() if k != 'uncertainties']
                
                # Header
                header = ['Parameter Value'] + metrics
                writer.writerow(header)
                
                # Data rows
                for variation in variations:
                    row = [variation.get('parameter_value', '')]
                    results = variation.get('results', {})
                    for metric in metrics:
                        row.append(results.get(metric, ''))
                    writer.writerow(row)
            
            writer.writerow([])
            
            # Write sensitivity scores
            scores = param_data.get('sensitivity_scores', {})
            if scores:
                writer.writerow(['Sensitivity Scores'])
                writer.writerow(['Metric', 'Sensitivity', 'Min', 'Max', 'Range'])
                for metric, score_data in scores.items():
                    writer.writerow([
                        metric,
                        score_data.get('sensitivity', ''),
                        score_data.get('min', ''),
                        score_data.get('max', ''),
                        score_data.get('range', '')
                    ])
            
            writer.writerow([])
            writer.writerow([])
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(data: Dict, pretty: bool = True) -> str:
        """
        Export data to JSON format
        
        Args:
            data: Data to export
            pretty: Whether to pretty-print the JSON
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(data, indent=2, default=str)
        else:
            return json.dumps(data, default=str)
    
    @staticmethod
    def create_summary_report(scenario: Dict) -> str:
        """
        Create a text summary report of a scenario
        
        Returns:
            Formatted text string
        """
        report = []
        report.append("=" * 60)
        report.append("SCENARIO SUMMARY REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Basic info
        report.append(f"Name: {scenario.get('name', 'Unnamed')}")
        report.append(f"ID: {scenario.get('id', 'N/A')}")
        report.append(f"Created: {scenario.get('created_at', 'N/A')}")
        report.append(f"Description: {scenario.get('description', 'No description')}")
        report.append("")
        
        # Parameters
        report.append("-" * 60)
        report.append("POLICY PARAMETERS")
        report.append("-" * 60)
        parameters = scenario.get('parameters', {})
        for key, value in parameters.items():
            readable_key = key.replace('_', ' ').title()
            report.append(f"  {readable_key}: {value:.3f}")
        report.append("")
        
        # Results
        report.append("-" * 60)
        report.append("OUTCOMES")
        report.append("-" * 60)
        results = scenario.get('results', {})
        
        key_metrics = [
            ('food_production', 'Food Production'),
            ('co2_emissions', 'CO2 Emissions'),
            ('water_demand', 'Water Demand'),
            ('water_stress_index', 'Water Stress Index'),
            ('food_security_index', 'Food Security Index'),
            ('sustainability_score', 'Sustainability Score')
        ]
        
        for key, label in key_metrics:
            if key in results:
                value = results[key]
                report.append(f"  {label}: {value:.2f}")
        
        report.append("")
        
        # Sustainability assessment
        report.append("-" * 60)
        report.append("SUSTAINABILITY ASSESSMENT")
        report.append("-" * 60)
        
        sustainability_score = results.get('sustainability_score', 0)
        if sustainability_score >= 0.7:
            assessment = "EXCELLENT - High sustainability across all metrics"
        elif sustainability_score >= 0.5:
            assessment = "GOOD - Moderate sustainability with room for improvement"
        elif sustainability_score >= 0.3:
            assessment = "FAIR - Significant sustainability challenges"
        else:
            assessment = "POOR - Major sustainability concerns"
        
        report.append(f"  Overall: {assessment}")
        report.append(f"  Score: {sustainability_score:.3f}/1.000")
        report.append("")
        
        report.append("=" * 60)
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("=" * 60)
        
        return "\n".join(report)
