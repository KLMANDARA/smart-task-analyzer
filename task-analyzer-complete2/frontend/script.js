const tasks = [];
document.getElementById('taskForm').addEventListener('submit', (e)=>{
  e.preventDefault();
  const t = {
    id: Date.now().toString(36),
    title: document.getElementById('title').value,
    due_date: document.getElementById('due_date').value || null,
    estimated_hours: parseFloat(document.getElementById('estimated_hours').value) || 1,
    importance: parseInt(document.getElementById('importance').value) || 5,
    dependencies: (document.getElementById('dependencies').value||'').split(',').map(s=>s.trim()).filter(Boolean)
  };
  tasks.push(t);
  alert('Task added to list. Click Analyze to send to API.');
  document.getElementById('taskForm').reset();
});

async function callAnalyze(payloadTasks, strategy){
  const res = await fetch('/api/tasks/analyze/', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({tasks: payloadTasks, strategy})
  });
  if(!res.ok){ throw new Error('API error'); }
  return await res.json();
}

document.getElementById('analyzeBtn').addEventListener('click', async ()=>{
  const bulk = document.getElementById('bulk').value.trim();
  let payloadTasks = tasks.slice();
  if(bulk){
    try{ payloadTasks = JSON.parse(bulk); }catch(e){ alert('Invalid JSON in bulk input'); return; }
  }
  const strategy = document.getElementById('strategy').value;
  try{
    const data = await callAnalyze(payloadTasks, strategy);
    const list = data.tasks || data;
    renderResults(list);
    renderEisenhower(list);
    renderGraph(list);
  }catch(e){
    alert('Error: '+e.message);
  }
});

document.getElementById('suggestBtn').addEventListener('click', async ()=>{
  const strategy = document.getElementById('strategy').value;
  const sample = JSON.stringify(tasks);
  const res = await fetch('/api/tasks/suggest/?strategy='+strategy+'&sample='+encodeURIComponent(sample));
  const data = await res.json();
  const list = data.suggestions || [];
  renderResults(list);
  renderEisenhower(list);
  renderGraph(list);
});

function renderResults(list){
  const out = document.getElementById('results');
  out.innerHTML = '';
  list.forEach(t=>{
    const div = document.createElement('div');
    div.className = 'task ' + (t.score>70? 'high' : (t.score>40? 'medium':'low'));
    div.innerHTML = `<strong>${t.title}</strong> — Score: ${t.score}<br/><em>${t.reason}</em><br/><small>Due: ${t.due_date} | Est hrs: ${t.estimated_hours} | Importance: ${t.importance}</small>`;
    out.appendChild(div);
  });
}

function renderEisenhower(list){
  // Clear cells
  ['urgent_important','not_urgent_important','urgent_not_important','not_urgent_not_important'].forEach(id=>document.getElementById(id).innerHTML='<h3>'+document.getElementById(id).querySelector('h3').innerText+'</h3>');
  const today = new Date();
  list.forEach(t=>{
    const due = t.due_date ? new Date(t.due_date) : null;
    const days = due ? Math.ceil((due - today)/(1000*60*60*24)) : 365;
    const urgent = days <= 7;
    const important = (t.importance||0) >= 7;
    let cellId = 'not_urgent_not_important';
    if(urgent && important) cellId = 'urgent_important';
    else if(!urgent && important) cellId = 'not_urgent_important';
    else if(urgent && !important) cellId = 'urgent_not_important';
    const el = document.createElement('div');
    el.className = 'task';
    el.innerHTML = `<strong>${t.title}</strong><br/>Score:${t.score}`;
    document.getElementById(cellId).appendChild(el);
  });
}

function renderGraph(list){
  const cyData = { elements: [] };
  const nodes = {};
  list.forEach(t=>{
    const id = t.id || t.title;
    nodes[id] = true;
    cyData.elements.push({ data: { id: id, label: t.title }});
  });
  list.forEach(t=>{
    const src = t.id || t.title;
    (t.dependencies||[]).forEach(dep=>{
      const tgt = dep;
      cyData.elements.push({ data: { id: src + '_' + tgt, source: tgt, target: src }});
    });
  });
  // destroy existing cy instance if present
  if(window.cyInstance){
    try{ window.cyInstance.destroy(); }catch(e){}
  }
  window.cyInstance = cytoscape({
    container: document.getElementById('cy'),
    elements: cyData.elements,
    style: [
      { selector: 'node', style: { 'label': 'data(label)', 'text-valign':'center','background-color':'#0074D9','color':'#fff','text-outline-width':2,'text-outline-color':'#0074D9' } },
      { selector: 'edge', style: { 'width': 2, 'line-color': '#ccc', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#ccc' } }
    ],
    layout: { name: 'dagre' }
  });
}

document.getElementById('sendFeedback').addEventListener('click', async ()=>{
  const comp = document.getElementById('fb_comp').value;
  const delta = parseFloat(document.getElementById('fb_delta').value) || 0;
  const strategy = document.getElementById('strategy').value;
  const payload = { adjustments: { [strategy]: { [comp]: delta } } };
  try{
    const res = await fetch('/api/tasks/feedback/', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(data.status === 'ok'){
      alert('Feedback recorded. New weights saved.');
    }else{
      alert('Error sending feedback');
    }
  }catch(e){
    alert('Feedback error: '+e.message);
  }
});
