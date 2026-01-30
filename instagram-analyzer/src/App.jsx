import { useState } from 'react'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const analyzePost = async () => {
    if (!url.trim()) return
    
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed')
      }
      
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getGradeColor = (grade) => {
    const colors = {
      'A': 'text-green-500',
      'B': 'text-blue-500',
      'C': 'text-yellow-500',
      'D': 'text-orange-500',
      'F': 'text-red-500'
    }
    return colors[grade] || 'text-gray-500'
  }

  const getGradeBg = (grade) => {
    const colors = {
      'A': 'bg-green-100 border-green-300',
      'B': 'bg-blue-100 border-blue-300',
      'C': 'bg-yellow-100 border-yellow-300',
      'D': 'bg-orange-100 border-orange-300',
      'F': 'bg-red-100 border-red-300'
    }
    return colors[grade] || 'bg-gray-100 border-gray-300'
  }

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            📊 Instagram Post Analyzer
          </h1>
          <p className="text-white/80">
            Paste an Instagram post URL to analyze engagement and get improvement tips
          </p>
        </div>

        {/* Input Card */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.instagram.com/p/..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              onKeyDown={(e) => e.key === 'Enter' && analyzePost()}
            />
            <button
              onClick={analyzePost}
              disabled={loading || !url.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing...
                </span>
              ) : 'Analyze'}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-100 border border-red-300 text-red-700 px-6 py-4 rounded-xl mb-6">
            <p className="font-medium">Error</p>
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="bg-white rounded-2xl shadow-xl p-6 space-y-6">
            {/* Grade Header */}
            <div className={`${getGradeBg(result.grade)} border-2 rounded-xl p-6 text-center`}>
              <p className="text-gray-600 text-sm uppercase tracking-wide mb-1">Post Grade</p>
              <p className={`text-6xl font-bold ${getGradeColor(result.grade)}`}>
                {result.grade}
              </p>
              <p className="text-gray-600 mt-2">{result.grade_description}</p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-xl p-4 text-center">
                <p className="text-gray-500 text-sm">Post Type</p>
                <p className="text-xl font-semibold text-gray-800">{result.post_type}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 text-center">
                <p className="text-gray-500 text-sm">Engagement Rate</p>
                <p className="text-xl font-semibold text-gray-800">{result.engagement_rate}%</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 text-center">
                <p className="text-gray-500 text-sm">Est. Likes</p>
                <p className="text-xl font-semibold text-gray-800">{result.estimated_likes?.toLocaleString()}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 text-center">
                <p className="text-gray-500 text-sm">Est. Comments</p>
                <p className="text-xl font-semibold text-gray-800">{result.estimated_comments?.toLocaleString()}</p>
              </div>
            </div>

            {/* Suggestions */}
            <div>
              <h3 className="font-semibold text-gray-800 mb-3">💡 Suggestions to Improve</h3>
              <ul className="space-y-2">
                {result.suggestions?.map((suggestion, i) => (
                  <li key={i} className="flex items-start gap-2 text-gray-600">
                    <span className="text-purple-500 mt-1">•</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Footer */}
        <p className="text-center text-white/60 text-sm mt-8">
          Built by Atlas 🏛️
        </p>
      </div>
    </div>
  )
}

export default App
