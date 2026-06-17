import React from 'react';
import { FiMapPin, FiCalendar, FiUsers, FiDollarSign } from 'react-icons/fi';

/**
 * TripForm — controlled form collecting core trip parameters.
 *
 * Props:
 *   formData  { startingLocation, destination, startDate, endDate, groupSize, budget }
 *   onChange  (field, value) => void
 *   onSubmit  (e) => void
 *   loading   boolean
 */
const LoadingProgress = () => {
  const [progress, setProgress] = React.useState(0);

  React.useEffect(() => {
    // animate up to 95% over ~30 seconds (300 steps of 100ms)
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return 95;
        return prev + (95 / 300);
      });
    }, 100);
    return () => clearInterval(interval);
  }, []);

  let stepText = "Khởi tạo AI...";
  if (progress > 15) stepText = "Đang phân tích yêu cầu & sở thích...";
  if (progress > 35) stepText = "Đang thu thập dữ liệu điểm đến...";
  if (progress > 55) stepText = "Đang lên lịch trình chi tiết từng ngày...";
  if (progress > 75) stepText = "Đang tính toán ngân sách & tối ưu hóa...";
  if (progress > 90) stepText = "Đang hoàn tất kế hoạch...";

  return (
    <div style={{ marginTop: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 500 }}>
        <span>{stepText}</span>
        <span>{Math.floor(progress)}%</span>
      </div>
      <div style={{ height: '8px', background: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
        <div style={{ 
          height: '100%', 
          width: `${progress}%`, 
          background: 'var(--primary)', 
          transition: 'width 0.1s linear',
          borderRadius: '4px'
        }}></div>
      </div>
    </div>
  );
};

const TripForm = ({ formData = {}, onChange, onSubmit, loading }) => {
  const { startingLocation = '', destination = [], startDate = '', endDate = '', groupSize = 2, budget = 2000000 } = formData;

  const [provinces, setProvinces] = React.useState([]);
  const [startProvince, setStartProvince] = React.useState('');
  const [startWard, setStartWard] = React.useState('');
  const [startWards, setStartWards] = React.useState([]);

  const [destProvince, setDestProvince] = React.useState('');
  const [destWard, setDestWard] = React.useState('');
  const [destWards, setDestWards] = React.useState([]);

  const destinations = Array.isArray(destination) ? destination : (destination ? [destination] : []);

  const addDestination = () => {
    if (!destProvince) return;
    const newDest = destWard ? `${destWard}, ${destProvince}` : destProvince;
    if (!destinations.includes(newDest)) {
      onChange?.('destination', [...destinations, newDest]);
    }
    setDestProvince('');
    setDestWard('');
  };

  const removeDestination = (idx) => {
    const newDests = [...destinations];
    newDests.splice(idx, 1);
    onChange?.('destination', newDests);
  };

  // Fetch all provinces on mount
  React.useEffect(() => {
    fetch('http://127.0.0.1:8000/destinations/api/provinces/')
      .then(res => res.json())
      .then(data => {
        if (data.success) setProvinces(data.provinces);
      })
      .catch(console.error);
  }, []);

  // Fetch wards when startProvince changes
  React.useEffect(() => {
    if (!startProvince) {
      setStartWards([]);
      return;
    }
    fetch(`http://127.0.0.1:8000/destinations/api/wards/?province=${encodeURIComponent(startProvince)}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) setStartWards(data.wards);
      })
      .catch(console.error);
  }, [startProvince]);

  // Fetch wards when destProvince changes
  React.useEffect(() => {
    if (!destProvince) {
      setDestWards([]);
      return;
    }
    fetch(`http://127.0.0.1:8000/destinations/api/wards/?province=${encodeURIComponent(destProvince)}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) setDestWards(data.wards);
      })
      .catch(console.error);
  }, [destProvince]);

  const field = (key) => ({
    value: formData[key] ?? '',
    onChange: (e) => onChange?.(key, e.target.value),
  });

  return (
    <div className="card-premium">
      <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-primary)' }}>
        <FiMapPin className="text-secondary" /> Lên kế hoạch chuyến đi
      </h3>

      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

        {/* Row 1: Starting Location */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
            📍 Điểm xuất phát
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <select
              className="input-field"
              required
              value={startProvince}
              onChange={(e) => {
                setStartProvince(e.target.value);
                setStartWard('');
                onChange?.('startingLocation', e.target.value);
              }}
            >
              <option value="" disabled>Chọn Tỉnh/Thành phố...</option>
              {provinces.map(p => <option key={`start-prov-${p}`} value={p}>{p}</option>)}
            </select>
            <select
              className="input-field"
              required={startWards.length > 0}
              value={startWard}
              onChange={(e) => {
                setStartWard(e.target.value);
                onChange?.('startingLocation', `${e.target.value}, ${startProvince}`);
              }}
              disabled={!startProvince || startWards.length === 0}
            >
              <option value="" disabled>Chọn Quận/Huyện/Phường...</option>
              {startWards.map(w => <option key={`start-ward-${w}`} value={w}>{w}</option>)}
            </select>
          </div>
        </div>

        {/* Row 1.5: Destination */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
            🎯 Điểm đến (có thể thêm nhiều nơi)
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '10px' }}>
            <select
              className="input-field"
              required={destinations.length === 0}
              value={destProvince}
              onChange={(e) => {
                setDestProvince(e.target.value);
                setDestWard('');
              }}
            >
              <option value="" disabled>Chọn Tỉnh/Thành phố...</option>
              {provinces.map(p => <option key={`dest-prov-${p}`} value={p}>{p}</option>)}
            </select>
            <select
              className="input-field"
              value={destWard}
              onChange={(e) => setDestWard(e.target.value)}
              disabled={!destProvince || destWards.length === 0}
            >
              <option value="">Chọn Quận/Huyện/Phường (Tuỳ chọn)</option>
              {destWards.map(w => <option key={`dest-ward-${w}`} value={w}>{w}</option>)}
            </select>
            <button 
              type="button" 
              onClick={addDestination}
              disabled={!destProvince}
              style={{
                padding: '0 16px', borderRadius: '8px', background: 'var(--primary)', color: 'white',
                border: 'none', cursor: destProvince ? 'pointer' : 'not-allowed', fontWeight: 600, opacity: destProvince ? 1 : 0.5
              }}
            >
              Thêm
            </button>
          </div>
          
          {destinations.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '10px' }}>
              {destinations.map((dest, idx) => (
                <div key={idx} style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '6px 12px', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--primary)',
                  borderRadius: '16px', fontSize: '0.85rem', fontWeight: 500
                }}>
                  {dest}
                  <button 
                    type="button" 
                    onClick={() => removeDestination(idx)}
                    style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', padding: '0 4px', fontSize: '1rem', display: 'flex' }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Row 2: Dates */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiCalendar style={{ verticalAlign: 'middle', marginRight: 4 }} /> Ngày đi
            </label>
            <input
              type="date"
              className="input-field"
              required
              {...field('startDate')}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiCalendar style={{ verticalAlign: 'middle', marginRight: 4 }} /> Ngày về
            </label>
            <input
              type="date"
              className="input-field"
              required
              {...field('endDate')}
            />
          </div>
        </div>

        {/* Row 3: Group size + Budget */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiUsers style={{ verticalAlign: 'middle', marginRight: 4 }} /> Số người đi
            </label>
            <input
              type="number"
              min={1}
              max={20}
              className="input-field"
              placeholder="2"
              {...field('groupSize')}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
              <FiDollarSign style={{ verticalAlign: 'middle', marginRight: 4 }} /> Tổng ngân sách (VNĐ)
            </label>
            <input
              type="number"
              min={100000}
              step={100000}
              className="input-field"
              placeholder="2000000"
              {...field('budget')}
            />
          </div>
        </div>

        {/* Row 4: Description (optional) */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 500 }}>
            ✍️ Mô tả chuyến đi mong muốn <span style={{ color: 'var(--text-secondary)' }}>(không bắt buộc)</span>
          </label>
          <textarea
            className="input-field"
            rows={3}
            placeholder="VD: Mình muốn đi chill gần biển, ăn hải sản ngon và ngắm cảnh đẹp…"
            style={{ resize: 'vertical', fontFamily: 'inherit' }}
            {...field('userDesInput')}
          />
        </div>

        {loading ? (
          <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: '20px', borderRadius: '12px', border: '1px solid var(--primary)', marginTop: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px', fontWeight: 600, color: 'var(--primary)', fontSize: '1.1rem' }}>
              <span className="spinner" style={{ borderColor: 'var(--primary)', borderTopColor: 'transparent', width: '20px', height: '20px', borderWidth: '3px' }} />
              AI đang xử lý kế hoạch...
            </div>
            <LoadingProgress />
          </div>
        ) : (
          <button
            type="submit"
            className="btn-premium btn-primary"
            style={{ width: '100%', fontSize: '1rem', padding: '14px', position: 'relative' }}
          >
            ✨ Tạo kế hoạch
          </button>
        )}
      </form>
    </div>
  );
};

export default TripForm;
