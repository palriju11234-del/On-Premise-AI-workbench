import React, { useState, useRef } from 'react';
import {
  ArrowRight, Plus, FileText, Search, Edit3,
  Calculator, CheckCircle2, ShieldCheck, Loader2, AlertCircle,
  Check, Circle, ArrowLeft, Shield, CheckCheck, FileDown, ExternalLink,
  Code, Cpu, Terminal, Sliders, Play, Layers, Eye
} from 'lucide-react';
import { workbenchApi } from './api';

export default function App() {
  // Screen Router (21 screens):
  // 1: 'login'          | 2: 'command_center' | 3: 'new_task'     | 4: 'understanding'
  // 5: 'plan'           | 6: 'execution'      | 7: 'activity'     | 8: 'routing'
  // 9: 'document'       | 10: 'knowledge'     | 11: 'files'       | 12: 'projects'
  // 13: 'approvals'     | 14: 'deliverables'  | 15: 'provenance'  | 16: 'security'
  // 17: 'risk_engine'   | 18: 'code_sandbox'  | 19: 'capabilities'| 20: 'model_registry'
  // 21: 'operations'
  const [screen, setScreen] = useState('login');

  // Auth / Role State
  const [role, setRole] = useState('ENGINEER');
  const [organization, setOrganization] = useState('Engineering Workspace');
  const [authLabel, setAuthLabel] = useState('Authorized user');

  // Task & Project State
  const [taskPrompt, setTaskPrompt] = useState(
    'Review the scanned inspection report for Unit-4 and prepare an approval note based on the latest maintenance SOP.'
  );
  const [attachedFileName, setAttachedFileName] = useState('inspection_report.pdf');
  const [docContext, setDocContext] = useState(
    'Equipment: Compressor C-204. Finding: Surface corrosion on flange assembly. Severity: Medium. Vibration nominal.'
  );
  const [projectTitle, setProjectTitle] = useState('Refinery Unit 4');
  const [classification, setClassification] = useState('INTERNAL');
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleDocumentSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await workbenchApi.uploadDocument(role, file);
      console.log('Upload response:', response.data);
      setAttachedFileName(file.name);
      if (response.data?.text || response.data?.text_preview) {
        setDocContext(response.data.text || response.data.text_preview);
      }
      alert('Document uploaded and processed successfully!');
    } catch (error) {
      alert('Upload failed. Please check API connection.');
    } finally {
      setIsUploading(false);
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };
  // Approval Flow State (WEB 13)
  const [approvalDecision, setApprovalDecision] = useState(null);

  // RAG Search State (WEB 10)
  const [knowledgeSearchQuery, setKnowledgeSearchQuery] = useState('');
  const [knowledgeResults, setKnowledgeResults] = useState([
    { title: 'Maintenance SOP — Section 4.2', tag: 'Relevant' },
    { title: 'Inspection Manual — Page 18', tag: 'Relevant' },
    { title: 'Previous approved report — Unit 3', tag: 'Related' },
  ]);

  // Files Filter State (WEB 11)
  const [fileFilter, setFileFilter] = useState('All');
  const filesList = [
    { name: 'inspection_report.pdf', type: 'PDF', security: 'Sensitive', category: 'Recent' },
    { name: 'Maintenance_SOP_v4.pdf', type: 'PDF', security: 'Sensitive', category: 'Projects' },
    { name: 'engineering_drawing.png', type: 'IMAGE', security: 'Critical', category: 'Critical' },
    { name: 'calculation.xlsx', type: 'XLSX', security: 'Normal', category: 'Recent' },
  ];

  // Operations Filter State (WEB 21)
  const [operationFilter, setOperationFilter] = useState('Processing');
  const operationsList = [
    { title: 'Inspection Report → Approval Note', status: 'Running', color: 'text-emerald-700 font-semibold', category: 'Processing' },
    { title: 'Vendor comparison', status: 'Needs review', color: 'text-emerald-800/80 font-medium', category: 'Pending' },
    { title: 'Pressure-drop calculation', status: 'Completed', color: 'text-emerald-700 font-semibold', category: 'Completed' },
    { title: 'Internal tool verification', status: 'Blocked', color: 'text-emerald-900/80 font-medium', category: 'Blocked' },
  ];

  // Code Workspace Sandbox Lines (WEB 18)
  const [codePrompt, setCodePrompt] = useState('Write a pressure-drop calculator.');
  const codeLines = [
    'def calculate_drop():',
    '    # parameters',
    '    result = ...',
    '    return result',
    '',
    'assert result >= 0',
    '',
    'print(result)',
    'def calculate_drop():',
    '    # parameters'
  ];

  // Capabilities Registry (WEB 19)
  const capabilitiesList = [
    { title: 'Search', status: 'Available' },
    { title: 'OCR', status: 'Available' },
    { title: 'Vision', status: 'Available' },
    { title: 'Calculation', status: 'Available' },
    { title: 'Code execution', status: 'Available' },
    { title: 'Spreadsheet processing', status: 'Available' },
    { title: 'Office generation', status: 'Available' },
    { title: 'Internal APIs', status: 'Available' },
  ];

  // Model Registry (WEB 20)
  const [modelsList, setModelsList] = useState([
    { name: 'Local Reasoning Model', category: 'Reasoning', status: 'Available' },
    { name: 'Local Coding Model', category: 'Coding', status: 'Available' },
    { name: 'Local Multimodal Model', category: 'Vision + Reasoning', status: 'Available' },
    { name: 'Embedding Model', category: 'Retrieval', status: 'Available' },
  ]);

  // Execution & Agent Pipeline State
  const [activeStepIndex, setActiveStepIndex] = useState(4);
  const [taskStatus, setTaskStatus] = useState('PROCESSING');
  const [agentResult, setAgentResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Workflow Checklist Steps (WEB 6)
  const workflowSteps = [
    { key: 'understand', label: 'Understand' },
    { key: 'plan', label: 'Plan' },
    { key: 'ocr', label: 'OCR / Vision' },
    { key: 'knowledge', label: 'Knowledge' },
    { key: 'analyze', label: 'Analyze' },
    { key: 'draft', label: 'Draft' },
    { key: 'verify', label: 'Verify' },
    { key: 'govern', label: 'Govern' },
    { key: 'deliver', label: 'Deliver' },
  ];

  // Plan 10 Steps (WEB 5)
  const planSteps = [
    'Inspect uploaded document',
    'Extract information',
    'Retrieve relevant SOP',
    'Analyze findings',
    'Draft recommendation',
    'Validate against SOP',
    'Assess risk',
    'Request approval if required',
    'Generate deliverable',
    'Record provenance',
  ];

  // Timeline Activities (WEB 7)
  const timelineActivities = [
    { id: '01', title: 'Document inspected', status: 'Completed', color: 'text-emerald-700' },
    { id: '02', title: 'Local OCR extracted scanned text', status: 'Completed', color: 'text-emerald-700' },
    { id: '03', title: 'Maintenance SOP retrieved', status: 'Completed', color: 'text-emerald-700' },
    { id: '04', title: 'Multimodal model selected', status: 'Selected', color: 'text-emerald-700' },
    { id: '05', title: 'Analysis running', status: 'Running', color: 'text-emerald-600 font-semibold' },
    { id: '06', title: 'Validation pending', status: 'Waiting', color: 'text-emerald-800/60' },
    { id: '07', title: 'Risk assessment pending', status: 'Waiting', color: 'text-emerald-800/60' },
  ];

  // Projects (WEB 12)
  const projectsData = [
    { name: 'Refinery Unit 4 Inspection', files: 48, tasks: 12 },
    { name: 'Maintenance Review', files: 24, tasks: 7 },
    { name: 'Engineering Analysis', files: 31, tasks: 9 },
    { name: 'Vendor Evaluation', files: 16, tasks: 4 },
  ];

  // Deliverables (WEB 14)
  const deliverablesData = [
    { name: 'Inspection_Approval_Note.docx', status: 'Verified' },
    { name: 'analysis.pdf', status: 'Verified' },
    { name: 'calculation.xlsx', status: 'Verified' },
    { name: 'verified_code.zip', status: 'Verified' },
  ];

  // Provenance Events (WEB 15)
  const provenanceSteps = [
    { id: '01', name: 'INPUT' },
    { id: '02', name: 'CLASSIFICATION' },
    { id: '03', name: 'OCR / PROCESSING' },
    { id: '04', name: 'KNOWLEDGE RETRIEVAL' },
    { id: '05', name: 'MODEL' },
    { id: '06', name: 'TOOL EXECUTION' },
    { id: '07', name: 'VALIDATION' },
    { id: '08', name: 'RISK DECISION' },
    { id: '09', name: 'HUMAN APPROVAL' },
    { id: '10', name: 'FINAL OUTPUT' },
  ];

  // Risk Engine Tiers (WEB 17)
  const riskTiers = [
    { label: 'LOW', description: 'Auto-complete' },
    { label: 'MEDIUM', description: 'Execute + Review' },
    { label: 'HIGH', description: 'Human approval' },
    { label: 'CRITICAL', description: 'Human approval mandatory' },
  ];

  // Live Agent Dispatch
  const handleTriggerAgentExecution = async () => {
    setScreen('execution');
    setTaskStatus('PROCESSING');
    setActiveStepIndex(3);
    setErrorMessage(null);

    const interval = setInterval(() => {
      setActiveStepIndex((prev) => {
        if (prev < 7) return prev + 1;
        clearInterval(interval);
        return 8;
      });
    }, 1200);

    try {
      const response = await workbenchApi.runAgent(
        role,
        taskPrompt,
        docContext,
        attachedFileName
      );
      setAgentResult(response.data);
      setTaskStatus('COMPLETED');
      setActiveStepIndex(9);
    } catch (err) {
      setErrorMessage(err.response?.data?.error || err.message || 'Execution failed');
      setTaskStatus('ERROR');
    } finally {
      clearInterval(interval);
    }
  };

  const handleExecuteRAGSearch = async (e) => {
    if (e.key === 'Enter' && knowledgeSearchQuery.trim()) {
      try {
        const res = await workbenchApi.queryRAG(role, knowledgeSearchQuery, 3);
        if (res.data?.results?.length > 0) {
          setKnowledgeResults(
            res.data.results.map((r, i) => ({
              title: `${r.doc_id || 'Extracted Document'} — Section ${i + 1}`,
              tag: 'Relevant',
            }))
          );
        }
      } catch (err) {
        console.error('RAG lookup error:', err);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#eafaf1] via-[#f0fbf5] to-[#d8f3e5] text-slate-800 flex items-center justify-center p-6 font-sans antialiased selection:bg-emerald-200">

      {/* ------------------------------------------------------------- */}
      {/* 1. WEB 1 — SECURE ACCESS                                       */}
      {/* ------------------------------------------------------------- */}
      {screen === 'login' && (
        <div className="w-full max-w-xl animate-in fade-in zoom-in-95 duration-200">
          <div className="mb-6">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">ACCESS</span>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Secure workspace</h1>
            <p className="text-slate-600 text-sm mt-1">Enter the organization workspace</p>
          </div>

          <div className="bg-white/95 backdrop-blur-md rounded-3xl p-10 shadow-xl shadow-emerald-950/5 border border-emerald-100/60 flex flex-col gap-6">
            <h2 className="text-2xl font-black tracking-wide text-emerald-800">SOVEREIGN</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-emerald-800 mb-2">Organization</label>
                <input
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/30"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-emerald-800 mb-2">Authentication</label>
                <div className="grid grid-cols-2 gap-2 mb-2">
                  {['ENGINEER', 'REVIEWER', 'AUDITOR', 'ADMIN'].map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRole(r)}
                      className={`py-2 px-3 text-xs font-bold rounded-xl border transition-all ${role === r
                        ? 'bg-emerald-700 text-white border-emerald-700 shadow-sm'
                        : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                        }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  value={`${authLabel} (${role})`}
                  readOnly
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200/80 rounded-2xl text-xs font-mono text-slate-600 focus:outline-none"
                />
              </div>
            </div>

            <button
              onClick={() => setScreen('command_center')}
              className="mt-2 w-full py-4 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 active:scale-[0.99] shadow-lg shadow-emerald-800/20 transition-all flex items-center justify-center gap-2"
            >
              Enter secure workspace
            </button>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 2. COMMAND CENTER                                             */}
      {/* ------------------------------------------------------------- */}
      {screen === 'command_center' && (
        <div className="w-full max-w-4xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">WORKSPACE</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">What do you need to get done?</h1>
              <p className="text-slate-600 text-sm mt-1">Private organizational work, from one controlled workspace.</p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setScreen('security')}
                className="py-2.5 px-4 rounded-2xl font-semibold text-emerald-800 bg-white border border-emerald-200 text-xs shadow-sm hover:bg-emerald-50 transition flex items-center gap-1.5"
              >
                <Shield className="w-3.5 h-3.5" /> Security
              </button>
              <button
                onClick={() => setScreen('operations')}
                className="py-2.5 px-4 rounded-2xl font-semibold text-emerald-800 bg-white border border-emerald-200 text-xs shadow-sm hover:bg-emerald-50 transition flex items-center gap-1.5"
              >
                <Layers className="w-3.5 h-3.5" /> Operations
              </button>
              <button
                onClick={() => setScreen('new_task')}
                className="py-2.5 px-5 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition flex items-center gap-2"
              >
                <Plus className="w-4 h-4" /> New Task
              </button>
            </div>
          </div>

          <div className="space-y-3">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase block">
              DESCRIBE THE WORK YOU NEED DONE
            </span>

            <div className="bg-white/95 backdrop-blur-md rounded-3xl p-6 shadow-xl shadow-emerald-950/5 border border-emerald-100/60 space-y-4">
              <textarea
                rows={3}
                value={taskPrompt}
                onChange={(e) => setTaskPrompt(e.target.value)}
                className="w-full p-2 bg-transparent text-slate-800 text-sm placeholder-slate-400 focus:outline-none resize-none leading-relaxed"
              />

              <div className="pt-2 border-t border-slate-100 flex items-center gap-3 text-xs text-emerald-800 font-medium flex-wrap">
                <button type="button" onClick={triggerFileUpload} className="hover:underline">
                  {isUploading ? 'Uploading...' : 'Attach files'}
                </button>
                <span className="text-slate-300">•</span>
                <button onClick={() => setScreen('knowledge')} className="hover:underline">Add context</button>
                <span className="text-slate-300">•</span>
                <button onClick={() => setScreen('projects')} className="hover:underline">Project: {projectTitle}</button>
                <span className="text-slate-300">•</span>
                <button onClick={() => setScreen('capabilities')} className="hover:underline">Capabilities</button>
                <span className="text-slate-300">•</span>
                <button onClick={() => setScreen('model_registry')} className="hover:underline">Models</button>
                <span className="text-slate-300">•</span>
                <span className="text-slate-500">Classification: {classification}</span>
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                onClick={() => setScreen('understanding')}
                className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-lg shadow-emerald-800/20 transition flex items-center gap-2"
              >
                Start Task <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="space-y-3">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase block">QUICK TASKS</span>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {[
                { title: 'Analyze Document', icon: FileText, dest: 'document' },
                { title: 'Search Knowledge', icon: Search, dest: 'knowledge' },
                { title: 'Write / Draft', icon: Edit3, dest: 'new_task' },
                { title: 'Run Calculation', icon: Calculator, dest: 'code_sandbox' },
                { title: 'Code & Verify', icon: ShieldCheck, dest: 'risk_engine' },
              ].map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => setScreen(item.dest)}
                  className="p-4 rounded-2xl bg-gradient-to-br from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white text-xs font-bold text-left flex flex-col justify-between h-24 shadow-md shadow-emerald-950/10 transition"
                >
                  <item.icon className="w-4 h-4 opacity-80" />
                  <span className="leading-snug">{item.title}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase block">ACTIVE WORK</span>
            <div
              onClick={() => setScreen('execution')}
              className="bg-white/95 backdrop-blur-md rounded-2xl px-6 py-4 shadow-md shadow-emerald-950/5 border border-emerald-100/60 flex items-center justify-between cursor-pointer hover:border-emerald-300 transition"
            >
              <span className="text-sm font-bold text-slate-800">Inspection Report → Approval Note</span>
              <span className="text-xs font-bold px-4 py-1.5 rounded-full border border-emerald-300 text-emerald-800 bg-emerald-50/60">
                PROCESSING
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 3. WEB 3 — CREATE A JOB                                       */}
      {/* ------------------------------------------------------------- */}
      {screen === 'new_task' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div>
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">NEW TASK</span>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Create a job</h1>
            <p className="text-slate-600 text-sm mt-1">Define the outcome, context and inputs.</p>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase block">TASK</span>
            <div className="bg-white/95 backdrop-blur-md rounded-2xl p-5 shadow-sm border border-emerald-100/80">
              <textarea
                rows={3}
                value={taskPrompt}
                onChange={(e) => setTaskPrompt(e.target.value)}
                className="w-full bg-transparent text-sm text-slate-800 focus:outline-none resize-none leading-relaxed"
              />
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase block">INPUTS</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div
                onClick={triggerFileUpload}
                className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80 cursor-pointer hover:border-emerald-300 transition"
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleDocumentSelect}
                  accept=".pdf,.txt,.docx,.csv"
                  className="hidden"
                />
                <p className="text-sm font-bold text-slate-800">+ Attach files</p>
                <p className="text-xs text-emerald-700 mt-1">
                  {isUploading ? 'Extracting text...' : (attachedFileName || 'PDF, image, spreadsheet, document')}
                </p>
              </div>

              <div
                onClick={() => setScreen('projects')}
                className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80 cursor-pointer hover:border-emerald-300 transition"
              >
                <p className="text-sm font-bold text-slate-800">Project: {projectTitle}</p>
                <p className="text-xs text-emerald-700 mt-1">Classification: determine automatically</p>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center pt-2">
            <button
              onClick={() => setScreen('command_center')}
              className="px-5 py-2.5 rounded-2xl text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
            >
              Cancel
            </button>
            <button
              onClick={() => setScreen('understanding')}
              className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition flex items-center gap-2"
            >
              Submit task <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 4. WEB 4 — TASK UNDERSTANDING                                 */}
      {/* ------------------------------------------------------------- */}
      {screen === 'understanding' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div>
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">TASK</span>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Understanding</h1>
            <p className="text-slate-600 text-sm mt-1">Review what the system inferred before execution.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80">
              <span className="text-xs font-bold text-emerald-800 block">Task type</span>
              <p className="text-sm font-medium text-slate-800 mt-1">Document analysis</p>
            </div>

            <div className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80">
              <span className="text-xs font-bold text-emerald-800 block">Required inputs</span>
              <p className="text-sm font-medium text-slate-800 mt-1">Scanned PDF</p>
            </div>

            <div className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80">
              <span className="text-xs font-bold text-emerald-800 block">Required capabilities</span>
              <p className="text-sm font-medium text-slate-800 mt-1">OCR + knowledge + reasoning</p>
            </div>

            <div className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80">
              <span className="text-xs font-bold text-emerald-800 block">Modality</span>
              <p className="text-sm font-medium text-slate-800 mt-1">Multimodal</p>
            </div>

            <div
              onClick={() => setScreen('risk_engine')}
              className="bg-white/95 rounded-2xl p-5 shadow-sm border border-emerald-100/80 sm:col-span-1 cursor-pointer hover:border-emerald-300 transition"
            >
              <span className="text-xs font-bold text-emerald-800 block">Risk classification</span>
              <p className="text-sm font-medium text-slate-800 mt-1">Medium / review</p>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4">
            <button
              onClick={() => setScreen('new_task')}
              className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-emerald-600 hover:bg-emerald-700 shadow-sm transition"
            >
              Modify
            </button>
            <button
              onClick={() => setScreen('plan')}
              className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition flex items-center gap-2"
            >
              Start execution <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 5. WEB 5 — TASK PLAN                                          */}
      {/* ------------------------------------------------------------- */}
      {screen === 'plan' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div>
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">AGENT</span>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Plan</h1>
            <p className="text-slate-600 text-sm mt-1">The proposed workflow before execution.</p>
          </div>

          <div className="space-y-3 py-2">
            {planSteps.map((step, idx) => (
              <div key={idx} className="flex items-center gap-4 text-sm">
                <span className="text-xs font-mono font-bold text-emerald-800 w-6">
                  {String(idx + 1).padStart(2, '0')}
                </span>
                <span className="text-slate-800 font-normal">{step}</span>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center pt-4">
            <button
              onClick={() => setScreen('understanding')}
              className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-emerald-600 hover:bg-emerald-700 shadow-sm transition"
            >
              Cancel
            </button>
            <button
              onClick={handleTriggerAgentExecution}
              className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition flex items-center gap-2"
            >
              Start execution <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 6. WEB 6 — AGENT EXECUTION WORKSPACE                          */}
      {/* ------------------------------------------------------------- */}
      {screen === 'execution' && (
        <div className="w-full max-w-4xl animate-in fade-in duration-200 space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">ACTIVE TASK</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
                Inspection Report → Approval Note
              </h1>
              <p className="text-slate-600 text-sm mt-1">Agent execution with auditable action summaries.</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setScreen('activity')}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-white border border-emerald-200 text-emerald-800 shadow-sm hover:bg-emerald-50"
              >
                Trace
              </button>
              <button
                onClick={() => setScreen('provenance')}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-white border border-emerald-200 text-emerald-800 shadow-sm hover:bg-emerald-50"
              >
                Provenance
              </button>
              <button
                onClick={() => setScreen('command_center')}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-white border border-emerald-200 text-emerald-800 shadow-sm hover:bg-emerald-50"
              >
                Command Center
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-start">
            <div className="md:col-span-4 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-6">
              <div>
                <span className="text-xs font-bold text-emerald-800 block">TASK</span>
                <p className="text-sm font-bold text-slate-900 mt-1 leading-snug">Review Unit-4 inspection report</p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">INPUT</span>
                <p
                  onClick={() => setScreen('document')}
                  className="text-xs font-mono text-emerald-700 mt-1 underline cursor-pointer hover:text-emerald-900"
                >
                  {attachedFileName}
                </p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">STATUS</span>
                <div className="mt-1.5">
                  <span className="inline-block text-xs font-bold px-3 py-1 rounded-full border border-emerald-300 text-emerald-800 bg-emerald-50/60">
                    {taskStatus}
                  </span>
                </div>
              </div>
            </div>

            <div className="md:col-span-5 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-3.5">
              {workflowSteps.map((s, idx) => {
                const isDone = idx < activeStepIndex;
                const isCurrent = idx === activeStepIndex;

                return (
                  <div key={s.key} className="flex items-center gap-2.5 text-sm">
                    <span className="font-semibold text-slate-800">{s.label}</span>
                    {isDone && <Check className="w-4 h-4 text-slate-800 stroke-[2.5]" />}
                    {isCurrent && <span className="w-2.5 h-2.5 rounded-full bg-slate-900 inline-block ml-0.5 animate-ping" />}
                    {!isDone && !isCurrent && <Circle className="w-3.5 h-3.5 text-slate-300 stroke-[1.5]" />}
                  </div>
                );
              })}
            </div>

            <div className="md:col-span-3 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-6">
              <div>
                <span className="text-xs font-bold text-emerald-800 block">TRUST</span>
                <p
                  onClick={() => setScreen('routing')}
                  className="text-sm font-bold text-slate-900 mt-1 cursor-pointer hover:underline"
                >
                  Local
                </p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">RISK</span>
                <div className="mt-1.5">
                  <span
                    onClick={() => setScreen('risk_engine')}
                    className="inline-block text-[11px] font-bold px-3 py-1 rounded-full border border-slate-200 text-emerald-800 tracking-wide cursor-pointer hover:border-emerald-400"
                  >
                    MEDIUM
                  </span>
                </div>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">Approval</span>
                <p
                  onClick={() => setScreen('approvals')}
                  className="text-sm font-medium text-emerald-700 underline cursor-pointer mt-1"
                >
                  Review required
                </p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">Provenance</span>
                <p
                  onClick={() => setScreen('provenance')}
                  className="text-sm font-medium text-emerald-700 underline cursor-pointer mt-1"
                >
                  Active
                </p>
              </div>
            </div>
          </div>

          {agentResult && (
            <div className="bg-white/95 rounded-3xl p-6 shadow-lg border border-emerald-200 space-y-3 animate-in fade-in">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-emerald-800 uppercase">Agent Synthesis Deliverable</span>
                <button
                  onClick={() => setScreen('deliverables')}
                  className="text-xs font-bold text-emerald-700 underline flex items-center gap-1"
                >
                  View in Deliverables <ArrowRight className="w-3 h-3" />
                </button>
              </div>
              <p className="text-xs font-mono text-slate-700 bg-slate-50 p-4 rounded-xl whitespace-pre-wrap leading-relaxed">
                {agentResult.answer}
              </p>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 7. WEB 7 — AGENT ACTIVITY TIMELINE                            */}
      {/* ------------------------------------------------------------- */}
      {screen === 'activity' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">TRACE</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Agent activity</h1>
              <p className="text-slate-600 text-sm mt-1">Concise auditable actions — never private chain-of-thought.</p>
            </div>
            <button
              onClick={() => setScreen('execution')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-3">
            {timelineActivities.map((act) => (
              <div
                key={act.id}
                className="bg-white/95 backdrop-blur-md rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <span className="text-xs font-mono font-bold text-emerald-800 w-6">{act.id}</span>
                  <span className="text-sm text-slate-800 font-medium">{act.title}</span>
                </div>
                <span className={`text-xs font-semibold ${act.color}`}>{act.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 8. WEB 8 — AUTOMATIC MODEL ROUTING                            */}
      {/* ------------------------------------------------------------- */}
      {screen === 'routing' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">MODEL FABRIC</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Automatic model routing</h1>
              <p className="text-slate-600 text-sm mt-1">The system selects an appropriate local model for the task.</p>
            </div>
            <button
              onClick={() => setScreen('execution')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-4">
              {['Multimodal', 'Long context', 'Reasoning', 'Local execution'].map((feature, i) => (
                <div key={i} className="flex items-center gap-2.5 text-sm text-slate-800 font-medium">
                  <Check className="w-4 h-4 text-slate-700 stroke-[2.5]" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>

            <div className="bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-bold text-emerald-800 tracking-wider uppercase block">
                  LOCAL MULTIMODAL REASONING
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-2">Selected automatically</h3>
                <p className="text-xs text-emerald-700 mt-1">Based on modality, complexity and resources.</p>
              </div>

              <button
                onClick={() => setScreen('model_registry')}
                className="mt-6 w-full py-3 px-5 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition"
              >
                View model registry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 9. WEB 9 — MULTIMODAL DOCUMENT WORKSPACE                      */}
      {/* ------------------------------------------------------------- */}
      {screen === 'document' && (
        <div className="w-full max-w-4xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">MULTIMODAL</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Inspection report</h1>
              <p className="text-slate-600 text-sm mt-1">Move between original evidence, extracted information and sources.</p>
            </div>
            <button
              onClick={() => setScreen('execution')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-start">
            <div className="md:col-span-4 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-4">
              <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider block">SCANNED PDF</span>
              <div className="space-y-2.5">
                {[1, 2, 3, 4, 5, 6, 7, 8].map((line) => (
                  <div key={line} className="h-6 w-full bg-slate-50 border border-slate-200/80 rounded-full" />
                ))}
              </div>
            </div>

            <div className="md:col-span-4 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-4">
              <div>
                <span className="text-xs font-bold text-emerald-800 block">Equipment</span>
                <p className="text-sm font-medium text-emerald-700 mt-0.5">Compressor C-204</p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">Date</span>
                <p className="text-sm font-medium text-emerald-700 mt-0.5">14 Aug 2026</p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">Finding</span>
                <p className="text-sm font-medium text-emerald-700 mt-0.5">Surface corrosion</p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">Severity</span>
                <p className="text-sm font-medium text-emerald-700 mt-0.5">Medium</p>
              </div>

              <div>
                <span className="text-xs font-bold text-emerald-800 block">Confidence</span>
                <p className="text-sm font-medium text-emerald-700 mt-0.5">94%</p>
              </div>
            </div>

            <div className="md:col-span-4 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-5">
              <div onClick={() => setScreen('knowledge')} className="cursor-pointer hover:underline">
                <p className="text-sm font-medium text-emerald-800">Maintenance SOP v4</p>
              </div>

              <div onClick={() => setScreen('knowledge')} className="cursor-pointer hover:underline">
                <p className="text-sm font-medium text-emerald-800">Inspection Manual</p>
              </div>

              <div onClick={() => setScreen('knowledge')} className="cursor-pointer hover:underline">
                <p className="text-sm font-medium text-emerald-800">Previous report</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 10. WEB 10 — ORGANIZATIONAL KNOWLEDGE (RAG)                  */}
      {/* ------------------------------------------------------------- */}
      {screen === 'knowledge' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">KNOWLEDGE</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Organizational knowledge</h1>
              <p className="text-slate-600 text-sm mt-1">Private manuals, SOPs, reports and correspondence.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="bg-white/95 rounded-2xl p-4 shadow-sm border border-emerald-100/80">
            <input
              type="text"
              value={knowledgeSearchQuery}
              onChange={(e) => setKnowledgeSearchQuery(e.target.value)}
              onKeyDown={handleExecuteRAGSearch}
              placeholder="Search organizational knowledge"
              className="w-full bg-transparent text-sm text-slate-800 focus:outline-none placeholder-slate-400"
            />
          </div>

          <div className="space-y-3">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase block">RESULTS</span>
            {knowledgeResults.map((item, i) => (
              <div
                key={i}
                className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between"
              >
                <span className="text-sm font-bold text-emerald-800">{item.title}</span>
                <span className="text-xs font-medium text-emerald-700">{item.tag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 11. WEB 11 — SECURE FILES                                    */}
      {/* ------------------------------------------------------------- */}
      {screen === 'files' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">FILES</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Secure files</h1>
              <p className="text-slate-600 text-sm mt-1">Documents and engineering inputs available to authorized work.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {['All', 'Recent', 'Projects', 'Sensitive', 'Critical'].map((pill) => (
              <button
                key={pill}
                onClick={() => setFileFilter(pill)}
                className={`py-2 px-5 text-xs font-bold rounded-2xl transition ${fileFilter === pill
                  ? 'bg-gradient-to-r from-emerald-700 to-emerald-600 text-white shadow-sm'
                  : 'bg-emerald-600/20 text-emerald-900 hover:bg-emerald-600/30'
                  }`}
              >
                {pill}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {filesList
              .filter((f) => fileFilter === 'All' || f.category === fileFilter || f.security === fileFilter)
              .map((file, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setAttachedFileName(file.name);
                    setScreen('document');
                  }}
                  className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between cursor-pointer hover:border-emerald-300 transition"
                >
                  <span className="text-sm font-bold text-slate-800">{file.name}</span>
                  <div className="flex items-center gap-6 text-xs font-medium">
                    <span className="text-emerald-700">{file.type}</span>
                    <span className="text-emerald-700">{file.security}</span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 12. WEB 12 — PROJECTS                                         */}
      {/* ------------------------------------------------------------- */}
      {screen === 'projects' && (
        <div className="w-full max-w-3xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">PROJECTS</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Projects</h1>
              <p className="text-slate-600 text-sm mt-1">Organize tasks, files, knowledge and deliverables around real work.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {projectsData.map((proj, idx) => (
              <div
                key={idx}
                className="bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 flex flex-col justify-between h-36"
              >
                <div>
                  <h3 className="text-base font-bold text-slate-900">{proj.name}</h3>
                  <p className="text-xs text-emerald-700 mt-1 font-medium">{proj.files} files • {proj.tasks} tasks</p>
                </div>
                <button
                  onClick={() => {
                    setProjectTitle(proj.name);
                    setScreen('command_center');
                  }}
                  className="text-xs font-bold text-emerald-700 hover:text-emerald-900 flex items-center gap-1 w-fit transition"
                >
                  Open project <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 13. WEB 13 — APPROVALS                                        */}
      {/* ------------------------------------------------------------- */}
      {screen === 'approvals' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">GOVERNANCE</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Approvals</h1>
              <p className="text-slate-600 text-sm mt-1">Human review for consequential actions.</p>
            </div>
            <button
              onClick={() => setScreen('execution')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="bg-white/95 rounded-3xl p-8 shadow-sm border border-emerald-100/80 space-y-6">
            <div>
              <h3 className="text-xl font-bold text-slate-900">Approval Required</h3>
              <div className="mt-2">
                <span className="inline-block text-[11px] font-bold px-3 py-1 rounded-full border border-slate-200 text-emerald-800 tracking-wide">
                  HIGH
                </span>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-bold text-slate-900">Inspection Report → Approval Note</h4>
              <p className="text-xs text-emerald-700 mt-1 font-medium">Recommendation prepared and validated against SOP.</p>
            </div>

            <div className="flex items-center gap-4 text-xs font-medium text-emerald-800">
              <span onClick={() => setScreen('document')} className="cursor-pointer hover:underline">Evidence • 3 sources</span>
              <span className="flex items-center gap-1"><Check className="w-3.5 h-3.5 stroke-[2.5]" /> Validation</span>
              <span onClick={() => setScreen('provenance')} className="flex items-center gap-1 cursor-pointer hover:underline"><Check className="w-3.5 h-3.5 stroke-[2.5]" /> Provenance</span>
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <button
                onClick={() => {
                  setApprovalDecision('APPROVED');
                  setScreen('deliverables');
                }}
                className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition"
              >
                Approve
              </button>
              <button
                onClick={() => {
                  setApprovalDecision('CHANGES_REQUESTED');
                  setScreen('execution');
                }}
                className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 shadow-md transition"
              >
                Request changes
              </button>
              <button
                onClick={() => {
                  setApprovalDecision('REJECTED');
                  setScreen('command_center');
                }}
                className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md transition"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 14. WEB 14 — DELIVERABLES                                     */}
      {/* ------------------------------------------------------------- */}
      {screen === 'deliverables' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">OUTPUT</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Deliverables</h1>
              <p className="text-slate-600 text-sm mt-1">Real files produced by controlled workflows.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-3">
            {deliverablesData.map((del, idx) => (
              <div
                key={idx}
                className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between"
              >
                <span className="text-sm font-bold text-slate-800">{del.name}</span>
                <div className="flex items-center gap-6">
                  <span className="text-xs font-semibold text-emerald-700">{del.status}</span>
                  <button
                    onClick={() => alert(`Opening ${del.name} (Provenance Hash Verified)`)}
                    className="py-2 px-6 rounded-xl font-bold text-white text-xs bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-sm transition"
                  >
                    Open
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 15. WEB 15 — PROVENANCE                                       */}
      {/* ------------------------------------------------------------- */}
      {screen === 'provenance' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">AUDIT</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Provenance</h1>
              <p className="text-slate-600 text-sm mt-1">Trace how the final deliverable was produced.</p>
            </div>
            <button
              onClick={() => setScreen('execution')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-2.5 py-1">
            {provenanceSteps.map((step) => (
              <div key={step.id} className="flex items-center justify-between text-xs py-1">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-emerald-800 w-5">{step.id}</span>
                  <span className="font-bold text-slate-800 tracking-wide">{step.name}</span>
                </div>
                <span className="text-emerald-700/80 font-medium">timestamp • source • result • hash</span>
              </div>
            ))}
          </div>

          <div className="flex justify-center pt-3">
            <span className="text-xs font-bold px-6 py-2 rounded-full border border-emerald-300 text-emerald-800 bg-white/95 shadow-sm tracking-wider">
              VERIFIED
            </span>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 16. WEB 16 — SOVEREIGN SECURITY                               */}
      {/* ------------------------------------------------------------- */}
      {screen === 'security' && (
        <div className="w-full max-w-3xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">SECURITY</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Sovereign security</h1>
              <p className="text-slate-600 text-sm mt-1">Make the trust boundary visible without clutter.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-stretch">
            <div className="bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 space-y-4">
              <div>
                <h3 className="text-2xl font-black text-slate-900">SECURE</h3>
                <p className="text-xs text-slate-600 mt-0.5 font-medium">Air-gapped / local execution</p>
              </div>

              <div className="space-y-3 pt-2">
                {['Data', 'Models', 'Knowledge', 'Tools', 'Processing', 'Outputs'].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs font-bold">
                    <span className="text-emerald-800">{item}</span>
                    <span className="text-emerald-700 flex items-center gap-1">
                      LOCAL <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider block">
                  NETWORK MONITOR
                </span>

                <div className="space-y-4 mt-4">
                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-emerald-800">External connections</span>
                    <span className="text-base font-bold text-slate-900">0</span>
                  </div>

                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-emerald-800">External AI/API calls</span>
                    <span className="text-base font-bold text-slate-900">0</span>
                  </div>

                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-emerald-800">Data egress</span>
                    <span className="text-base font-bold text-slate-900">0 bytes</span>
                  </div>

                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-emerald-800">Internal activity</span>
                    <span className="text-base font-bold text-slate-900">Active</span>
                  </div>
                </div>
              </div>

              <p className="text-[11px] text-emerald-700 mt-6 pt-3 border-t border-slate-100 font-medium">
                Demo values must be labeled as simulated.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 17. WEB 17 — RISK ENGINE                                      */}
      {/* ------------------------------------------------------------- */}
      {screen === 'risk_engine' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">GOVERNANCE</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Risk engine</h1>
              <p className="text-slate-600 text-sm mt-1">Risk determines when review or intervention is required.</p>
            </div>
            <button
              onClick={() => setScreen('understanding')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-3">
            {riskTiers.map((tier, idx) => (
              <div
                key={idx}
                className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center gap-6"
              >
                <span className="text-xs font-bold px-5 py-1.5 rounded-full border border-slate-300 text-emerald-800 tracking-wide w-28 text-center">
                  {tier.label}
                </span>
                <span className="text-sm font-bold text-slate-900">
                  {tier.description}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2">
            <p className="text-sm font-bold text-emerald-950">
              Current task: HIGH → human approval required
            </p>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 18. WEB 18 — CODE WORKSPACE (SANDBOX)                         */}
      {/* ------------------------------------------------------------- */}
      {screen === 'code_sandbox' && (
        <div className="w-full max-w-4xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">DEVELOPMENT</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Code workspace</h1>
              <p className="text-slate-600 text-sm mt-1">Generate, execute and verify code in an isolated sandbox.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-stretch">
            {/* Left Prompt Column */}
            <div className="md:col-span-4 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80">
              <textarea
                value={codePrompt}
                onChange={(e) => setCodePrompt(e.target.value)}
                rows={4}
                className="w-full bg-transparent text-sm font-bold text-slate-900 focus:outline-none resize-none"
              />
            </div>

            {/* Middle Code Editor Column */}
            <div className="md:col-span-5 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 font-mono text-xs text-emerald-700 leading-relaxed space-y-1">
              {codeLines.map((line, idx) => (
                <div key={idx} className="flex gap-4">
                  <span className="text-slate-400 w-4 text-right select-none">{idx + 1}</span>
                  <span className="text-emerald-700 font-medium whitespace-pre">{line}</span>
                </div>
              ))}
            </div>

            {/* Right Sandbox Policy Column */}
            <div className="md:col-span-3 bg-white/95 rounded-3xl p-6 shadow-sm border border-emerald-100/80 flex flex-col justify-between">
              <div className="space-y-6">
                <div>
                  <span className="text-xs font-bold text-emerald-800 tracking-wider block">ISOLATED</span>
                </div>

                <div>
                  <span className="text-xs font-bold text-emerald-800 tracking-wider block">Network OFF</span>
                </div>

                <div>
                  <span className="text-xs font-bold text-emerald-800 tracking-wider block">Files TEMP</span>
                </div>

                <div className="flex items-center gap-1 text-xs font-bold text-emerald-800">
                  <span>Tests</span>
                  <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 19. WEB 19 — CAPABILITIES                                     */}
      {/* ------------------------------------------------------------- */}
      {screen === 'capabilities' && (
        <div className="w-full max-w-3xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">CAPABILITY FABRIC</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Capabilities</h1>
              <p className="text-slate-600 text-sm mt-1">Controlled organizational tools available to agents.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {capabilitiesList.map((tool, idx) => (
              <div
                key={idx}
                className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between"
              >
                <span className="text-sm font-bold text-slate-900">{tool.title}</span>
                <span className="text-xs font-medium text-emerald-700">{tool.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 20. WEB 20 — MODEL REGISTRY                                   */}
      {/* ------------------------------------------------------------- */}
      {screen === 'model_registry' && (
        <div className="w-full max-w-3xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">MODEL FABRIC</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Model registry</h1>
              <p className="text-slate-600 text-sm mt-1">Registered local open-weight models.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-3">
            {modelsList.map((mod, idx) => (
              <div
                key={idx}
                className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between"
              >
                <span className="text-sm font-bold text-slate-900">{mod.name}</span>
                <div className="flex items-center gap-8">
                  <span className="text-xs font-medium text-emerald-700">{mod.category}</span>
                  <span className="text-xs font-medium text-emerald-700">{mod.status}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={() => {
                const name = prompt('Enter new local model identifier:');
                if (name) {
                  setModelsList([...modelsList, { name, category: 'General', status: 'Available' }]);
                }
              }}
              className="py-3 px-6 rounded-2xl font-semibold text-white text-sm bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 shadow-md shadow-emerald-800/20 transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" /> Register model
            </button>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 21. OPERATIONS / ACTIVITY                                     */}
      {/* ------------------------------------------------------------- */}
      {screen === 'operations' && (
        <div className="w-full max-w-2xl animate-in fade-in duration-200 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">OPERATIONS</span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">Activity</h1>
              <p className="text-slate-600 text-sm mt-1">Monitor work that is running, waiting or blocked.</p>
            </div>
            <button
              onClick={() => setScreen('command_center')}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {['Processing', 'Pending', 'Completed', 'Blocked'].map((pill) => (
              <button
                key={pill}
                onClick={() => setOperationFilter(pill)}
                className={`py-2 px-6 text-xs font-bold rounded-2xl transition ${operationFilter === pill
                  ? 'bg-gradient-to-r from-emerald-700 to-emerald-600 text-white shadow-sm'
                  : 'bg-emerald-600/20 text-emerald-900 hover:bg-emerald-600/30'
                  }`}
              >
                {pill}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {operationsList
              .filter((op) => op.category === operationFilter)
              .map((op, idx) => (
                <div
                  key={idx}
                  onClick={() => setScreen('execution')}
                  className="bg-white/95 rounded-2xl px-6 py-4 shadow-sm border border-emerald-100/80 flex items-center justify-between cursor-pointer hover:border-emerald-300 transition"
                >
                  <span className="text-sm font-bold text-slate-900">{op.title}</span>
                  <span className={`text-xs ${op.color}`}>{op.status}</span>
                </div>
              ))}
          </div>
        </div>
      )}

    </div>
  );
}