// Debug overlay for Atlas Voice Interface
(function() {
    const debugDiv = document.createElement('div');
    debugDiv.id = 'debug-overlay';
    debugDiv.style.cssText = 'position:fixed;bottom:10px;left:10px;background:rgba(0,0,0,0.9);color:#0f0;font-family:monospace;font-size:11px;padding:10px;max-width:400px;max-height:200px;overflow-y:auto;z-index:9999;border-radius:5px;';
    document.body.appendChild(debugDiv);
    
    const log = (msg) => {
        const time = new Date().toISOString().substr(11, 12);
        debugDiv.innerHTML = `[${time}] ${msg}<br>` + debugDiv.innerHTML;
        if (debugDiv.children.length > 50) debugDiv.lastChild.remove();
        console.log(`[DEBUG] ${msg}`);
    };
    
    // Intercept WebSocket
    const origWS = WebSocket;
    window.WebSocket = function(url) {
        log(`WS connecting: ${url}`);
        const ws = new origWS(url);
        
        ws.addEventListener('open', () => log('WS OPEN'));
        ws.addEventListener('close', (e) => log(`WS CLOSE code=${e.code} reason=${e.reason}`));
        ws.addEventListener('error', (e) => log(`WS ERROR: ${e.message || 'unknown'}`));
        ws.addEventListener('message', (e) => {
            const data = JSON.parse(e.data);
            log(`WS MSG: ${data.type} ${data.text?.substring(0,30) || data.status || ''}`);
        });
        
        const origSend = ws.send.bind(ws);
        ws.send = function(data) {
            const parsed = JSON.parse(data);
            log(`WS SEND: ${parsed.type} ${parsed.text?.substring(0,30) || ''}`);
            return origSend(data);
        };
        
        return ws;
    };
    
    // Catch all errors
    window.onerror = (msg, src, line, col, err) => {
        log(`ERROR: ${msg} at ${src}:${line}`);
        return false;
    };
    
    window.onunhandledrejection = (e) => {
        log(`PROMISE ERROR: ${e.reason}`);
    };
    
    log('Debug overlay active');
})();
