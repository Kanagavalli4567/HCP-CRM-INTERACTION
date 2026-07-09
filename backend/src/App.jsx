import React, { useState } from 'react';
import './App.css';
import InteractionForm from './components/InteractionForm';
import ChatInterface from './components/ChatInterface';
// import InteractionList from './components/InteractionList';

function App() {
  const [activeView, setActiveView] = useState('form'); // 'form' or 'chat'
  const [selectedHCP, setSelectedHCP] = useState(null);

  return (
    <div className="app">
      <header className="app-header">
        <h1>HCP CRM - Log Interaction</h1>
        <div className="header-actions">
          {/* <button 
            className={`view-toggle ${activeView === 'form' ? 'active' : ''}`}
            onClick={() => setActiveView('form')}
          >
            Form View
          </button>
          <button 
            className={`view-toggle ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            AI Chat
          </button> */}
        </div>
      </header>

      <main className="app-main">
        <div className="content-area">
          {activeView === 'form' ? (
            <InteractionForm selectedHCP={selectedHCP} />
          ) : (
            <ChatInterface selectedHCP={selectedHCP} />
          )}
        </div>
        
        <aside className="sidebar">
          {/* <InteractionList onSelectHCP={setSelectedHCP} /> */}
        </aside>
      </main>
    </div>
  );
}

export default App;