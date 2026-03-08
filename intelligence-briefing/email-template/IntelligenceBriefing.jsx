import * as React from 'react';
import {
  Html,
  Head,
  Body,
  Container,
  Section,
  Text,
  Link,
  Hr,
  Heading,
} from '@react-email/components';

export const IntelligenceBriefing = ({
  date = 'Monday, January 26, 2026',
  executiveSummary = [],
  marketMovements = [],
  geopoliticalRisks = [],
  geopoliticalAlphaChains = [],
  atlasAnalysis = {},
  whatToWatch = [],
  educational = {},
  furtherReading = [],
}) => {
  return (
    <Html>
      <Head />
      <Body style={main}>
        <Container style={container}>
          {/* Header */}
          <Section style={header}>
            <Heading style={headerTitle}>🌍 INTELLIGENCE BRIEFING</Heading>
            <Text style={headerSubtitle}>{date} | Past 24 Hours</Text>
          </Section>

          {/* Executive Summary */}
          <Section style={section}>
            <Heading style={sectionTitle}>📊 EXECUTIVE SUMMARY</Heading>
            {executiveSummary.map((item, idx) => (
              <Text key={idx} style={bulletPoint}>• {item}</Text>
            ))}
          </Section>

          <Hr style={divider} />

          {/* Market Movements */}
          <Section style={section}>
            <Heading style={sectionTitle}>🎯 MARKET MOVEMENTS</Heading>
            {marketMovements.map((move, idx) => {
              const isPositive = move.direction === 'up';
              return (
                <div key={idx} style={marketItem}>
                  <Text style={marketSymbol}>
                    {isPositive ? '📈' : '📉'} <strong>{move.symbol}</strong>
                  </Text>
                  <Text style={marketPrice}>
                    ${typeof move.price === 'number' ? move.price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : move.price}
                  </Text>
                  <Text style={isPositive ? marketChangePositive : marketChangeNegative}>
                    {move.change > 0 ? '+' : ''}{move.change.toFixed(1)}%
                  </Text>
                  <Link href={move.chartUrl} style={chartLink}>📊 Chart</Link>
                </div>
              );
            })}
          </Section>

          {marketMovements[0]?.explanation && (
            <Section style={explanationBox}>
              <Text style={explanationTitle}><strong>{marketMovements[0].explanation.asset}</strong></Text>
              <Text style={explanationText}>{marketMovements[0].explanation.movement}</Text>
              <Text style={explanationSubtitle}>Possible causes:</Text>
              {marketMovements[0].explanation.causes.map((cause, idx) => (
                <Text key={idx} style={bulletPointSmall}>  • {cause}</Text>
              ))}
            </Section>
          )}

          <Hr style={divider} />

          {/* Geopolitical Landscape */}
          <Section style={section}>
            <Heading style={sectionTitle}>⚡ GEOPOLITICAL LANDSCAPE</Heading>
            {geopoliticalRisks.map((risk, idx) => {
              const riskEmoji = risk.risk_level === 'elevated' || risk.risk_level === 'likely' ? '🔴' 
                              : risk.risk_level === 'moderate' ? '🟡' : '🟢';
              return (
                <div key={idx} style={geopoliticalItem}>
                  <Text style={geopoliticalTitle}>
                    {riskEmoji} <strong>{risk.title}</strong>
                  </Text>
                  <Text style={geopoliticalDetails}>
                    Odds: {risk.odds} | Volume: ${risk.volume}
                  </Text>
                  <Text style={geopoliticalRiskLevel}>
                    Risk level: <span style={getRiskStyle(risk.risk_level)}>{risk.risk_level}</span>
                  </Text>
                </div>
              );
            })}
          </Section>

          {/* Geopolitical Alpha Chains */}
          {geopoliticalAlphaChains.length > 0 && (
            <>
              <Hr style={divider} />
              <Section style={section}>
                <Heading style={sectionTitle}>🎯 GEOPOLITICAL ALPHA</Heading>
                <Text style={alphaIntro}>Live transmission chains from events to assets</Text>
                {geopoliticalAlphaChains.map((chain, idx) => (
                  <div key={idx} style={alphaChainBox}>
                    {/* Headline with date */}
                    <Text style={alphaHeadline}>
                      <strong>{chain.headline}</strong>
                      {chain.date && <span style={alphaDate}> ({chain.date})</span>}
                    </Text>
                    
                    {/* Source */}
                    {chain.sourceUrl && (
                      <Text style={alphaSource}>
                        📰 <Link href={chain.sourceUrl} style={alphaSourceLink}>{chain.sourceDomain}</Link>
                      </Text>
                    )}
                    
                    {/* Chain summary */}
                    <Text style={alphaChainSummary}>{chain.chainSummary}</Text>
                    
                    {/* Top assets */}
                    {chain.topAssets.length > 0 && (
                      <>
                        <Text style={alphaAssetsLabel}>Transmission:</Text>
                        {chain.topAssets.map((asset, assetIdx) => {
                          const arrow = asset.direction === 'up' ? '📈' : asset.direction === 'down' ? '📉' : '➡️';
                          const convictionDots = asset.conviction === 'high' ? '●●●' 
                                                : asset.conviction === 'medium' ? '●●○' 
                                                : '●○○';
                          return (
                            <Text key={assetIdx} style={alphaAssetItem}>
                              {arrow} <strong>{asset.asset}</strong> {asset.direction} 
                              <span style={alphaConviction}> {convictionDots}</span>
                              {asset.magnitude && <span style={alphaMagnitude}> ({asset.magnitude} mag.)</span>}
                            </Text>
                          );
                        })}
                      </>
                    )}
                    
                    {/* Historical parallel */}
                    {chain.historicalParallel && (
                      <div style={alphaHistoricalBox}>
                        <Text style={alphaHistoricalLabel}>📜 Historical Echo:</Text>
                        <Text style={alphaHistoricalText}>
                          <strong>{chain.historicalParallel.event}</strong> ({chain.historicalParallel.date})
                        </Text>
                        {chain.historicalParallel.lesson && (
                          <Text style={alphaHistoricalLesson}>{chain.historicalParallel.lesson}</Text>
                        )}
                      </div>
                    )}
                    
                    {/* Teaching note */}
                    {chain.teachingNote && (
                      <div style={alphaTeachingBox}>
                        <Text style={alphaTeachingLabel}>💡 Why this connection exists:</Text>
                        <Text style={alphaTeachingText}>{chain.teachingNote}</Text>
                      </div>
                    )}
                    
                    {/* Conviction */}
                    <Text style={alphaConvictionFooter}>
                      Conviction: {chain.convictionEmoji} <strong>{chain.convictionLabel}</strong>
                    </Text>
                  </div>
                ))}
              </Section>
            </>
          )}

          <Hr style={divider} />

          {/* Atlas's Analysis */}
          <Section style={section}>
            <Heading style={sectionTitle}>💡 ATLAS'S ANALYSIS</Heading>
            <div style={analysisBox}>
              <Text style={analysisLabel}>My take:</Text>
              <Text style={analysisText}>{atlasAnalysis.thesis}</Text>
              
              {atlasAnalysis.deepTake && (
                <>
                  <Text style={analysisText}>{atlasAnalysis.deepTake}</Text>
                </>
              )}
              
              {atlasAnalysis.reasoning && atlasAnalysis.reasoning.length > 0 && (
                <>
                  <Text style={analysisLabel}>Why this matters:</Text>
                  {atlasAnalysis.reasoning.map((reason, idx) => (
                    <Text key={idx} style={bulletPointSmall}>  • {reason}</Text>
                  ))}
                </>
              )}
              
              {atlasAnalysis.contrarianView && (
                <>
                  <Text style={analysisLabel}>Contrarian angle:</Text>
                  <Text style={analysisText}>{atlasAnalysis.contrarianView}</Text>
                </>
              )}
              
              {atlasAnalysis.prediction && (
                <>
                  <Text style={analysisLabel}>Watch for:</Text>
                  <Text style={analysisText}>{atlasAnalysis.prediction}</Text>
                </>
              )}
              
              <Text style={confidenceText}>
                Confidence: <strong>{atlasAnalysis.confidence}</strong>
              </Text>
            </div>
          </Section>

          {whatToWatch.length > 0 && (
            <Section style={section}>
              <Heading style={sectionTitle}>📈 WHAT TO WATCH TODAY</Heading>
              {whatToWatch.map((item, idx) => (
                <Text key={idx} style={bulletPoint}>  • {item}</Text>
              ))}
            </Section>
          )}

          <Hr style={divider} />

          {/* Educational Content */}
          <Section style={section}>
            <Heading style={sectionTitle}>📚 LEARN: {educational.concept}</Heading>
            <Text style={educationalText}>{educational.explanation}</Text>
            {educational.interpretation && (
              <Text style={educationalHighlight}>
                <em>Today:</em> {educational.interpretation}
              </Text>
            )}
          </Section>

          {/* Further Reading */}
          {furtherReading.length > 0 && (
            <>
              <Hr style={divider} />
              <Section style={section}>
                <Heading style={sectionTitle}>🔍 FURTHER READING</Heading>
                {furtherReading.map((item, idx) => (
                  <Text key={idx} style={bulletPoint}>
                    • <Link href={item.url} style={readingLink}>{item.title}</Link>
                  </Text>
                ))}
              </Section>
            </>
          )}

          {/* Quick Reference Glossary */}
          <Hr style={divider} />
          <Section style={section}>
            <Heading style={sectionTitle}>📖 QUICK REFERENCE</Heading>
            <Text style={glossaryIntro}>Key terms used in this briefing:</Text>
            <Text style={glossaryItem}>• <strong>VIX:</strong> 'Fear gauge' - measures expected market volatility (higher = more fear)</Text>
            <Text style={glossaryItem}>• <strong>Support level:</strong> Price where buyers typically step in to prevent further drops</Text>
            <Text style={glossaryItem}>• <strong>Credit spreads:</strong> Premium for corporate bonds vs safe Treasuries (widens when fear rises)</Text>
            <Text style={glossaryItem}>• <strong>Small caps (IWM):</strong> Smaller, riskier companies that often move before large stocks</Text>
            <Text style={glossaryItem}>• <strong>Polymarket:</strong> Prediction market where people bet real money on future events</Text>
          </Section>

          {/* Footer */}
          <Hr style={divider} />
          <Section style={footer}>
            <Text style={footerText}>
              Carrying the weight so you don't have to · Built with engineering principles
            </Text>
            <Text style={footerSignature}>🏛️ Atlas</Text>
            <Text style={footerTagline}>Your Titan in the machine</Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
};

// Styles
const main = {
  backgroundColor: '#f6f9fc',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif',
};

const container = {
  backgroundColor: '#ffffff',
  margin: '0 auto',
  padding: '20px 0',
  maxWidth: '600px',
};

const header = {
  backgroundColor: '#0f172a',
  padding: '32px 24px',
  textAlign: 'center',
  borderBottom: '3px solid #1e40af',
};

const headerTitle = {
  color: '#ffffff',
  fontSize: '28px',
  fontWeight: '700',
  margin: '0 0 8px 0',
};

const headerSubtitle = {
  color: '#a0a0a0',
  fontSize: '14px',
  margin: '0',
};

const section = {
  padding: '24px',
};

const sectionTitle = {
  fontSize: '18px',
  fontWeight: '600',
  color: '#1a1a2e',
  margin: '0 0 16px 0',
};

const bulletPoint = {
  fontSize: '14px',
  lineHeight: '1.6',
  color: '#333333',
  margin: '4px 0',
};

const bulletPointSmall = {
  fontSize: '13px',
  lineHeight: '1.5',
  color: '#666666',
  margin: '2px 0',
};

const marketItem = {
  display: 'flex',
  alignItems: 'center',
  padding: '12px 16px',
  backgroundColor: '#f8f9fa',
  borderRadius: '8px',
  marginBottom: '8px',
  gap: '12px',
};

const marketSymbol = {
  fontSize: '14px',
  fontWeight: '600',
  color: '#1a1a2e',
  flex: '0 0 120px',
  margin: '0',
};

const marketPrice = {
  fontSize: '14px',
  color: '#333333',
  flex: '1',
  margin: '0',
};

const marketChangePositive = {
  fontSize: '14px',
  fontWeight: '600',
  color: '#10b981',
  flex: '0 0 60px',
  margin: '0',
};

const marketChangeNegative = {
  fontSize: '14px',
  fontWeight: '600',
  color: '#ef4444',
  flex: '0 0 60px',
  margin: '0',
};

const chartLink = {
  fontSize: '12px',
  color: '#3b82f6',
  textDecoration: 'none',
  flex: '0 0 60px',
};

const explanationBox = {
  backgroundColor: '#fffbeb',
  border: '1px solid #fcd34d',
  borderRadius: '8px',
  padding: '16px',
  margin: '16px 24px',
};

const explanationTitle = {
  fontSize: '14px',
  color: '#92400e',
  margin: '0 0 8px 0',
};

const explanationText = {
  fontSize: '13px',
  color: '#78350f',
  margin: '0 0 8px 0',
};

const explanationSubtitle = {
  fontSize: '13px',
  fontStyle: 'italic',
  color: '#92400e',
  margin: '8px 0 4px 0',
};

const geopoliticalItem = {
  padding: '12px 0',
  borderBottom: '1px solid #e5e7eb',
};

const geopoliticalTitle = {
  fontSize: '14px',
  color: '#1a1a2e',
  margin: '0 0 4px 0',
};

const geopoliticalDetails = {
  fontSize: '13px',
  color: '#666666',
  margin: '4px 0',
};

const geopoliticalRiskLevel = {
  fontSize: '12px',
  color: '#888888',
  margin: '4px 0',
};

const getRiskStyle = (level) => {
  const colors = {
    'high': { color: '#dc2626', fontWeight: '600' },
    'elevated': { color: '#ea580c', fontWeight: '600' },
    'moderate': { color: '#ca8a04', fontWeight: '600' },
    'low': { color: '#16a34a', fontWeight: '600' },
  };
  return colors[level] || { color: '#666666' };
};

const analysisBox = {
  backgroundColor: '#f0f4f8',
  border: '2px solid #1e3a5f',
  borderRadius: '8px',
  padding: '20px',
};

const analysisLabel = {
  fontSize: '13px',
  fontWeight: '600',
  color: '#1e40af',
  margin: '12px 0 4px 0',
};

const analysisText = {
  fontSize: '14px',
  color: '#1e3a8a',
  lineHeight: '1.6',
  margin: '0 0 12px 0',
};

const confidenceText = {
  fontSize: '13px',
  color: '#1e40af',
  margin: '12px 0 0 0',
};

const educationalText = {
  fontSize: '14px',
  lineHeight: '1.6',
  color: '#333333',
  margin: '0 0 12px 0',
};

const educationalHighlight = {
  fontSize: '13px',
  backgroundColor: '#f0fdf4',
  border: '1px solid #86efac',
  borderRadius: '6px',
  padding: '12px',
  color: '#166534',
  margin: '8px 0',
};

const readingLink = {
  color: '#3b82f6',
  textDecoration: 'underline',
  fontSize: '14px',
};

const divider = {
  borderColor: '#e5e7eb',
  margin: '0',
};

const footer = {
  padding: '24px',
  textAlign: 'center',
};

const footerText = {
  fontSize: '12px',
  color: '#888888',
  fontStyle: 'italic',
  margin: '0 0 8px 0',
};

const footerSignature = {
  fontSize: '14px',
  color: '#1a1a2e',
  margin: '0',
};

const footerTagline = {
  fontSize: '11px',
  color: '#a0a0a0',
  fontStyle: 'italic',
  margin: '4px 0 0 0',
};

const glossaryIntro = {
  fontSize: '13px',
  fontStyle: 'italic',
  color: '#666666',
  margin: '0 0 8px 0',
};

const glossaryItem = {
  fontSize: '13px',
  lineHeight: '1.6',
  color: '#333333',
  margin: '4px 0',
};

// Geopolitical Alpha styles
const alphaIntro = {
  fontSize: '12px',
  fontStyle: 'italic',
  color: '#666666',
  margin: '0 0 16px 0',
};

const alphaChainBox = {
  backgroundColor: '#f8fafc',
  border: '2px solid #1e40af',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '16px',
};

const alphaHeadline = {
  fontSize: '15px',
  color: '#0f172a',
  margin: '0 0 8px 0',
  lineHeight: '1.4',
};

const alphaDate = {
  fontSize: '13px',
  color: '#64748b',
  fontWeight: 'normal',
};

const alphaSource = {
  fontSize: '12px',
  color: '#475569',
  margin: '0 0 12px 0',
};

const alphaSourceLink = {
  color: '#3b82f6',
  textDecoration: 'none',
  fontWeight: '500',
};

const alphaChainSummary = {
  fontSize: '14px',
  fontWeight: '600',
  color: '#1e40af',
  backgroundColor: '#eff6ff',
  padding: '8px 12px',
  borderRadius: '6px',
  margin: '0 0 12px 0',
};

const alphaAssetsLabel = {
  fontSize: '12px',
  fontWeight: '600',
  color: '#475569',
  margin: '12px 0 6px 0',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const alphaAssetItem = {
  fontSize: '13px',
  color: '#334155',
  margin: '4px 0',
  paddingLeft: '8px',
};

const alphaConviction = {
  fontSize: '11px',
  color: '#94a3b8',
};

const alphaMagnitude = {
  fontSize: '11px',
  color: '#64748b',
  fontStyle: 'italic',
};

const alphaHistoricalBox = {
  backgroundColor: '#fefce8',
  border: '1px solid #fde047',
  borderRadius: '6px',
  padding: '12px',
  margin: '12px 0',
};

const alphaHistoricalLabel = {
  fontSize: '12px',
  fontWeight: '600',
  color: '#713f12',
  margin: '0 0 6px 0',
};

const alphaHistoricalText = {
  fontSize: '13px',
  color: '#854d0e',
  margin: '0 0 6px 0',
};

const alphaHistoricalLesson = {
  fontSize: '12px',
  color: '#a16207',
  fontStyle: 'italic',
  margin: '0',
};

const alphaTeachingBox = {
  backgroundColor: '#f0fdf4',
  border: '1px solid #86efac',
  borderRadius: '6px',
  padding: '12px',
  margin: '12px 0',
};

const alphaTeachingLabel = {
  fontSize: '12px',
  fontWeight: '600',
  color: '#15803d',
  margin: '0 0 6px 0',
};

const alphaTeachingText = {
  fontSize: '12px',
  color: '#166534',
  lineHeight: '1.5',
  margin: '0',
};

const alphaConvictionFooter = {
  fontSize: '12px',
  color: '#475569',
  margin: '12px 0 0 0',
  textAlign: 'right',
};

export default IntelligenceBriefing;
