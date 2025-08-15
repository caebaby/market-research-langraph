# team_icp/prompts/gtm_blueprint_prompts.py

class GTMBlueprintPrompts:
    """Prompts for the GTM Blueprint synthesis agent"""
    
    @staticmethod
    def get_role_prompt():
        """Elite GTM strategist role that synthesizes all insights"""
        return """You are an elite Go-to-Market strategist who synthesizes deep customer insights into comprehensive, executable market entry strategies.

Your expertise spans:
- Strategic positioning and differentiation
- Product-market fit optimization
- Messaging architecture and narrative design
- Channel strategy and distribution models
- Pricing psychology and monetization
- Sales enablement and conversion optimization
- Growth mechanics and scaling strategies
- Competitive positioning and market entry timing

SYNTHESIS MASTERY:
You excel at weaving together insights from multiple sources:
- Psychological analysis → Product positioning
- Voice of customer → Messaging and copy
- Interview insights → Sales enablement
- Competitive intelligence → Differentiation strategy

You create strategies that are:
1. **Psychologically Grounded**: Based on deep human understanding
2. **Voice-Authentic**: Using actual customer language
3. **Competition-Aware**: Positioned to win
4. **Execution-Ready**: With clear next steps
5. **Measurable**: With success metrics

Your GTM blueprints become the north star for entire organizations."""

    @staticmethod
    def get_synthesis_template():
        """Template for comprehensive GTM blueprint"""
        return """Based on all agent insights, create a comprehensive GTM Blueprint.

AVAILABLE INSIGHTS:
{all_insights}

TASK: {task}
BUSINESS CONTEXT: {business_context}

Create a COMPREHENSIVE GTM BLUEPRINT (2500+ words) with these sections:

# 🎯 EXECUTIVE SUMMARY
- The big opportunity (2-3 sentences)
- Why now (market timing)
- Our unique advantage
- Expected outcomes

# 🧠 PART 1: CUSTOMER TRUTH FOUNDATION

## Deep Customer Psychology
Synthesize psychological insights into actionable understanding:
- Core identity and self-perception
- Hidden fears and desires
- Psychological triggers for action
- Decision-making patterns

## Voice of Customer Insights
From actual customer language:
- How they describe their problem
- Words they use about solutions
- Emotional language patterns
- Trust signals they seek

# 🎭 PART 2: STRATEGIC POSITIONING

## Market Position Statement
- What we are (and are not)
- Who we serve (and don't serve)
- Problem we solve uniquely
- Our philosophical stance

## Competitive Differentiation
Based on competitor analysis:
- Where competitors can't go
- Capabilities they lack
- Positions they've abandoned
- Our wedge into the market

## Messaging Architecture
Three-layer messaging:
1. **Hook** (attention): The pattern interrupt
2. **Heart** (emotion): The visceral connection
3. **Head** (logic): The rational justification

# 🚀 PART 3: GO-TO-MARKET MECHANICS

## Launch Sequence Strategy
Phase 1 (Months 1-3): Foundation
- Initial positioning test
- Core message validation
- Early adopter acquisition
- Proof point development

Phase 2 (Months 4-6): Amplification
- Channel expansion
- Message optimization
- Social proof building
- Competitive response

Phase 3 (Months 7-12): Scale
- Market education
- Category creation/redefinition
- Partnership activation
- Geographic/segment expansion

## Channel Strategy
Primary Channels:
- [Channel 1]: Why, how, expected ROI
- [Channel 2]: Why, how, expected ROI
- [Channel 3]: Why, how, expected ROI

## Pricing & Monetization
- Pricing model and psychology
- Value metric alignment
- Competitive pricing position
- Expansion revenue strategy

# 💰 PART 4: SALES ENABLEMENT

## Sales Narrative Arc
Based on interview insights:
1. Problem Agitation
2. Failed Alternative Framing
3. New Approach Introduction
4. Proof and Validation
5. Vision of Success

## Objection Handling Framework
Top 5 objections and responses:
[Use insights from sales interviews]

## Conversion Optimization
- Trial/demo strategy
- Proof of value moments
- Decision acceleration tactics
- Champion building approach

# 📊 PART 5: METRICS & SCALING

## Success Metrics
Leading Indicators:
- [Metric 1]: Target and why
- [Metric 2]: Target and why
- [Metric 3]: Target and why

Lagging Indicators:
- [Metric 1]: Target and timeline
- [Metric 2]: Target and timeline

## Scaling Triggers
When to accelerate:
- Signal 1: [Specific metric/event]
- Signal 2: [Specific metric/event]
- Signal 3: [Specific metric/event]

## Risk Mitigation
Top 3 risks and mitigation:
1. [Risk]: [Mitigation strategy]
2. [Risk]: [Mitigation strategy]
3. [Risk]: [Mitigation strategy]

# 🎬 PART 6: 90-DAY EXECUTION PLAN

## Days 1-30: Foundation
Specific actions:
- [ ] Action item with owner
- [ ] Action item with owner
- [ ] Action item with owner

## Days 31-60: Validation
Specific actions:
- [ ] Action item with owner
- [ ] Action item with owner
- [ ] Action item with owner

## Days 61-90: Acceleration
Specific actions:
- [ ] Action item with owner
- [ ] Action item with owner
- [ ] Action item with owner

# 🔑 KEY TAKEAWAYS

## The One Thing
If you remember nothing else: [Single most important insight]

## Quick Wins
Three things to do tomorrow:
1. [Immediate action]
2. [Immediate action]
3. [Immediate action]

## Long-term Vision
Where this positions us in 3 years: [Vision statement]

---

Ensure the blueprint is:
- **Comprehensive**: 2500+ words of strategic depth
- **Specific**: Names, numbers, and concrete examples
- **Actionable**: Clear next steps and owners
- **Grounded**: Built on all agent insights
- **Inspiring**: Creates excitement and buy-in"""

    @staticmethod
    def get_quality_criteria():
        """Criteria for evaluating GTM blueprint quality"""
        return """Evaluate this GTM Blueprint on strategic excellence:

1. **Synthesis Quality (0-1)**: How well does it integrate insights from all agents?
2. **Strategic Coherence (0-1)**: Does everything connect into a unified strategy?
3. **Execution Clarity (0-1)**: Are next steps specific and actionable?
4. **Differentiation Power (0-1)**: Will this create a unique market position?
5. **Psychological Grounding (0-1)**: Is it based on deep customer understanding?
6. **Completeness (0-1)**: Does it cover all critical GTM elements?
7. **Innovation (0-1)**: Does it propose non-obvious strategies?

Consider:
- Would an executive team rally around this?
- Can a sales team execute on this?
- Will this actually win in the market?
- Is this better than what competitors would create?

Provide detailed critique, then a final score 0.0-1.0."""