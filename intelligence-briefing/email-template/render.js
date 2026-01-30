const { render } = require('@react-email/render');
const React = require('react');
const IntelligenceBriefing = require('./IntelligenceBriefing.jsx').default;
const fs = require('fs');
const path = require('path');

// Read insights JSON from command line arg or default path
const insightsPath = process.argv[2] || '../data/history/2026-01-25_insights.json';
const insights = JSON.parse(fs.readFileSync(insightsPath, 'utf8'));

// Transform insights data to email props
const emailProps = {
  date: new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }),
  executiveSummary: insights.executive_summary || [],
  marketMovements: (insights.patterns_raw?.significant_moves || []).map(move => ({
    symbol: move.symbol,
    price: move.price,
    change: move.change,
    direction: move.direction,
    chartUrl: `https://finance.yahoo.com/quote/${move.symbol}`,
    explanation: insights.market_explanations?.[0] ? {
      asset: insights.market_explanations[0].asset,
      movement: insights.market_explanations[0].movement,
      causes: insights.market_explanations[0].possible_causes || []
    } : null
  })),
  geopoliticalRisks: (insights.patterns_raw?.geopolitical_risks || []).map(risk => ({
    title: risk.title,
    odds: risk.odds,
    volume: risk.volume,
    risk_level: risk.risk_level
  })),
  atlasAnalysis: {
    thesis: insights.atlas_opinion?.main_thesis || '',
    reasoning: insights.atlas_opinion?.reasoning || [],
    confidence: insights.atlas_opinion?.confidence || 'moderate'
  },
  whatToWatch: insights.atlas_opinion?.what_to_watch || [],
  educational: {
    concept: insights.educational?.concept || '',
    explanation: insights.educational?.explanation || '',
    interpretation: insights.educational?.interpretation || insights.educational?.current_signal || ''
  },
  furtherReading: [] // Will be populated from the briefing
};

// Render to HTML
const html = render(React.createElement(IntelligenceBriefing, emailProps));

// Output or save
if (process.argv[3] === '--save') {
  const outputPath = path.join(__dirname, '..', 'data', 'cache', 'email.html');
  fs.writeFileSync(outputPath, html);
  console.log(`✅ Email HTML saved to: ${outputPath}`);
} else {
  console.log(html);
}
