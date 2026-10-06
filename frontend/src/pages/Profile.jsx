import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { User, Phone, Calendar, Heart, Shield, Save, CheckCircle2, AlertCircle } from 'lucide-react';
import PageGuideModal from '../components/PageGuideModal';

const Profile = () => {
  const { user, updateProfile } = useAuth();

  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    age: '',
    gender: 'Male',
    height: '',
    weight: '',
    blood_group: '',
    allergies: '',
    existing_conditions: '',
  });

  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        phone: user.phone || '',
        age: user.age !== undefined && user.age !== null ? String(user.age) : '',
        gender: user.gender || 'Male',
        height: user.height !== undefined && user.height !== null ? String(user.height) : '',
        weight: user.weight !== undefined && user.weight !== null ? String(user.weight) : '',
        blood_group: user.blood_group || '',
        allergies: user.allergies || '',
        existing_conditions: user.existing_conditions || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.full_name || !formData.phone || !formData.age || !formData.gender) {
      setError('Name, Phone, Age, and Gender are required.');
      return;
    }

    const ageNum = parseInt(formData.age, 10);
    if (isNaN(ageNum) || ageNum <= 0 || ageNum >= 120) {
      setError('Please enter a valid age between 1 and 120.');
      return;
    }

    const payload = {
      full_name: formData.full_name.trim(),
      phone: formData.phone.trim(),
      age: ageNum,
      gender: formData.gender,
      height: formData.height !== '' ? parseFloat(formData.height) : null,
      weight: formData.weight !== '' ? parseFloat(formData.weight) : null,
      blood_group: formData.blood_group !== '' ? formData.blood_group : null,
      allergies: formData.allergies !== '' ? formData.allergies.trim() : null,
      existing_conditions: formData.existing_conditions !== '' ? formData.existing_conditions.trim() : null,
    };

    setLoading(true);

    try {
      await updateProfile(payload);
      setSuccess('Patient profile updated successfully!');
    } catch (err) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 850, margin: '0 auto' }}>
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div
              style={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                backgroundColor: 'rgba(20, 184, 166, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary-500)',
              }}
            >
              <User size={32} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Patient Profile Settings
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                Manage your personal information, contact details, and medical metrics
              </p>
            </div>
          </div>

          <PageGuideModal
            title="Patient Profile & Health Details"
            purpose="Manages patient demographics, contact details, emergency contact info, and height/weight health baseline used across AI diagnostic modules."
            howItWorks={[
              "Stores user demographic data (Age, Gender, Height, Weight, Blood Group, Phone, Emergency Contact) in database.",
              "Profile height and weight auto-populate BMI and Diabetes risk prediction forms across the platform."
            ]}
            howToUse={[
              "Update your age, height, weight, and blood group.",
              "Fill in contact and emergency information.",
              "Click 'Save Changes' to update your medical baseline profile."
            ]}
          />
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <CheckCircle2 size={18} />
          <span>{success}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Personal & Account Details */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--primary-500)' }}>
            Personal Details
          </h2>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="full_name"
                className="form-input"
                value={formData.full_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email Address (Read-Only)</label>
              <input
                type="email"
                className="form-input"
                value={user?.email || ''}
                disabled
                style={{ opacity: 0.6, cursor: 'not-allowed' }}
              />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <input
                type="tel"
                name="phone"
                className="form-input"
                value={formData.phone}
                onChange={handleChange}
                required
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Age</label>
                <input
                  type="number"
                  name="age"
                  className="form-input"
                  value={formData.age}
                  onChange={handleChange}
                  min="1"
                  max="120"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Gender</label>
                <select
                  name="gender"
                  className="form-select"
                  value={formData.gender}
                  onChange={handleChange}
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Health & Medical Metrics */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--primary-500)' }}>
            Health Metrics & Medical History
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Height (cm)</label>
              <input
                type="number"
                step="0.1"
                name="height"
                className="form-input"
                placeholder="e.g. 175"
                value={formData.height}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Weight (kg)</label>
              <input
                type="number"
                step="0.1"
                name="weight"
                className="form-input"
                placeholder="e.g. 70"
                value={formData.weight}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Blood Group</label>
              <select
                name="blood_group"
                className="form-select"
                value={formData.blood_group}
                onChange={handleChange}
              >
                <option value="">Select Blood Group</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Known Allergies</label>
            <textarea
              name="allergies"
              className="form-input"
              rows={2}
              placeholder="List any known food, drug, or environmental allergies..."
              value={formData.allergies}
              onChange={handleChange}
              style={{ resize: 'vertical' }}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Pre-Existing Medical Conditions</label>
            <textarea
              name="existing_conditions"
              className="form-input"
              rows={2}
              placeholder="e.g., Hypertension, Asthma, Type 2 Diabetes..."
              value={formData.existing_conditions}
              onChange={handleChange}
              style={{ resize: 'vertical' }}
            />
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', padding: '0.85rem' }}
          disabled={loading}
        >
          <Save size={18} />
          {loading ? 'Saving Changes...' : 'Save Profile Changes'}
        </button>
      </form>
    </div>
  );
};

export default Profile;
