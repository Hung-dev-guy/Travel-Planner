import React from 'react';

const ServiceCard = ({ service }) => {
  return (
    <div className="card-premium" style={{ overflow: 'hidden', padding: 0 }}>
      <div style={{ height: '180px', background: 'var(--border-light)', position: 'relative', overflow: 'hidden' }}>
        {(service.img_url || service.image) ? (
            <img 
              src={service.img_url || service.image} 
              alt={service.name} 
              style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
            />
        ) : (
            <div style={{ width: '100%', height: '100%', background: 'var(--border-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ color: 'var(--text-muted)' }}>Chưa có hình ảnh</span>
            </div>
        )}
        <div style={{ position: 'absolute', top: '12px', right: '12px', display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
          <div style={{ background: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
              {service.rating || '4.8'} ★
          </div>
        </div>
        {service.category && (
          <div style={{ position: 'absolute', top: '12px', left: '12px', background: 'var(--primary)', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
              {service.category}
          </div>
        )}
      </div>
      <div style={{ padding: '20px' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>{service?.name || 'Phương tiện'}</h3>
        <p style={{ 
          margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden'
        }}>
          {service?.description || 'Dịch vụ vận chuyển uy tín.'}
        </p>
        <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 700, color: 'var(--primary)' }}>
              {service.price ? `${Number(service.price).toLocaleString('vi-VN')} ₫` : 'Miễn phí'}
            </span>
            <button 
              className="btn-premium btn-secondary" 
              style={{ padding: '6px 12px', fontSize: '0.8rem' }}
              onClick={() => alert(`Chi tiết phương tiện:\n- Tên: ${service.name}\n- Mô tả: ${service.description}\n- Giá: ${service.price} ₫`)}
            >
              Xem chi tiết
            </button>
        </div>
      </div>
    </div>
  );
};

export default ServiceCard;
