import React, { useState, useMemo, useEffect } from 'react';
import DestinationCard from './DestinationCard';
import ServiceCard from './ServiceCard';

const SearchResultList = ({ results }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;
  
  const [selectedProvince, setSelectedProvince] = useState('');
  const [selectedWard, setSelectedWard] = useState('');

  const displayResults = results || [];

  // Lấy danh sách Tỉnh/Thành phố duy nhất
  const availableProvinces = useMemo(() => {
    const provinces = new Set(displayResults.map(r => r.province_name).filter(Boolean));
    return Array.from(provinces).sort();
  }, [displayResults]);

  // Lấy danh sách Phường/Xã duy nhất dựa trên Tỉnh/Thành phố đã chọn
  const availableWards = useMemo(() => {
    let filtered = displayResults;
    if (selectedProvince) {
      filtered = filtered.filter(r => r.province_name === selectedProvince);
    }
    const wards = new Set(filtered.map(r => r.ward_name).filter(Boolean));
    return Array.from(wards).sort();
  }, [displayResults, selectedProvince]);

  // Lọc kết quả
  const filteredResults = useMemo(() => {
    return displayResults.filter(res => {
      if (selectedProvince && res.province_name !== selectedProvince) return false;
      if (selectedWard && res.ward_name !== selectedWard) return false;
      return true;
    });
  }, [displayResults, selectedProvince, selectedWard]);

  // Phân trang
  const totalPages = Math.ceil(filteredResults.length / itemsPerPage);
  const currentItems = filteredResults.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Reset trang về 1 khi đổi bộ lọc
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedProvince, selectedWard]);

  return (
    <div className="search-result-list">
      {/* Bộ lọc */}
      {(availableProvinces.length > 0 || availableWards.length > 0) && (
        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Tỉnh / Thành phố</label>
            <select 
              className="input-field" 
              style={{ width: '250px' }}
              value={selectedProvince} 
              onChange={(e) => { setSelectedProvince(e.target.value); setSelectedWard(''); }}
            >
              <option value="">-- Tất cả --</option>
              {availableProvinces.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Phường / Xã</label>
            <select 
              className="input-field" 
              style={{ width: '250px' }}
              value={selectedWard} 
              onChange={(e) => setSelectedWard(e.target.value)}
              disabled={!selectedProvince && availableWards.length === 0}
            >
              <option value="">-- Tất cả --</option>
              {availableWards.map(w => <option key={w} value={w}>{w}</option>)}
            </select>
          </div>
        </div>
      )}

      {/* Danh sách kết quả */}
      <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
          gap: '24px',
          marginTop: '10px'
      }}>
        {currentItems.length > 0 ? (
          currentItems.map((res, index) => (
            <div key={res.id || index}>
                <DestinationCard destination={res} />
            </div>
          ))
        ) : (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            Không tìm thấy địa điểm nào phù hợp với bộ lọc.
          </div>
        )}
      </div>

      {/* Phân trang */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '40px' }}>
          <button 
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="btn-premium btn-secondary"
            style={{ padding: '8px 16px', opacity: currentPage === 1 ? 0.5 : 1, cursor: currentPage === 1 ? 'not-allowed' : 'pointer' }}
          >
            Trước
          </button>
          
          {[...Array(totalPages)].map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentPage(i + 1)}
              className={currentPage === i + 1 ? "btn-premium btn-primary" : "btn-premium btn-secondary"}
              style={{ padding: '8px 16px', minWidth: '40px' }}
            >
              {i + 1}
            </button>
          ))}
          
          <button 
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="btn-premium btn-secondary"
            style={{ padding: '8px 16px', opacity: currentPage === totalPages ? 0.5 : 1, cursor: currentPage === totalPages ? 'not-allowed' : 'pointer' }}
          >
            Sau
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchResultList;
