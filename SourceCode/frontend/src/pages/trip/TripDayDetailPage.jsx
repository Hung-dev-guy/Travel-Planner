import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiMapPin, FiTarget, FiCoffee, FiHome, FiNavigation, FiDollarSign, FiZap } from 'react-icons/fi';
import destinationService from '../../services/destinationService';
import DestinationCard from '../../components/search/DestinationCard';

const fmt = (n) => Number(n || 0).toLocaleString('vi-VN');
const fmtTime = (t) => {
  if (!t) return '';
  if (t.includes('T')) return t.split('T')[1].substring(0, 5);
  return t.length > 5 ? t.substring(0, 5) : t;
};

const itemIcon = (type) => {
  const map = { 
    activity: <FiTarget />, 
    meal: <FiCoffee />, 
    accommodation: <FiHome />, 
    transportation: <FiNavigation />, 
    transport: <FiNavigation /> 
  };
  return map[type?.toLowerCase()] || <FiTarget />;
};

const typeBadgeColor = (type) => {
  const map = {
    activity: { bg: 'rgba(16,185,129,0.12)', color: '#10b981' },
    meal: { bg: 'rgba(245,158,11,0.12)', color: '#f59e0b' },
    accommodation: { bg: 'rgba(139,92,246,0.12)', color: '#8b5cf6' },
    transportation: { bg: 'rgba(59,130,246,0.12)', color: '#3b82f6' },
    transport: { bg: 'rgba(59,130,246,0.12)', color: '#3b82f6' },
  };
  return map[type] || { bg: 'rgba(100,116,139,0.12)', color: '#64748b' };
};

