// frontend/src/components/InteractionForm.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logInteraction } from '../store/slices/interactionSlice';
import { fetchHCPs } from '../store/slices/hcpSlice';
import Select from 'react-select';
import {
  Search,
  Mic,
  Calendar,
  Clock,
  Plus,
  AlertTriangle,
  Sparkles,
} from 'lucide-react';
import './InteractionForm.css';

const AI_SUGGESTED_FOLLOWUPS = [
  'Schedule follow-up meeting in 2 weeks',
  'Send OncoBoost Phase III PDF',
  'Add Dr. Sharma to advisory board invite list',
];

const InteractionForm = ({ selectedHCP }) => {
  const dispatch = useDispatch();
  const { hcps, loading: hcpLoading, error } = useSelector((state) => state.hcps);
  const { loading } = useSelector((state) => state.interactions);

  const now = new Date();

  const [formData, setFormData] = useState({
    hcp_id: '',
    interaction_type: 'Meeting',
    date: now.toISOString().slice(0, 10),
    time: now.toTimeString().slice(0, 5),
    attendees: '',
    topics: '',
    summary: '',
    sentiment: 'Neutral',
    outcomes: '',
    follow_up: '',
    materials_shared: [],
    samples_distributed: [],
  });

  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false); 
  const chatEndRef = useRef(null);
  

  useEffect(() => {
    console.log('🔄 Fetching HCPs on component mount...');
    dispatch(fetchHCPs());
  }, [dispatch]);

  useEffect(() => {
    if (selectedHCP) {
      setFormData((prev) => ({ ...prev, hcp_id: selectedHCP.id }));
    }
  }, [selectedHCP]);

  useEffect(() => {
    console.log('📊 HCPs in Redux state:', hcps.length, 'HCPs');
    console.log('📊 HCP data:', hcps);
  }, [hcps]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddFollowUp = (suggestion) => {
    setFormData((prev) => ({
      ...prev,
      follow_up: prev.follow_up ? `${prev.follow_up}\n${suggestion}` : suggestion,
    }));
  };

  const handleAddMaterial = () => {
    const material = window.prompt('Search or enter a material name:');
    if (material) {
      setFormData((prev) => ({
        ...prev,
        materials_shared: [...prev.materials_shared, material],
      }));
    }
  };

  const handleAddSample = () => {
    const sample = window.prompt('Enter sample name:');
    if (sample) {
      setFormData((prev) => ({
        ...prev,
        samples_distributed: [...prev.samples_distributed, sample],
      }));
    }
  };

const handleChatSend = async () => {
  if (!chatInput.trim() || chatLoading) return;

  const userMessage = chatInput.trim();
  const updatedMessages = [...chatMessages, { role: 'user', text: userMessage }];

  setChatMessages(updatedMessages);
  setChatInput('');
  setChatLoading(true);

  try {
    // CHANGE THIS URL TO MATCH YOUR BACKEND ENDPOINT
    const response = await fetch('http://localhost:8000/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        hcp_id: formData.hcp_id || null,
        context: {
          interaction_type: formData.interaction_type,
          topics: formData.topics,
          sentiment: formData.sentiment,
          attendees: formData.attendees,
        }
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'AI assistant request failed');
    }

    const data = await response.json();
    
    // The agent returns 'response' field, not 'reply'
    setChatMessages((prev) => [...prev, { 
      role: 'assistant', 
      text: data.response || data.reply || 'I processed your request.' 
    }]);

    // Auto-fill form fields if AI suggests
    if (data.suggested_fields) {
      setFormData((prev) => ({
        ...prev,
        ...data.suggested_fields,
      }));
    }

  } catch (err) {
    console.error('AI assistant error:', err);
    setChatMessages((prev) => [
      ...prev,
      { role: 'assistant', text: `⚠️ Sorry, something went wrong: ${err.message}` },
    ]);
  } finally {
    setChatLoading(false);
  }
};

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.hcp_id) {
      alert('⚠️ Please select an HCP first!');
      return;
    }
    const payload = {
        hcp_id: Number(formData.hcp_id),
        interaction_type: formData.interaction_type,
        date: `${formData.date}T${formData.time}:00`,
        topics: formData.topics,
        summary: formData.summary,
        sentiment: formData.sentiment,
        outcomes: formData.outcomes,
        follow_up: formData.follow_up,

        materials_shared: formData.materials_shared.join(", "),
        samples_distributed: formData.samples_distributed.join(", "),
      };
      
    const result = await dispatch(logInteraction(payload));
    if (result.meta.requestStatus === 'fulfilled') {
      alert('✅ Interaction logged successfully!');
      setFormData((prev) => ({
        ...prev,
        attendees: '',
        topics: '',
        summary: '',
        outcomes: '',
        follow_up: '',
        materials_shared: [],
        samples_distributed: [],
      }));
    }
  };

  const hcpOptions = hcps.map((hcp) => ({
    value: hcp.id,
    label: `${hcp.name} - ${hcp.specialty || 'No Specialty'}`,
  }));

  console.log('🎯 Generated HCP Options:', hcpOptions.length, 'options');

  return (
    <div className="ihf-page">
      <h2 className="ihf-title">Log HCP Interaction</h2>

      <div className="ihf-grid">
        {/* ---------------- LEFT: Interaction Details ---------------- */}
        <section className="ihf-card">
          <h3 className="ihf-card-header">Interaction Details</h3>

          <form onSubmit={handleSubmit}>
            {error && (
              <div className="ihf-error-banner">❌ Error loading HCPs: {error}</div>
            )}

            <div className="ihf-row">
              <div className="ihf-field">
                <label>HCP Name</label>
                <Select
                  classNamePrefix="ihf-select"
                  options={hcpOptions}
                  value={hcpOptions.find((opt) => opt.value === formData.hcp_id) || null}
                  onChange={(selected) =>
                    setFormData((prev) => ({ ...prev, hcp_id: selected ? selected.value : '' }))
                  }
                  placeholder={hcpLoading ? 'Loading HCPs...' : 'Search or select HCP...'}
                  isClearable
                  isLoading={hcpLoading}
                  noOptionsMessage={() => (hcpLoading ? 'Loading...' : 'No HCPs found. Please add some.')}
                />
                {!hcpLoading && hcps.length === 0 && (
                  <div className="ihf-hint">💡 No HCPs available. Please add HCPs to the database.</div>
                )}
              </div>

              <div className="ihf-field">
                <label>Interaction Type</label>
                <select
                  name="interaction_type"
                  value={formData.interaction_type}
                  onChange={handleChange}
                >
                  <option value="Meeting">Meeting</option>
                  <option value="Call">Call</option>
                  <option value="Email">Email</option>
                  <option value="Visit">Visit</option>
                </select>
              </div>
            </div>

            <div className="ihf-row">
              <div className="ihf-field">
                <label>Date</label>
                <div className="ihf-input-icon">
                  <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    required
                  />
                  {/* <Calendar size={16} className="ihf-icon" /> */}
                </div>
              </div>

              <div className="ihf-field">
                <label>Time</label>
                <div className="ihf-input-icon">
                  <input
                    type="time"
                    name="time"
                    value={formData.time}
                    onChange={handleChange}
                    required
                  />
                  {/* <Clock size={16} className="ihf-icon" /> */}
                </div>
              </div>
            </div>

            <div className="ihf-field">
              <label>Attendees</label>
              <input
                type="text"
                name="attendees"
                value={formData.attendees}
                onChange={handleChange}
                placeholder="Enter names or search..."
              />
            </div>

            <div className="ihf-field">
              <label>Topics Discussed</label>
              <div className="ihf-textarea-icon">
                <textarea
                  name="topics"
                  value={formData.topics}
                  onChange={handleChange}
                  placeholder="Enter key discussion points..."
                />
                <Mic size={16} className="ihf-icon ihf-icon-bottom" />
              </div>
            </div>

            <button type="button" className="ihf-pill-btn">
              <Sparkles size={14} />
              Summarize from Voice Note (Requires Consent)
            </button>

            <div className="ihf-subsection">
              <h4>Materials Shared / Samples Distributed</h4>

              <div className="ihf-list-row">
                <div className="ihf-list-header">
                  <span className="ihf-list-label">Materials Shared</span>
                  <button type="button" className="ihf-outline-btn" onClick={handleAddMaterial}>
                    <Search size={14} />
                    Search/Add
                  </button>
                </div>
                {formData.materials_shared.length === 0 ? (
                  <p className="ihf-empty">No materials added.</p>
                ) : (
                  <ul className="ihf-chip-list">
                    {formData.materials_shared.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="ihf-list-row">
                <div className="ihf-list-header">
                  <span className="ihf-list-label">Samples Distributed</span>
                  <button type="button" className="ihf-outline-btn" onClick={handleAddSample}>
                    <Plus size={14} />
                    Add Sample
                  </button>
                </div>
                {formData.samples_distributed.length === 0 ? (
                  <p className="ihf-empty">No samples added.</p>
                ) : (
                  <ul className="ihf-chip-list">
                    {formData.samples_distributed.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="ihf-field">
              <label>Observed/Inferred HCP Sentiment</label>
              <div className="ihf-sentiment-row">
                {[
                  { key: 'Positive', icon: '🙂' },
                  { key: 'Neutral', icon: '😐' },
                  { key: 'Negative', icon: '🙁' },
                ].map(({ key, icon }) => (
                  <label key={key} className="ihf-sentiment-option">
                    <input
                      type="radio"
                      name="sentiment"
                      value={key}
                      checked={formData.sentiment === key}
                      onChange={handleChange}
                    />
                    <span className="ihf-sentiment-icon">{icon}</span>
                    {key}
                  </label>
                ))}
              </div>
            </div>

            <div className="ihf-field">
              <label>Outcomes</label>
              <textarea
                name="outcomes"
                value={formData.outcomes}
                onChange={handleChange}
                placeholder="Key outcomes or agreements..."
              />
            </div>

            <div className="ihf-field">
              <label>Follow-up Actions</label>
              <textarea
                name="follow_up"
                value={formData.follow_up}
                onChange={handleChange}
                placeholder="Enter next steps or tasks..."
              />
            </div>

            <div className="ihf-ai-followups">
              <p className="ihf-ai-followups-title">AI Suggested Follow-ups:</p>
              <ul>
                {AI_SUGGESTED_FOLLOWUPS.map((suggestion) => (
                  <li key={suggestion}>
                    <button type="button" onClick={() => handleAddFollowUp(suggestion)}>
                      + {suggestion}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <button type="submit" className="btn-primary" disabled={loading || hcpLoading}>
              {loading ? 'Logging...' : 'Log Interaction'}
            </button>
          </form>
        </section>

        {/* ---------------- RIGHT: AI Assistant ---------------- */}
        <aside className="ihf-card ihf-ai-card">
          <div className="ihf-ai-header">
            <Sparkles size={16} className="ihf-ai-header-icon" />
            <div>
              <h3>AI Assistant</h3>
              <p>Log interaction via chat</p>
            </div>
          </div>

          <div className="ihf-ai-chat">
            {chatMessages.length === 0 ? (
              <div className="ihf-ai-bubble">
                Log interaction details here (e.g., "Met Dr. Smith, discussed Product X
                efficacy, positive sentiment, shared brochure") or ask for help.
              </div>
            ) : (
              chatMessages.map((m, i) => (
                <div key={i} className={`ihf-ai-bubble ihf-ai-bubble-${m.role}`}>
                  {m.text}
                </div>
              ))
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="ihf-ai-input-row">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleChatSend(); } }}
              placeholder="Describe interaction..."
            />
            {/* <button type="button" onClick={handleChatSend}>
              <AlertTriangle size={14} />
              Log
            </button> */}
            <button type="button" onClick={handleChatSend} disabled={chatLoading} > {chatLoading ? "Thinking..." : "Log"} </button>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default InteractionForm;