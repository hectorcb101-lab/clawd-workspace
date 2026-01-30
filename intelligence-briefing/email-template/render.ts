import { render } from '@react-email/render';
import React from 'react';
import IntelligenceBriefing from './IntelligenceBriefing.jsx';
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Parse arguments - skip node/tsx/script paths
const args = process.argv.slice(2);
const saveFlag = args.includes('--save');
const insightsArg = args.find(arg => arg !== '--save' && arg.endsWith('.json'));
const insightsPath = insightsArg || join(__dirname, '..', 'data', 'history', '2026-01-25_insights.json');

console.log(`Reading insights from: ${insightsPath}`);
const insights = JSON.parse(readFileSync(insightsPath, 'utf8'));

// Transform insights data to email props
const emailProps = {
  date: new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }),
  executiveSummary: insights.executive_summary || [],
  marketMovements: (insights.patterns_raw?.significant_moves || []).map((move: any) => ({
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
  geopoliticalRisks: (insights.patterns_raw?.geopolitical_risks || []).map((risk: any) => ({
    title: risk.title,
    odds: risk.odds,
    volume: risk.volume,
    risk_level: risk.risk_level
  })),
  atlasAnalysis: {
    thesis: insights.atlas_opinion?.main_thesis || '',
    deepTake: insights.atlas_opinion?.deep_take || '',
    reasoning: insights.atlas_opinion?.reasoning || [],
    contrarianView: insights.atlas_opinion?.contrarian_view || '',
    prediction: insights.atlas_opinion?.prediction || '',
    confidence: insights.atlas_opinion?.confidence || 'moderate'
  },
  whatToWatch: insights.atlas_opinion?.what_to_watch || [],
  educational: {
    concept: insights.educational?.concept || '',
    explanation: insights.educational?.explanation || '',
    interpretation: insights.educational?.interpretation || insights.educational?.current_signal || ''
  },
  furtherReading: []
};

// Render to HTML (async)
(async () => {
  const html = await render(React.createElement(IntelligenceBriefing, emailProps));

  // Output or save
  if (saveFlag) {
    const outputPath = join(__dirname, '..', 'data', 'cache', 'email.html');
    writeFileSync(outputPath, html);
    console.log(`✅ Email HTML saved to: ${outputPath}`);
    console.log(`📧 Preview: file://${outputPath}`);
  } else {
    console.log(html);
  }
})();
