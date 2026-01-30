# Solution: Batch Creating Google Docs

**Problem:** Need to create multiple Google Docs programmatically, but MCP connection doesn't persist across bash subprocess calls.

**Failed Approaches:**
1. Bash script calling mcporter - Connection drops between calls
2. Python subprocess calling mcporter - Same issue  
3. Direct bash loops - Same issue

**Working Solution:** Node.js script

## Why It Works

Node.js maintains a single process context. Each `spawn('mcporter')` call happens within the same Node process, which maintains the MCP connection state.

## Implementation

```javascript
const { spawn } = require('child_process');
const fs = require('fs');

async function createDoc(title, content) {
  return new Promise((resolve, reject) => {
    const proc = spawn('mcporter', [
      'call', 'google-workspace.create_doc',
      `user_google_email=hectorcb101@gmail.com`,
      `title=${title}`,
      `content=${content.substring(0, 9500)}`
    ]);
    
    let output = '';
    proc.stdout.on('data', (data) => { output += data; });
    proc.on('close', (code) => {
      if (code === 0 && output.includes('ID:')) resolve(output);
      else reject(new Error(output));
    });
  });
}

// Loop through docs with 3-second delays
for (const doc of docs) {
  await createDoc(doc.title, content);
  await new Promise(r => setTimeout(r, 3000));
}
```

## Key Learnings

1. **Process context matters:** Subprocess calls from bash lose MCP connection
2. **Single process works:** Node.js maintaining one process keeps connection alive
3. **Delays are important:** 3 seconds between calls prevents rate limiting
4. **Trial and error:** Tried 3 approaches before finding the solution

## Usage

```bash
node /path/to/create_docs.js
```

## Result

Successfully created 15 Google Docs in ~5 minutes.

**Lesson:** When blocked, try multiple approaches. The solution often requires changing the execution context, not just the code.
