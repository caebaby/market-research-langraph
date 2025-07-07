# agents/learning_memory.py

class LearningMemorySystem:
    """Manages agent learning while preventing session contamination"""
    
    def __init__(self):
        self.framework_improvements = []
        self.industry_patterns = {}
        self.technique_refinements = []
        self.quality_insights = []
    
    def extract_learning_patterns(self, session_result):
        """Extract learning without business-specific content"""
        learning = {
            "framework_effectiveness": self._analyze_framework_performance(session_result),
            "industry_expertise": self._extract_industry_patterns(session_result),
            "technique_improvements": self._identify_technique_refinements(session_result),
            "quality_factors": self._analyze_quality_drivers(session_result)
        }
        
        # Store learning patterns (no specific business context)
        self._update_learning_memory(learning)
        return learning
    
    def get_learning_context_for_industry(self, industry):
        """Provide accumulated expertise for specific industry"""
        return {
            "framework_best_practices": self._get_framework_expertise(),
            "industry_specific_patterns": self.industry_patterns.get(industry, {}),
            "proven_techniques": self._get_proven_techniques(),
            "quality_optimization": self._get_quality_insights()
        }
    
    def _analyze_framework_performance(self, result):
        """Learn which frameworks work best for different scenarios"""
        return {
            "jungian_effectiveness": result.get("jungian_insights_quality", 0),
            "lab_profile_accuracy": result.get("lab_analysis_confidence", 0),
            "jtbd_depth": result.get("jtbd_insight_depth", 0),
            "voc_authenticity": result.get("voice_authenticity_score", 0)
        }
    
    def _extract_industry_patterns(self, result):
        """Learn industry-specific psychological patterns (without business details)"""
        industry = result.get("industry_context", "unknown")
        
        patterns = {
            "common_archetypes": result.get("dominant_archetypes", []),
            "typical_pain_categories": result.get("pain_pattern_types", []),
            "decision_making_styles": result.get("decision_patterns", []),
            "language_pattern_types": result.get("communication_styles", [])
        }
        
        # Store as industry expertise, not specific business context
        if industry not in self.industry_patterns:
            self.industry_patterns[industry] = {"patterns": [], "confidence": 0}
        
        self.industry_patterns[industry]["patterns"].append(patterns)
        self.industry_patterns[industry]["confidence"] += 1
        
        return patterns
    
    def _identify_technique_refinements(self, result):
        """Learn which analysis techniques produce better insights"""
        return {
            "depth_techniques": [
                "Multi-layer pain analysis works better than single-level",
                "Contradiction testing improves insight accuracy",
                "Voice authenticity validation catches AI-like language"
            ],
            "framework_sequences": [
                "Start with Jungian for identity foundation",
                "Apply LAB profiles for communication style",
                "Use JTBD for purchase psychology",
                "Layer cognitive biases for decision shortcuts"
            ]
        }
    
    def _analyze_quality_drivers(self, result):
        """Learn what makes insights more authentic and actionable"""
        return {
            "authenticity_drivers": [
                "Specific examples increase believability",
                "Emotional language captures real voice",
                "Industry terminology builds credibility"
            ],
            "insight_depth_factors": [
                "Contradiction analysis reveals hidden motivations",
                "Multi-framework overlap validates insights",
                "Voice pattern consistency indicates accuracy"
            ]
        }
    
    def _get_framework_expertise(self):
        """Return accumulated framework application expertise"""
        return {
            "proven_analysis_sequences": [
                "Start with Jungian archetypes for identity foundation",
                "Apply LAB profiles for communication preferences", 
                "Use JTBD for purchase psychology",
                "Layer cognitive biases for decision shortcuts"
            ],
            "depth_techniques": [
                "Contradiction testing for insight validation",
                "Multi-layer pain analysis (surface → hidden → denied)",
                "Voice authenticity validation through pattern matching"
            ],
            "quality_drivers": [
                "Specific examples increase authenticity",
                "Emotional language captures real voice",
                "Industry-specific terminology builds credibility"
            ]
        }
    
    def _get_proven_techniques(self):
        """Return techniques proven to work across sessions"""
        return [
            "Identity contradiction analysis reveals core psychology",
            "Pain archaeology uncovers deeper motivations",
            "Voice pattern mapping ensures authentic language",
            "Framework triangulation validates insights"
        ]
    
    def _get_quality_insights(self):
        """Return insights about what drives higher quality output"""
        return {
            "high_quality_indicators": [
                "Client reaction: 'How did you know that?'",
                "Specific voice examples that feel real",
                "Insights that connect multiple frameworks",
                "Actionable recommendations with psychology backing"
            ],
            "common_quality_issues": [
                "Generic insights that could apply to anyone",
                "AI-sounding language patterns",
                "Surface-level analysis without depth",
                "Recommendations without psychological foundation"
            ]
        }
    
    def _update_learning_memory(self, learning):
        """Update memory with new learning patterns"""
        self.framework_improvements.append(learning["framework_effectiveness"])
        self.technique_refinements.append(learning["technique_improvements"])
        self.quality_insights.append(learning["quality_factors"])
        
        # Note: This is simplified - in production you'd want persistent storage
