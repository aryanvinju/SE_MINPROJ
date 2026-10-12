const form = document.querySelector('#prediction-form');
const errorBox = document.querySelector('#error');
const names = {ML:'ML · Logistic regression', DL:'DL · Neural network', QML:'QML · Quantum kernel SVM'};
async function readJSON(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.status || 'Request failed.');
  return data;
}
function showError(message) { errorBox.textContent = message; errorBox.hidden = false; }
function paragraph(className, text) { const p=document.createElement('p'); p.className=className; p.textContent=text; return p; }
async function runPrediction(model, features) {
  return readJSON('/api/predict', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({model,features})});
}
function displayResults(data) {
  const container=document.querySelector('#results'); container.replaceChildren();
  for (const result of data.results) {
    const card=document.createElement('div'); card.className='result';
    const heading=document.createElement('div'); heading.className='result-head';
    heading.append(paragraph('result-title', names[result.model]), paragraph('result-label', result.label));
    const risk = paragraph('risk-badge risk-' + result.risk.level.toLowerCase(), result.risk.level + ' demo risk');
    card.append(heading, risk, paragraph('result-detail', `${result.score_type}: ${result.score.toFixed(3)}`), paragraph('result-detail', `Inference: ${result.inference_ms.toFixed(1)} ms`));
    container.append(card);
  }
  container.append(paragraph('result-detail', 'YES and NO are predicted dataset labels. Risk levels are illustrative model-score bands, not clinical risk estimates. Low does not rule out disease.'));
  const audit=document.querySelector('#audit');
  audit.replaceChildren();
  audit.hidden=!data.comparison;
  if(data.comparison){
    const c=data.comparison;
    audit.append(paragraph('audit-title', c.unanimous?'All three labels agree':'Model labels disagree'));
    audit.append(paragraph('result-detail', `${c.agreement_count} of 3 models chose ${c.majority_dataset_label}. This is a descriptive majority label, not a clinical decision.`));
    if(c.review_flag) audit.append(paragraph('warning', `Review flag: ${c.review_reasons.join('; ')}.`));
  }
  const warning=document.querySelector('#warning'); warning.textContent=data.warnings.join(' '); warning.hidden=!data.warnings.length;
}
form.addEventListener('submit', async (event) => {
  event.preventDefault(); errorBox.hidden=true;
  const button=document.querySelector('#submit'); button.disabled=true; button.textContent='Running…';
  document.querySelector('#results').replaceChildren(paragraph('empty','Running selected models…'));
  document.querySelector('#warning').hidden=true;
  try {
    const fields=Object.fromEntries(new FormData(form)); const model=fields.model; delete fields.model;
    for(const key of Object.keys(fields)) if(key!=='GENDER') fields[key]=Number(fields[key]);
    displayResults(await runPrediction(model,fields));
  } catch(error) {showError(error.message); document.querySelector('#results').replaceChildren(paragraph('empty','Prediction unavailable. Check the error beside the form.'));}
  finally {button.disabled=false;button.textContent='Run comparison';}
});
document.querySelector('#example').addEventListener('click', async()=>{
  errorBox.hidden=true;
  try { const data=await readJSON('/api/example');for(const [key,value] of Object.entries(data.features)) form.elements.namedItem(key).value=value;form.elements.namedItem('model').value='ALL';document.querySelector('#results').replaceChildren(paragraph('empty','Example loaded. Run the comparison to see predictions.'));document.querySelector('#warning').hidden=true;}
  catch(error){showError(error.message);}
});
async function initialize(){
  try {await readJSON('/health/ready');document.querySelector('#health').textContent='Models ready';}
  catch {document.querySelector('#health').textContent='Models unavailable';}
  try {
    const data=await readJSON('/api/metrics');
    document.querySelector('#split-note').textContent=`${data.unique_rows} unique records · ${data.splits.test.count} test records`;
    document.querySelector('#baseline').textContent=`Always predicting the training majority class scores ${(100*data.majority_baseline_accuracy).toFixed(1)}% accuracy. Balanced accuracy helps reveal performance on the minority class.`;
    for(const name of ['ML','DL','QML']) {
      const tr=document.createElement('tr'); const title=document.createElement('td');title.textContent=names[name];tr.append(title);
      for(const key of ['accuracy','balanced_accuracy','precision','recall','f1','roc_auc']) {const td=document.createElement('td');td.textContent=(data.models[name][key]*100).toFixed(1)+'%';tr.append(td);}
      document.querySelector('#metrics-body').append(tr);
    }
  }catch(error){document.querySelector('#split-note').textContent=error.message;}
}
initialize();
// Optional WebMCP surface for browsers that implement the emerging API.
if(document.modelContext?.registerTool){
  const lifecycle = new AbortController();
  window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
  try {Promise.resolve(document.modelContext.registerTool({name:'compare_lung_dataset_models',annotations:{readOnlyHint:false,untrustedContentHint:false},description:'Run educational ML, DL and simulated QML classification for the supplied survey codes and display the results. Not a medical assessment.',inputSchema:{type:'object',additionalProperties:false,properties:{features:{type:'object',description:'Exactly the 15 lung CSV feature fields; gender M/F, age integer, binary codes 1/2.'}},required:['features']},execute:async({features})=>{const result=await runPrediction('ALL',features);displayResults(result);return result;}},{signal:lifecycle.signal})).catch(()=>{});}catch{}
}
