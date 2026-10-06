import React, { useState, useEffect } from 'react';
import {
  createMedicineReminder,
  getMedicineReminders,
  getTodayMedicineReminders,
  updateMedicineReminder,
  deleteMedicineReminder
} from '../services/api';
import {
  Pill,
  Clock,
  Plus,
  Trash2,
  Edit2,
  CheckCircle2,
  AlertCircle,
  ShieldAlert,
  Calendar,
  ToggleLeft,
  ToggleRight,
  X,
  Bell
} from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const MedicineReminders = () => {
  const [activeTab, setActiveTab] = useState('today'); // 'today' or 'all'
  const [reminders, setReminders] = useState([]);
  const [todayReminders, setTodayReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeAlert, setActiveAlert] = useState(null);

  // Form Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const getTodayString = () => new Date().toISOString().split('T')[0];

  const [formData, setFormData] = useState({
    medicine_name: '',
    dosage: '',
    frequency: 'Daily',
    start_date: getTodayString(),
    end_date: '',
    reminder_time: '08:00 AM',
    notes: '',
    active: true,
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [allList, todayList] = await Promise.all([
        getMedicineReminders(),
        getTodayMedicineReminders(),
      ]);
      setReminders(allList || []);
      setTodayReminders(todayList || []);
    } catch (err) {
      console.error('Failed to load medicine reminders:', err);
      setError(err.message || 'Failed to fetch medication reminders.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Live Medication Alert Notification Engine
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    const checkReminders = () => {
      const now = new Date();
      const currentHours = now.getHours();
      const currentMinutes = now.getMinutes();

      const period = currentHours >= 12 ? 'PM' : 'AM';
      const h12 = currentHours % 12 || 12;
      const h12Str = h12 < 10 ? `0${h12}` : `${h12}`;
      const mStr = currentMinutes < 10 ? `0${currentMinutes}` : `${currentMinutes}`;

      const time12_pad = `${h12Str}:${mStr} ${period}`;
      const time12_nopad = `${h12}:${mStr} ${period}`;
      const time24 = `${currentHours < 10 ? '0' : ''}${currentHours}:${mStr}`;

      const todayStr = getTodayString();

      reminders.forEach((rec) => {
        if (!rec.active) return;
        if (rec.start_date > todayStr) return;
        if (rec.end_date && rec.end_date < todayStr) return;

        const rTime = rec.reminder_time.trim().toUpperCase();
        if (
          rTime === time12_pad.toUpperCase() ||
          rTime === time12_nopad.toUpperCase() ||
          rTime === time24
        ) {
          const alertKey = `alert_fired_${rec.id}_${todayStr}_${mStr}`;
          if (!sessionStorage.getItem(alertKey)) {
            sessionStorage.setItem(alertKey, 'true');

            setActiveAlert(rec);

            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification(`🔔 Medication Reminder: ${rec.medicine_name}`, {
                body: `Time to take ${rec.dosage} (${rec.frequency}). ${rec.notes || ''}`,
              });
            }
          }
        }
      });
    };

    checkReminders();
    const interval = setInterval(checkReminders, 15000);
    return () => clearInterval(interval);
  }, [reminders]);

  const openAddModal = () => {
    setEditingId(null);
    setFormData({
      medicine_name: '',
      dosage: '',
      frequency: 'Daily',
      start_date: getTodayString(),
      end_date: '',
      reminder_time: '08:00 AM',
      notes: '',
      active: true,
    });
    setIsModalOpen(true);
    setError('');
  };

  const openEditModal = (rec) => {
    setEditingId(rec.id);
    setFormData({
      medicine_name: rec.medicine_name,
      dosage: rec.dosage,
      frequency: rec.frequency,
      start_date: rec.start_date,
      end_date: rec.end_date || '',
      reminder_time: rec.reminder_time,
      notes: rec.notes || '',
      active: rec.active,
    });
    setIsModalOpen(true);
    setError('');
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
  };

  const handleChange = (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: val });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.medicine_name.trim()) {
      setError('Medicine name is required.');
      return;
    }
    if (!formData.dosage.trim()) {
      setError('Dosage is required.');
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        ...formData,
        end_date: formData.end_date ? formData.end_date : null,
      };

      if (editingId) {
        await updateMedicineReminder(editingId, payload);
      } else {
        await createMedicineReminder(payload);
      }

      closeModal();
      await loadData();
    } catch (err) {
      setError(err.message || 'Failed to save medicine reminder.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = async (rec) => {
    try {
      await updateMedicineReminder(rec.id, { active: !rec.active });
      await loadData();
    } catch (err) {
      console.error('Failed to toggle reminder status:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this medicine reminder?')) return;

    try {
      await deleteMedicineReminder(id);
      await loadData();
    } catch (err) {
      console.error('Failed to delete medicine reminder:', err);
    }
  };

  const displayedList = activeTab === 'today' ? todayReminders : reminders;

  return (
    <div style={{ maxWidth: 1050, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                backgroundColor: 'rgba(20, 184, 166, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary-500)',
              }}
            >
              <Pill size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Medicine Reminders & Schedule
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Track your prescribed medications, daily dosage schedule, and reminder alerts
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <PageGuideModal
              title="Medication Reminders & Alarm System"
              purpose="Allows patients to maintain medication schedules, track daily dosages, and receive active in-browser popup alarms and notifications."
              howItWorks={[
                "Saves medication schedules (Medicine Name, Dosage, Frequency, Reminder Time, Notes) in database.",
                "Background clock worker checks active reminders every 15 seconds against local system time.",
                "Triggers native HTML5 Browser Notifications and an active glowing alarm banner when reminder time matches current time."
              ]}
              howToUse={[
                "Click '+ Add Medicine Reminder' to enter medication details and reminder time.",
                "Toggle reminder switches ON/OFF to activate or pause alarm monitoring.",
                "Allow Browser Notifications when prompted to receive desktop popups even when tab is in background."
              ]}
            />

            <button className="btn btn-primary" onClick={openAddModal} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Plus size={18} />
              <span>Add Medicine Reminder</span>
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Active Live Alarm Alert Banner */}
      {activeAlert && (
        <div className="alert" style={{ marginBottom: '1.5rem', borderLeft: '6px solid #10b981', padding: '1rem 1.25rem', backgroundColor: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Bell size={24} style={{ color: '#10b981', flexShrink: 0 }} />
            <div>
              <h4 style={{ margin: 0, color: '#10b981', fontSize: '1.05rem', fontWeight: 700 }}>
                🔔 Medication Reminder Alert: {activeAlert.medicine_name} ({activeAlert.dosage})
              </h4>
              <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-main)', fontSize: '0.9rem' }}>
                It's <strong>{activeAlert.reminder_time}</strong>! Frequency: {activeAlert.frequency}. {activeAlert.notes ? `Special Notes: "${activeAlert.notes}"` : 'Please take your prescribed dosage now.'}
              </p>
            </div>
          </div>
          <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.35rem 0.85rem' }} onClick={() => setActiveAlert(null)}>
            Dismiss Alert
          </button>
        </div>
      )}

      {/* Tabs Bar */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        <button
          className={`btn ${activeTab === 'today' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('today')}
          style={{ fontSize: '0.9rem', padding: '0.45rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
        >
          <Clock size={16} />
          <span>Today's Reminders ({todayReminders.length})</span>
        </button>

        <button
          className={`btn ${activeTab === 'all' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('all')}
          style={{ fontSize: '0.9rem', padding: '0.45rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
        >
          <Pill size={16} />
          <span>All Medications ({reminders.length})</span>
        </button>
      </div>

      {/* Medication Reminders List */}
      <div style={{ marginBottom: '2.5rem' }}>
        {loading ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>
            Loading medicine reminders...
          </p>
        ) : displayedList.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '3.5rem 1rem',
              color: 'var(--text-muted)',
              backgroundColor: 'rgba(15, 23, 42, 0.4)',
              borderRadius: 'var(--radius-md)',
              border: '1px dashed var(--border-color)',
            }}
          >
            <Pill size={44} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
            <p style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-main)' }}>
              {activeTab === 'today' ? 'No medicine reminders today.' : 'No medication reminders configured.'}
            </p>
            <span style={{ fontSize: '0.85rem' }}>
              {activeTab === 'today'
                ? 'You have no active medications scheduled for today.'
                : 'Click "Add Medicine Reminder" above to set up your prescription schedule.'}
            </span>
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '1.25rem',
            }}
          >
            {displayedList.map((rec) => (
              <div
                key={rec.id}
                className="card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  opacity: rec.active ? 1 : 0.6,
                  borderColor: rec.active ? 'var(--border-color)' : 'rgba(30, 45, 74, 0.4)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div
                        style={{
                          background: rec.active ? 'rgba(20, 184, 166, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                          padding: '0.45rem',
                          borderRadius: 'var(--radius-sm)',
                          color: rec.active ? 'var(--primary-500)' : 'var(--text-muted)',
                        }}
                      >
                        <Pill size={18} />
                      </div>
                      <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {rec.medicine_name}
                      </h3>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span
                        className="badge"
                        style={{
                          backgroundColor: rec.active ? 'rgba(16, 185, 129, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                          color: rec.active ? '#10b981' : 'var(--text-muted)',
                          border: `1px solid ${rec.active ? 'rgba(16, 185, 129, 0.3)' : 'rgba(148, 163, 184, 0.3)'}`,
                        }}
                      >
                        {rec.active ? 'Active' : 'Disabled'}
                      </span>

                      <button
                        onClick={() => handleToggleActive(rec)}
                        title={rec.active ? 'Disable Reminder' : 'Enable Reminder'}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: rec.active ? 'var(--primary-500)' : 'var(--text-muted)' }}
                      >
                        {rec.active ? <ToggleRight size={26} /> : <ToggleLeft size={26} />}
                      </button>
                    </div>
                  </div>

                  <div style={{ fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.4rem', color: 'var(--text-muted)' }}>
                    <div>
                      <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>Dosage:</span> {rec.dosage}
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>Frequency:</span> {rec.frequency}
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>Reminder Time:</span>{' '}
                      <strong style={{ color: 'var(--primary-500)' }}>{rec.reminder_time}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>Schedule Period:</span>{' '}
                      {rec.start_date} {rec.end_date ? `to ${rec.end_date}` : '(Ongoing)'}
                    </div>
                    {rec.notes && (
                      <div style={{ fontStyle: 'italic', marginTop: '0.2rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.4rem 0.6rem', borderRadius: 4 }}>
                        "{rec.notes}"
                      </div>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1.25rem', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
                  <button
                    className="btn btn-secondary"
                    style={{ padding: '0.3rem 0.65rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                    onClick={() => openEditModal(rec)}
                  >
                    <Edit2 size={14} />
                    <span>Edit</span>
                  </button>

                  <button
                    className="btn"
                    style={{
                      padding: '0.3rem 0.65rem',
                      fontSize: '0.8rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      backgroundColor: 'rgba(239, 68, 68, 0.15)',
                      color: 'var(--accent-red)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                    }}
                    onClick={() => handleDelete(rec.id)}
                  >
                    <Trash2 size={14} />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Safety Disclaimer Banner */}
      <div
        style={{
          marginBottom: '2.5rem',
          padding: '0.85rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid var(--border-color)',
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-start',
        }}
      >
        <ShieldAlert size={20} style={{ minWidth: 20, color: 'var(--accent-amber)', marginTop: 2 }} />
        <span>
          <strong>Disclaimer:</strong> This module is a scheduling tool for your prescribed medications. HealthAI does not prescribe or verify medications, change dosages, or guarantee medication delivery. Always follow your doctor or pharmacist's exact instructions.
        </span>
      </div>

      {/* Add/Edit Modal */}
      {isModalOpen && (
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
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div className="card" style={{ maxWidth: 500, width: '100%', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {editingId ? 'Edit Medicine Reminder' : 'Add Medicine Reminder'}
              </h2>
              <button onClick={closeModal} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Medicine Name</label>
                <input
                  type="text"
                  name="medicine_name"
                  className="form-input"
                  placeholder="e.g. Metformin, Amoxicillin, Vitamin D"
                  value={formData.medicine_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Dosage</label>
                  <input
                    type="text"
                    name="dosage"
                    className="form-input"
                    placeholder="e.g. 500 mg, 1 tablet"
                    value={formData.dosage}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Frequency</label>
                  <select
                    name="frequency"
                    className="form-input"
                    value={formData.frequency}
                    onChange={handleChange}
                    required
                  >
                    <option value="Daily">Daily</option>
                    <option value="Twice Daily">Twice Daily</option>
                    <option value="Three Times Daily">Three Times Daily</option>
                    <option value="Weekly">Weekly</option>
                    <option value="As Needed">As Needed</option>
                  </select>
                </div>
              </div>

              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Start Date</label>
                  <input
                    type="date"
                    name="start_date"
                    className="form-input"
                    value={formData.start_date}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">End Date (Optional)</label>
                  <input
                    type="date"
                    name="end_date"
                    className="form-input"
                    value={formData.end_date}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Reminder Time</label>
                <input
                  type="text"
                  name="reminder_time"
                  className="form-input"
                  placeholder="e.g. 08:00 AM or 20:00"
                  value={formData.reminder_time}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Special Notes / Instructions</label>
                <textarea
                  name="notes"
                  className="form-input"
                  rows="2"
                  placeholder="e.g. Take after breakfast with water"
                  value={formData.notes}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  id="active"
                  name="active"
                  checked={formData.active}
                  onChange={handleChange}
                  style={{ accentColor: 'var(--primary-500)', width: 18, height: 18 }}
                />
                <label htmlFor="active" style={{ fontSize: '0.9rem', color: 'var(--text-main)', cursor: 'pointer' }}>
                  Enable reminder alert
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? 'Saving...' : editingId ? 'Update Reminder' : 'Save Reminder'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MedicineReminders;
