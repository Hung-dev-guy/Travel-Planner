import React, { useState } from 'react';
import { FiMapPin, FiClock, FiStar, FiX, FiTag } from 'react-icons/fi';

const DestinationCard = ({ destination }) => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="card-premium" style={{ overflow: 'hidden', padding: 0 }}>
        <div style={{ height: '180px', background: 'var(--border-light)', position: 'relative', overflow: 'hidden' }}>
            {destination.image ? (
                <img 
                  src={destination.image} 
                  alt={destination.name} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                />
            ) : (
                <div style={{ width: '100%', height: '100%', background: 'var(--border-light)' }}></div>
            )}
            <div style={{ position: 'absolute', top: '12px', right: '12px', background: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
                {destination.rating || '4.8'} ★
            </div>
            {destination.category && (
              <div style={{ position: 'absolute', top: '12px', left: '12px', background: 'var(--primary)', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
                  {destination.category}
              </div>
            )}
        </div>
        <div style={{ padding: '20px' }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>{destination?.name || 'Điểm đến tuyệt đẹp'}</h3>
          <p style={{ 
            margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)',
            display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden'
          }}>
            {destination?.description || 'Khám phá sự kỳ diệu của nơi tuyệt vời này.'}
          </p>
          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 700, color: 'var(--primary)' }}>
                {destination.price ? `${Number(destination.price).toLocaleString('vi-VN')} ₫` : 'Miễn phí'}
              </span>
              <button 
                onClick={() => setShowModal(true)}
                className="btn-premium btn-secondary" 
                style={{ padding: '6px 12px', fontSize: '0.8rem' }}
              >
                Xem chi tiết
              </button>
          </div>
        </div>
      </div>

      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 9999, padding: '20px', backdropFilter: 'blur(5px)'
        }}>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: '16px',
            width: '100%', maxWidth: '600px',
            maxHeight: '90vh', overflowY: 'auto',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
            position: 'relative'
          }}>
            <button 
              onClick={() => setShowModal(false)}
              style={{
                position: 'absolute', top: '16px', right: '16px',
                background: 'rgba(0,0,0,0.5)', border: 'none', color: 'white',
                borderRadius: '50%', width: '32px', height: '32px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', zIndex: 10
              }}
            >
              <FiX size={20} />
            </button>
            
            <div style={{ height: '250px', position: 'relative' }}>
               <img src={destination.image} alt={destination.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
               <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'linear-gradient(transparent, rgba(0,0,0,0.8))', padding: '30px 20px 20px' }}>
                  <h2 style={{ margin: 0, color: 'white', fontSize: '1.8rem' }}>{destination.name}</h2>
                  <div style={{ display: 'flex', gap: '12px', marginTop: '8px', color: '#eee', fontSize: '0.9rem' }}>
                    {destination.province && <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><FiMapPin /> {destination.province}</span>}
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><FiStar color="#FFD700" /> {destination.rating || '4.8'}</span>
                  </div>
               </div>
            </div>

            <div style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)' }}>
                    {destination.price ? `${Number(destination.price).toLocaleString('vi-VN')} ₫` : 'Miễn phí'}
                  </div>
                  {destination.category && (
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '8px', padding: '4px 10px', background: 'var(--border-light)', borderRadius: '20px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      <FiTag /> {destination.category}
                    </div>
                  )}
                </div>
                <button className="btn-premium btn-primary" style={{ padding: '10px 20px' }}>
                   Thêm vào chuyến đi
                </button>
              </div>

              <div style={{ marginTop: '20px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: 'var(--text-primary)', fontSize: '1.1rem' }}>Về địa điểm này</h4>
                <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                  {destination.description || 'Chưa có mô tả chi tiết cho địa điểm này.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DestinationCard;
