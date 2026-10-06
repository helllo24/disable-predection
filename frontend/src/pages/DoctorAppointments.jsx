import React, { useState, useEffect } from 'react';
import {
  getDoctors,
  createAppointment,
  getUserAppointments,
  cancelAppointment
} from '../services/api';
import {
  Calendar,
  Clock,
  UserCheck,
  Stethoscope,
  Building,
  Phone,
  Mail,
  AlertCircle,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Plus,
  X,
  Filter
} from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const DoctorAppointments = () => {
  const [activeTab, setActiveTab] = useState('browse'); // 'browse' or 'my_appointments'
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [specializationFilter, setSpecializationFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Booking Modal State
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const getTodayString = () => new Date().toISOString().split('T')[0];

  const [bookingData, setBookingData] = useState({
    appointment_date: getTodayString(),
    appointment_time: '10:00 AM',
    reason: '',
    notes: '',
  });

  const availableTimeSlots = [
    '09:00 AM',
    '10:00 AM',
    '11:00 AM',
    '12:00 PM',
    '02:00 PM',
    '03:00 PM',
    '04:00 PM',
    '05:00 PM',
  ];

  const loadData = async () => {
    try {
      setLoading(true);
      const [docList, apptList] = await Promise.all([
        getDoctors(specializationFilter),
        getUserAppointments(),
      ]);
      setDoctors(docList || []);
      setAppointments(apptList || []);
    } catch (err) {
      console.error('Failed to load doctor appointments data:', err);
      setError(err.message || 'Failed to fetch doctor directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [specializationFilter]);

  const openBookingModal = (doctor) => {
    setSelectedDoctor(doctor);
    setBookingData({
      appointment_date: getTodayString(),
      appointment_time: '10:00 AM',
      reason: '',
      notes: '',
    });
    setIsModalOpen(true);
    setError('');
    setSuccessMessage('');
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedDoctor(null);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!bookingData.reason.trim()) {
      setError('Please provide a reason for consultation.');
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        doctor_id: selectedDoctor.id,
        appointment_date: bookingData.appointment_date,
        appointment_time: bookingData.appointment_time,
        reason: bookingData.reason.trim(),
        notes: bookingData.notes.trim() ? bookingData.notes.trim() : null,
      };

      await createAppointment(payload);
      setSuccessMessage(`Appointment successfully booked with Dr. ${selectedDoctor.name}!`);
      closeModal();
      setActiveTab('my_appointments');
      await loadData();
    } catch (err) {
      setError(err.message || 'Failed to book appointment.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelAppointment = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;

    try {
      await cancelAppointment(id);
      await loadData();
      setSuccessMessage('Appointment has been cancelled.');
    } catch (err) {
      setError(err.message || 'Failed to cancel appointment.');
    }
  };

  return (
    <div style={{ maxWidth: 1050, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
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
              <Calendar size={30} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Doctor Consultations & Appointments
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Schedule consultations with specialist healthcare professionals and manage your appointment calendar
              </p>
            </div>
          </div>

          <PageGuideModal
            title="Doctor Appointment Booking & Management"
            purpose="Enables patients to browse medical specialists, check real-time availability, schedule consultations, and manage upcoming or past appointments without scheduling conflicts."
            howItWorks={[
              "Filters available doctors by medical specialty (Endocrinology, Cardiology, Nephrology, General Medicine, Neurology).",
              "Enforces conflict prevention: verifies selected doctor does not already have an active appointment at chosen date & time.",
              "Persists appointments in SQLite backend with status tracking (Upcoming, Completed, Cancelled)."
            ]}
            howToUse={[
              "Browse specialist doctor profiles by department.",
              "Click 'Book Appointment', choose date and time slot, and confirm booking.",
              "Switch to 'My Appointments' tab to view upcoming schedule or cancel existing appointments."
            ]}
          />
        </div>
      </div>

      {/* Demo System Disclaimer Banner */}
      <div
        style={{
          marginBottom: '1.5rem',
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
          <strong>Project Demo System Notice:</strong> This is a sample appointment scheduling system built for project demonstration. Doctor profiles are demo data and do not connect to live hospital booking networks.
        </span>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <CheckCircle2 size={18} />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Tabs & Filter Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className={`btn ${activeTab === 'browse' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('browse')}
            style={{ fontSize: '0.9rem', padding: '0.45rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <Stethoscope size={16} />
            <span>Browse Doctors ({doctors.length})</span>
          </button>

          <button
            className={`btn ${activeTab === 'my_appointments' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('my_appointments')}
            style={{ fontSize: '0.9rem', padding: '0.45rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <Calendar size={16} />
            <span>My Appointments ({appointments.length})</span>
          </button>
        </div>

        {activeTab === 'browse' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
            <select
              className="form-input"
              style={{ width: 'auto', padding: '0.4rem 0.85rem', fontSize: '0.85rem' }}
              value={specializationFilter}
              onChange={(e) => setSpecializationFilter(e.target.value)}
            >
              <option value="">All Specializations</option>
              <option value="Cardiology">Cardiology</option>
              <option value="Endocrinology">Endocrinology</option>
              <option value="General Medicine">General Medicine</option>
              <option value="Neurology">Neurology</option>
              <option value="Pediatrics">Pediatrics</option>
            </select>
          </div>
        )}
      </div>

      {/* Main Tab Content */}
      {activeTab === 'browse' ? (
        /* Doctors Directory List */
        <div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>
              Loading doctor directory...
            </p>
          ) : doctors.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>
              No doctors found matching the selected specialization filter.
            </p>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                gap: '1.25rem',
                marginBottom: '2.5rem',
              }}
            >
              {doctors.map((doc) => (
                <div
                  key={doc.id}
                  className="card"
                  style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                      <span className="badge badge-patient">{doc.specialization}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{doc.qualification}</span>
                    </div>

                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                      {doc.name}
                    </h3>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Building size={14} style={{ color: 'var(--primary-500)' }} />
                        <span>{doc.clinic_hospital}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Calendar size={14} style={{ color: 'var(--primary-500)' }} />
                        <span>Days: {doc.available_days}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Clock size={14} style={{ color: 'var(--primary-500)' }} />
                        <span>Hours: {doc.available_times}</span>
                      </div>
                    </div>
                  </div>

                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                    onClick={() => openBookingModal(doc)}
                  >
                    Book Consultation
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* My Appointments List */
        <div>
          {loading ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>
              Loading your appointments...
            </p>
          ) : appointments.length === 0 ? (
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
              <Calendar size={44} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
              <p style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-main)' }}>
                No upcoming appointments.
              </p>
              <span style={{ fontSize: '0.85rem' }}>
                Browse our specialist doctors and book your consultation session.
              </span>
            </div>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                gap: '1.25rem',
                marginBottom: '2.5rem',
              }}
            >
              {appointments.map((appt) => {
                const isScheduled = appt.status === 'Scheduled';
                const isCancelled = appt.status === 'Cancelled';
                return (
                  <div
                    key={appt.id}
                    className="card"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      justify質Content: 'space-between',
                      opacity: isCancelled ? 0.6 : 1,
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: isScheduled
                              ? 'rgba(16, 185, 129, 0.15)'
                              : isCancelled
                              ? 'rgba(239, 68, 68, 0.15)'
                              : 'rgba(148, 163, 184, 0.15)',
                            color: isScheduled
                              ? '#10b981'
                              : isCancelled
                              ? 'var(--accent-red)'
                              : 'var(--text-muted)',
                            border: `1px solid ${
                              isScheduled
                                ? 'rgba(16, 185, 129, 0.3)'
                                : isCancelled
                                ? 'rgba(239, 68, 68, 0.3)'
                                : 'rgba(148, 163, 184, 0.3)'
                            }`,
                          }}
                        >
                          {appt.status}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Appt ID #{appt.id}
                        </span>
                      </div>

                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                        {appt.doctor ? appt.doctor.name : `Doctor ID #${appt.doctor_id}`}
                      </h3>
                      <div style={{ fontSize: '0.85rem', color: 'var(--primary-500)', fontWeight: 600, marginBottom: '0.85rem' }}>
                        {appt.doctor ? appt.doctor.specialization : ''}
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        <div>
                          <strong style={{ color: 'var(--text-main)' }}>Date & Time:</strong>{' '}
                          <span style={{ color: 'var(--primary-500)', fontWeight: 600 }}>
                            {appt.appointment_date} at {appt.appointment_time}
                          </span>
                        </div>
                        <div>
                          <strong style={{ color: 'var(--text-main)' }}>Location:</strong>{' '}
                          {appt.doctor ? appt.doctor.clinic_hospital : 'Clinic'}
                        </div>
                        <div>
                          <strong style={{ color: 'var(--text-main)' }}>Reason:</strong> {appt.reason}
                        </div>
                      </div>
                    </div>

                    {isScheduled && (
                      <div style={{ marginTop: '1.25rem', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', textAlign: 'right' }}>
                        <button
                          className="btn"
                          style={{
                            padding: '0.35rem 0.75rem',
                            fontSize: '0.8rem',
                            backgroundColor: 'rgba(239, 68, 68, 0.15)',
                            color: 'var(--accent-red)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                          }}
                          onClick={() => handleCancelAppointment(appt.id)}
                        >
                          Cancel Appointment
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Booking Modal */}
      {isModalOpen && selectedDoctor && (
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
          <div className="card" style={{ maxWidth: 520, width: '100%', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Book Doctor Consultation
                </h2>
                <p style={{ fontSize: '0.85rem', color: 'var(--primary-500)' }}>
                  {selectedDoctor.name} ({selectedDoctor.specialization})
                </p>
              </div>
              <button onClick={closeModal} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleBookingSubmit}>
              <div className="form-group">
                <label className="form-label">Appointment Date</label>
                <input
                  type="date"
                  name="appointment_date"
                  className="form-input"
                  min={getTodayString()}
                  value={bookingData.appointment_date}
                  onChange={(e) => setBookingData({ ...bookingData, appointment_date: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Select Available Time Slot</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '0.5rem', marginTop: '0.35rem' }}>
                  {availableTimeSlots.map((slot) => (
                    <button
                      key={slot}
                      type="button"
                      className={`btn ${bookingData.appointment_time === slot ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ fontSize: '0.8rem', padding: '0.4rem 0.2rem', textAlign: 'center' }}
                      onClick={() => setBookingData({ ...bookingData, appointment_time: slot })}
                    >
                      {slot}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Reason for Consultation</label>
                <textarea
                  name="reason"
                  className="form-input"
                  rows="3"
                  placeholder="Describe your health symptoms, medical check-up goals, or consultation reason..."
                  value={bookingData.reason}
                  onChange={(e) => setBookingData({ ...bookingData, reason: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Additional Patient Notes (Optional)</label>
                <input
                  type="text"
                  name="notes"
                  className="form-input"
                  placeholder="e.g. Previous test results available"
                  value={bookingData.notes}
                  onChange={(e) => setBookingData({ ...bookingData, notes: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? 'Confirming Booking...' : 'Confirm Appointment Booking'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorAppointments;
