#!/usr/bin/env python3
"""
Test script for Geopolitical Alpha module
Verifies all components work together without sending actual briefings
"""

import sys
import json
from pathlib import Path

# Add to path
sys.path.append('/home/ubuntu/clawd/intelligence-briefing')

def test_collector():
    """Test geopolitical event collection."""
    print("=" * 60)
    print("TEST 1: Geopolitical Event Collector")
    print("=" * 60)
    
    from collectors.collect_geopolitical_simple import collect_geopolitical_events
    
    result = collect_geopolitical_events()
    
    assert result['status'] == 'success', "Collector failed"
    assert len(result['events']) > 0, "No events collected"
    
    print(f"✅ Collected {len(result['events'])} events")
    print(f"   Categories: {set(e['category'] for e in result['events'])}")
    
    return result

def test_analyzer(events_data):
    """Test geopolitical alpha analysis."""
    print("\n" + "=" * 60)
    print("TEST 2: Geopolitical Alpha Analysis")
    print("=" * 60)
    
    from analysis.geopolitical_alpha import analyze_geopolitical_alpha
    
    result = analyze_geopolitical_alpha(events_data)
    
    assert result['status'] == 'success', "Analysis failed"
    assert len(result['chains']) > 0, "No chains generated"
    
    print(f"✅ Generated {len(result['chains'])} transmission chains")
    print(f"   High conviction: {result['summary']['high_conviction']}")
    print(f"   Medium conviction: {result['summary']['medium_conviction']}")
    
    # Verify chain structure
    chain = result['chains'][0]
    assert 'event' in chain, "Missing event in chain"
    assert 'affected_assets' in chain, "Missing affected_assets"
    assert 'historical_parallel' in chain, "Missing historical_parallel"
    assert 'teaching_note' in chain, "Missing teaching_note"
    assert 'conviction_score' in chain, "Missing conviction_score"
    
    print(f"\n   Sample chain: {chain['event'][:60]}...")
    print(f"   Affected assets: {len(chain['affected_assets'])}")
    print(f"   Conviction: {chain['conviction_score']:.0f}/100")
    
    return result

def test_synthesis(geo_alpha):
    """Test synthesis with geopolitical alpha."""
    print("\n" + "=" * 60)
    print("TEST 3: Insight Synthesis")
    print("=" * 60)
    
    from synthesis.generate_insights import generate_geopolitical_alpha
    
    result = generate_geopolitical_alpha(geo_alpha)
    
    assert result is not None, "Synthesis returned None"
    assert 'chains' in result, "Missing chains in synthesis"
    assert len(result['chains']) > 0, "No chains in synthesis output"
    
    print(f"✅ Synthesized {len(result['chains'])} alpha insights")
    
    # Verify synthesis structure
    chain = result['chains'][0]
    assert 'headline' in chain, "Missing headline"
    assert 'conviction_emoji' in chain, "Missing conviction_emoji"
    assert 'conviction_label' in chain, "Missing conviction_label"
    assert 'watch' in chain, "Missing watch items"
    assert 'historical_parallel' in chain, "Missing historical_parallel"
    
    print(f"   Top chain: {chain['headline'][:60]}...")
    print(f"   Conviction: {chain['conviction_emoji']} {chain['conviction_label']}")
    print(f"   Watch items: {len(chain['watch'])}")
    
    return result

def test_presentation(insights_with_alpha):
    """Test briefing formatting."""
    print("\n" + "=" * 60)
    print("TEST 4: Briefing Presentation")
    print("=" * 60)
    
    # Need to create mock insights structure
    mock_insights = {
        'timestamp': '2026-02-16T10:00:00',
        'executive_summary': ['Test bullet 1', 'Test bullet 2'],
        'market_explanations': [],
        'atlas_opinion': {
            'main_thesis': 'Test thesis',
            'deep_take': 'Test deep take',
            'reasoning': [],
            'contrarian_view': 'Test contrarian',
            'what_to_watch': [],
            'prediction': 'Test prediction',
            'confidence': 'high'
        },
        'educational': {
            'concept': 'Test Concept',
            'explanation': 'Test explanation'
        },
        'geopolitical_alpha': insights_with_alpha,
        'patterns_raw': {
            'significant_moves': [],
            'geopolitical_risks': [],
            'sentiment': {},
            'market_sentiment': {}
        }
    }
    
    from presentation.format_briefing import format_briefing
    
    briefing = format_briefing(mock_insights)
    
    assert isinstance(briefing, str), "Briefing should be string"
    assert len(briefing) > 0, "Briefing is empty"
    assert '🎯 GEOPOLITICAL ALPHA' in briefing or '🎯 **GEOPOLITICAL ALPHA**' in briefing, "Missing geopolitical alpha section"
    
    print(f"✅ Formatted briefing ({len(briefing)} chars)")
    print(f"   Contains Geopolitical Alpha section: Yes")
    
    # Show sample of geopolitical alpha section
    if '🎯' in briefing:
        start = briefing.find('🎯')
        sample = briefing[start:start+500]
        print(f"\n   Sample output:\n{sample}...\n")
    
    return briefing

def main():
    """Run all tests."""
    print("\n" + "🎯" * 30)
    print("GEOPOLITICAL ALPHA MODULE TEST SUITE")
    print("🎯" * 30 + "\n")
    
    try:
        # Test 1: Collector
        events = test_collector()
        
        # Test 2: Analyzer
        geo_alpha = test_analyzer(events)
        
        # Test 3: Synthesis
        insights = test_synthesis(geo_alpha)
        
        # Test 4: Presentation
        briefing = test_presentation(insights)
        
        # Summary
        print("=" * 60)
        print("🎉 ALL TESTS PASSED")
        print("=" * 60)
        print("\nGeopolitical Alpha module is ready!")
        print("To use in production:")
        print("  cd ~/clawd/intelligence-briefing")
        print("  python3 daily_briefing.py")
        print("\n✅ Module integration complete\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