const TripDayDetailPage = () => {
  const { dayId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // Prefer real day data from router state; fall back to placeholder
  const dayData = location.state?.dayData;
  const tripOverview = location.state?.tripOverview;

  // ── Fallback placeholder ────────────────────────────────────────────────────
  if (!dayData) {
    return (
      <div style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 16 }}>Không tìm thấy chi tiết Ngày {dayId}</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
          Vui lòng truy cập từ trang kế hoạch chuyến đi để xem dữ liệu lịch trình thực tế.
        </p>
        <button className="btn-premium btn-primary" onClick={() => navigate('/trip-plan')}>
          ← Quay lại Lịch trình
        </button>
      </div>
    );
  }

  const { day, date, title, items = [], day_summary = {} } = dayData;

  // Tự động tính toán các thông số thay vì phụ thuộc hoàn toàn vào LLM sinh ra
  const calcTotalCost = items.reduce((acc, item) => acc + (Number(item.cost) || 0), 0);
  const calcActs = items.filter(i => ['activity', 'sightseeing'].includes(i.type?.toLowerCase())).length;
  const calcMeals = items.filter(i => ['meal', 'food', 'restaurant'].includes(i.type?.toLowerCase())).length;
  const travelCount = items.filter(i => ['transportation', 'transport'].includes(i.type?.toLowerCase())).length;

  const displayCost = calcTotalCost > 0 ? calcTotalCost : (day_summary.total_cost || 0);
  const displayActs = calcActs > 0 ? calcActs : (day_summary.activities_count || 0);
  const displayMeals = calcMeals > 0 ? calcMeals : (day_summary.meals_count || 0);
  const displayTravel = day_summary.travel_time_hours || (travelCount * 0.5) || 1;
  const displayEnergy = day_summary.energy_level || 'moderate';

  const energyMap = {
    low: 'thư giãn',
    moderate: 'vừa phải',
    high: 'năng động'
  };
  const translatedEnergy = energyMap[displayEnergy?.toLowerCase()] || displayEnergy;

  const typeNameMap = {
    activity: 'Hoạt động',
    sightseeing: 'Tham quan',
    meal: 'Ăn uống',
    food: 'Ăn uống',
    restaurant: 'Nhà hàng',
    accommodation: 'Chỗ ở',
    stay: 'Chỗ ở',
    transportation: 'Di chuyển',
    transport: 'Di chuyển'
  };

  const [dbLocations, setDbLocations] = useState({});
  const [selectedDestination, setSelectedDestination] = useState(null);

  // Loại bỏ các tiền tố sinh ra bởi AI để lấy tên thật của địa điểm
  const getRealName = (name) => {
    if (!name) return '';
    const stripped = name.replace(/^(Check-in khách sạn:|Check-in|Di chuyển đến|Ăn sáng tại|Ăn trưa tại|Ăn tối tại|Ăn sáng|Ăn trưa|Ăn tối|Tham quan)\s+/i, '').trim();
    return stripped || name.trim();
  };

  useEffect(() => {
    // Lấy danh sách locations từ database để map ảnh và hiển thị chi tiết
    destinationService.getLocations('All', '').then(res => {
      if (res.data?.success) {
        const locations = res.data.results || res.data.locations || [];
        const locMap = {};
        
        items.forEach(item => {
           const itemName = item.name?.toLowerCase() || '';
           const realItemName = getRealName(item.name).toLowerCase();
           const itemLocation = (typeof item.location === 'string' ? item.location : '').toLowerCase();
           
           // Tìm location tương ứng trong CSDL
           const matchedLoc = locations.find(loc => {
             const locName = loc.name?.toLowerCase();
             if (!locName || !realItemName) return false;
             
             // Chỉ match dựa trên tên địa điểm, tránh match nhầm địa chỉ (itemLocation)
             return realItemName.includes(locName) || locName.includes(realItemName);
           });
           
           if (matchedLoc) {
             locMap[item.name] = matchedLoc;
           }
        });
        setDbLocations(locMap);
      }
    }).catch(err => console.error('Error fetching DB locations:', err));
  }, [items]);

  return (
    <div className="content" style={{ paddingBottom: '60px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>

        {/* Back button */}
        <button
          onClick={() => navigate('/trip-plan', { state: location.state })}
          style={{
            marginBottom: 24,
            background: 'transparent',
            border: '1px solid var(--border-light)',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 16px',
            borderRadius: 8,
            fontSize: '0.875rem',
          }}
        >
          <FiArrowLeft /> Quay lại Lịch trình
        </button>

        {/* Header */}
        <header style={{ marginBottom: 32 }}>
          <div style={{ display: 'inline-block', background: 'var(--primary)', color: '#fff', padding: '4px 16px', borderRadius: 8, fontSize: '0.875rem', marginBottom: 12, fontWeight: 600 }}>
            Ngày {day} · {date?.split('T')[0] || date}
          </div>
          <h1 style={{ fontSize: '2rem', color: 'var(--text-primary)', marginBottom: 8 }}>{title}</h1>
          {tripOverview && (
            <p style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <FiMapPin /> {tripOverview.destination} · {tripOverview.group_size} người
            </p>
          )}
        </header>

        <div style={{
          display: 'flex',
          gap: 16,
          flexWrap: 'wrap',
          marginBottom: 28,
          padding: '14px 18px',
          background: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: 12,
          fontSize: '0.875rem',
        }}>
          <span style={{ display: 'flex', color: "var(--primary)", alignItems: 'center', gap: 4 }}><FiDollarSign /> <strong>{fmt(displayCost)} ₫</strong></span>
          <span style={{ display: 'flex', color: "var(--primary)", alignItems: 'center', gap: 4 }}><FiTarget /> <strong>{displayActs}</strong> hoạt động</span>
          <span style={{ display: 'flex', color: "var(--primary)", alignItems: 'center', gap: 4 }}><FiCoffee /> <strong>{displayMeals}</strong> bữa ăn</span>
          <span style={{ display: 'flex', color: "var(--primary)", alignItems: 'center', gap: 4 }}><FiClock /> <strong>{displayTravel}h</strong> di chuyển</span>
          <span style={{ display: 'flex', color: "var(--primary)", alignItems: 'center', gap: 4 }}><FiZap /> <strong style={{ textTransform: 'capitalize' }}>{translatedEnergy}</strong></span>
        </div>

        {/* Schedule items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {items.map((item, idx) => {
            const badge = typeBadgeColor(item.type);
            return (
              <div
                key={idx}
                className="card-premium"
                style={{ display: 'flex', gap: 20, alignItems: 'flex-start' }}
              >
                {/* Time column */}
                <div style={{ minWidth: 90, textAlign: 'center', flexShrink: 0 }}>
                  <div style={{ fontSize: '1.5rem' }}>{itemIcon(item.type)}</div>
                  <div style={{ fontSize: '0.8rem', color: '#0e9427ff', fontWeight: 700, marginTop: 4 }}>
                    {fmtTime(item.time_start)}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#008cffff', fontWeight: 700 }}>
                    → {fmtTime(item.time_end)}
                  </div>
                </div>

                {/* Content */}
                <div style={{ flex: 1, display: 'flex', gap: 16, flexDirection: window.innerWidth < 600 ? 'column' : 'row' }}>
                  {(() => {
                    let imgSrc = dbLocations[item.name]?.img_url || dbLocations[item.name]?.image || item.img_url;
                    if (!imgSrc || imgSrc.includes('default.jpg')) {
                      imgSrc = null;
                    }
                    if (imgSrc) {
                      return (
                        <div style={{ width: 120, height: 100, flexShrink: 0, borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border-light)' }}>
                          <img src={imgSrc} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        </div>
                      );
                    }
                    return null;
                  })()}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 6 }}>
                      <div>
                        <h3 style={{ margin: 0, color: 'var(--primary-text)', fontSize: '1.05rem' }}>{item.name}</h3>
                        <span style={{
                          display: 'inline-block',
                          marginTop: 4,
                          padding: '2px 10px',
                          borderRadius: 10,
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          background: badge.bg,
                          color: badge.color,
                        }}>
                          {typeNameMap[item.type?.toLowerCase()] || item.type}
                        </span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 700, color: 'var(--primary-color)', fontSize: '1rem' }}>
                          {fmt(item.cost)} ₫
                        </div>
                        {item.duration_minutes > 0 && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4, justifyContent: 'flex-end', marginTop: 2 }}>
                            <FiClock /> {Math.round(item.duration_minutes / 60 * 10) / 10}h
                          </div>
                        )}
                      </div>
                    </div>

                    {item.location && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 8 }}>
                        <FiMapPin /> {item.location}
                      </div>
                    )}

                    {item.description && (
                      <p style={{ margin: '8px 0 0', fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                        {item.description}
                      </p>
                    )}

                    {item.notes && (
                      <div style={{
                        marginTop: 10,
                        padding: '10px 14px',
                        background: 'rgba(16,185,129,0.08)',
                        borderRadius: 8,
                        borderLeft: '4px solid var(--primary)',
                        fontSize: '0.85rem',
                        color: 'var(--text-primary)',
                      }}>
                        <strong>Ghi chú:</strong> {item.notes}
                      </div>
                    )}

                    <div style={{ marginTop: '12px' }}>
                      <button 
                        onClick={() => setSelectedDestination(dbLocations[item.name] || {
                          id: `temp-${idx}`,
                          name: getRealName(item.name),
                          description: item.description || item.notes,
                          price: item.cost,
                          category: typeNameMap[item.type?.toLowerCase()] || item.type,
                          img_url: dbLocations[item.name]?.img_url || dbLocations[item.name]?.image || item.img_url
                        })}
                        className="btn-premium btn-secondary" 
                        style={{ padding: '6px 12px', fontSize: '0.8rem', background: 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)' }}
                      >
                        Xem thông tin
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {selectedDestination && (
        <DestinationCard 
          modalOnly={true} 
          destination={selectedDestination} 
          onClose={() => setSelectedDestination(null)} 
        />
      )}
    </div>
  );
};

export default TripDayDetailPage;
