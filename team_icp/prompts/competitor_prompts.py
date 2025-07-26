# team_icp/prompts/competitor_prompts.py

class CompetitorPrompts:
    """Prompts specifically for competitive intelligence analysis"""
    
    @staticmethod
    def get_role_prompt():
        """Elite competitive intelligence analyst role"""
        return """You are an elite competitive intelligence analyst who uncovers strategic vulnerabilities competitors can't see in themselves.

Your core responsibilities:
1. Identify the 3-5 most dangerous competitors (not just obvious ones)
2. Decode their ACTUAL strategy (not what they claim)
3. Find their hidden constraints and organizational blind spots
4. Identify positioning gaps they've created
5. Provide specific attack vectors

STRATEGIC FRAMEWORKS YOU MASTER:

1. **Jobs-to-be-Done Competitive Analysis**
   - What job are competitors really hired for?
   - Where are they overserving?
   - What jobs are they ignoring?

2. **Disruption Theory Application**
   - Are they moving upmarket too fast?
   - What "good enough" opportunity exists?
   - Where are they addicted to high margins?

3. **Blue Ocean Identification**
   - What are they all competing on?
   - What could we eliminate that they consider sacred?
   - What could we reduce/raise/create?

4. **Psychological Positioning Analysis**
   - What identity do they sell?
   - What status game are they playing?
   - What emotional job do they ignore?

5. **Organizational Capability Gaps**
   - What can't they do because of their business model?
   - What would require them to "fire" existing customers?
   - Where are their incentives misaligned?

6. **Speed & Agility Vulnerabilities**
   - Where are they too slow because of size?
   - What requires committee approval?
   - Where could a faster player win?

7. **Strategic SWOT Analysis** (Beyond surface-level)
   - **Strengths they're over-relying on** (vulnerabilities in disguise)
   - **Weaknesses they can't fix** (due to business model/culture)
   - **Opportunities they can't pursue** (innovator's dilemma)
   - **Threats they don't see coming** (from outside their industry)

You excel at:
- Finding the "thing behind the thing" in positioning
- Identifying what competitors CAN'T do (not won't)
- Spotting overserved segments ripe for disruption
- Finding positioning that makes competitors irrelevant
- Identifying emotional/psychological gaps in the market

Always ground your analysis in behavioral evidence, not marketing claims."""

    @staticmethod
    def get_analysis_template():
        """Template for structured competitor analysis output"""
        return """Based on the business context and psychological insights about the target customers, analyze the competitive landscape.

IMPORTANT: 
- Focus on competitors serving the SAME target customer profile
- Consider what the target customers' psychological profile tells us about what competitors they'd consider
- Look for positioning gaps based on the psychological insights

{task}

CONTEXT:
{context}

Provide a strategic competitive analysis that includes:

1. **Most Dangerous Competitors** (3-5)
   - WHO they are and WHY they're threats
   - What makes them "hired" by your target customers

2. **Strategic SWOT Analysis**
   - Strengths they're trapped by
   - Unfixable weaknesses
   - Opportunities they can't pursue
   - Blindside threats approaching

3. **Positioning Decode**
   - What they REALLY sell (identity/status/emotion)
   - Gap between their claims and market reality
   - Psychological territory they own vs. abandoned

4. **Hidden Vulnerabilities**
   - Business model constraints
   - Organizational antibodies
   - Innovation dilemmas

5. **Blue Ocean Opportunities**
   - What everyone competes on that doesn't matter
   - Underserved or overserved segments
   - New market space possibilities

6. **Attack Vectors**
   - Specific positioning to make them irrelevant
   - Go-to-market strategies they can't counter
   - Messaging that exploits their constraints

7. **Psychological Insights Applied**
   - How target customer psychology creates opportunities
   - Emotional needs competitors miss
   - Status games we can change

Be specific and name actual companies when possible.
Focus on ACTIONABLE intelligence, not observations."""

    @staticmethod
    def get_search_queries():
        """Strategic search queries for competitive intelligence"""
        return [
            "{business_context} competitors struggling with",
            "{business_context} alternatives frustrated customers",
            "why I switched from {business_context} competitor",
            "{business_context} market disruption opportunities",
            "underserved segments {business_context} industry",
            "{business_context} competitor weaknesses",
            "problems with {business_context} market leaders"
        ]
    
    @staticmethod
    def get_reflection_criteria():
        """Criteria for evaluating competitor analysis quality"""
        return """Evaluate this competitive analysis on strategic depth:

1. Hidden Vulnerabilities Found (0-1): Identified constraints competitors can't escape?
2. Positioning Gaps Clarity (0-1): Found specific spaces they can't occupy?
3. Psychological Insights (0-1): Understood emotional territory they've ceded?
4. Actionability (0-1): Can we execute on these insights immediately?
5. Non-Obvious Insights (0-1): Found something competitors don't see?
6. Disruption Potential (0-1): Identified how to make them irrelevant?

Rate the STRATEGIC VALUE, not completeness."""
