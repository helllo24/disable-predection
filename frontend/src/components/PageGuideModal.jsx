import React, { useState } from 'react';
import { HelpCircle, X, Info, Cog, CheckCircle2 } from 'lucide-react';

const PageGuideModal = ({ title, purpose, howItWorks, howToUse }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('purpose');

  return (
    <>
      {/* Info Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="btn btn-secondary"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          fontSize: '0.85rem',
          padding: '0.4rem 0.85rem',
          borderColor: 'var(--primary-500)',
          color: 'var(--primary-500)',
          backgroundColor: 'rgba(20, 184, 166, 0.08)'
        }}
        title="Click for page explanation & usage guide"
      >
        <HelpCircle size={16} />
        <span>Page Info & Guide</span>
      </button>

      {/* Guide Modal Backdrop */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            padding: '1rem',
          }}
        >
          <div
            className="card"
            style={{
              maxWidth: 620,
              width: '100%',
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--primary-500)',
              borderWidth: 1,
              position: 'relative',
              maxHeight: '90vh',
              overflowY: 'auto'
            }}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <div style={{ backgroundColor: 'rgba(20, 184, 166, 0.15)', padding: '0.45rem', borderRadius: 'var(--radius-sm)', color: 'var(--primary-500)' }}>
                  <Info size={22} />
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-main)' }}>
                    {title} — User & Technical Guide
                  </h3>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Comprehensive explanation of features, backend mechanics, and usage instructions
                  </span>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 4 }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Tabs */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              <button
                className={`btn ${activeTab === 'purpose' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('purpose')}
                style={{ fontSize: '0.85rem', padding: '0.35rem 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <Info size={14} />
                <span>What This Page Does</span>
              </button>

              <button
                className={`btn ${activeTab === 'mechanics' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('mechanics')}
                style={{ fontSize: '0.85rem', padding: '0.35rem 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <Cog size={14} />
                <span>How It Works Behind Scenes</span>
              </button>

              <button
                className={`btn ${activeTab === 'usage' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('usage')}
                style={{ fontSize: '0.85rem', padding: '0.35rem 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <CheckCircle2 size={14} />
                <span>How To Use Step-by-Step</span>
              </button>
            </div>

            {/* Modal Content Sections */}
            <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.6 }}>
              {activeTab === 'purpose' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ fontWeight: 600, color: 'var(--primary-500)', fontSize: '0.95rem' }}>
                    📌 Page Purpose & Clinical Scope:
                  </div>
                  <p style={{ margin: 0, color: 'var(--text-main)' }}>{purpose}</p>
                </div>
              )}

              {activeTab === 'mechanics' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ fontWeight: 600, color: 'var(--primary-500)', fontSize: '0.95rem' }}>
                    ⚙️ Technical Implementation & Backend Logic:
                  </div>
                  {Array.isArray(howItWorks) ? (
                    <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                      {howItWorks.map((item, idx) => (
                        <li key={idx} style={{ marginBottom: '0.4rem' }}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ margin: 0 }}>{howItWorks}</p>
                  )}
                </div>
              )}

              {activeTab === 'usage' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ fontWeight: 600, color: 'var(--primary-500)', fontSize: '0.95rem' }}>
                    💡 Step-by-Step Usage Instructions:
                  </div>
                  {Array.isArray(howToUse) ? (
                    <ol style={{ margin: 0, paddingLeft: '1.25rem' }}>
                      {howToUse.map((item, idx) => (
                        <li key={idx} style={{ marginBottom: '0.4rem' }}>{item}</li>
                      ))}
                    </ol>
                  ) : (
                    <p style={{ margin: 0 }}>{howToUse}</p>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem', paddingTop: '0.85rem', borderTop: '1px solid var(--border-color)' }}>
              <button className="btn btn-primary" onClick={() => setIsOpen(false)} style={{ padding: '0.35rem 1.25rem', fontSize: '0.85rem' }}>
                Got It, Close Guide
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PageGuideModal;
