import React, { useState, useEffect } from 'react';
import SearchResultList from '../components/search/SearchResultList';
import destinationService from '../services/destinationService';
import { FiRefreshCw, FiPlus, FiX, FiSearch } from 'react-icons/fi';

const SearchPage = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Trạng thái modal và form thêm địa điểm
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '', category: 'Stay', description: '', img_url: '', 
    estimatedPrice: 0, ward_name: '', province_name: '', latitude: '', longitude: ''
  });

  // Trạng thái modal thêm phương tiện
  const [showAddTransportModal, setShowAddTransportModal] = useState(false);
  const [transportData, setTransportData] = useState({
    from_city: '', to_city: '', type: 'xe khách',
    provider: '', price: 0, duration_hours: 0, departure_times: ''
  });
  
  // Dữ liệu dropdown
  const [provincesList, setProvincesList] = useState([]);
  const [wardsList, setWardsList] = useState([]);
  
  // Lấy thông tin user để check quyền admin
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  const isAdmin = user?.role === 'admin';

  const filters = [
    { id: 'All', label: 'Tất cả' },
    { id: 'Stay', label: 'Nơi lưu trú' },
    { id: 'Activity', label: 'Hoạt động' },
    { id: 'Food', label: 'Quán ăn/nhà hàng' },
    { id: 'Transport', label: 'Phương tiện' }
  ];

  useEffect(() => {
    const fetchLocations = async () => {
      setLoading(true);
      try {
        const res = await destinationService.getLocations(category, searchQuery);
        setLocations(res.data.results || []);
      } catch (error) {
        console.error("Error fetching locations:", error);
      } finally {
        setLoading(false);
      }
    };
    
    // Add a small debounce for search query
    const timeoutId = setTimeout(() => {
      fetchLocations();
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [category, searchQuery]);

  // Load provinces khi mở modal
  useEffect(() => {
    if (showAddModal) {
      destinationService.getProvinces()
        .then(res => setProvincesList(res.data.provinces || []))
        .catch(err => console.error(err));
    }
  }, [showAddModal]);

  // Load wards khi chọn province
  useEffect(() => {
    if (formData.province_name) {
      destinationService.getWards(formData.province_name)
        .then(res => setWardsList(res.data.wards || []))
        .catch(err => console.error(err));
      // Reset ward khi đổi province
      setFormData(prev => ({ ...prev, ward_name: '' }));
    } else {
      setWardsList([]);
    }
  }, [formData.province_name]);

  const handleAddLocation = async (e) => {
    e.preventDefault();
    try {
      await destinationService.addLocation(formData);
      alert('Thêm địa điểm thành công!');
      setShowAddModal(false);
      // Gọi lại API fetchLocations để refresh danh sách
      const res = await destinationService.getLocations(category, searchQuery);
      setLocations(res.data.results || []);
    } catch (err) {
      alert('Lỗi: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleAddTransport = async (e) => {
    e.preventDefault();
    try {
      await destinationService.addTransport(transportData);
      alert('Thêm phương tiện thành công!');
      setShowAddTransportModal(false);
      // Reset form
      setTransportData({
        from_city: '', to_city: '', type: 'xe khách',
        provider: '', price: 0, duration_hours: 0, departure_times: ''
      });
      // Optional refresh
      if (category === 'Transport' || category === 'All') {
        const res = await destinationService.getLocations(category, searchQuery);
        setLocations(res.data.results || []);
      }
    } catch (err) {
      alert('Lỗi: ' + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="search-page" style={{ maxWidth: 1200, margin: '0 auto' }}>
      <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '2rem', color: 'var(--primary)' }}>Khám phá các Điểm đến</h1>
          <div style={{ position: 'relative', marginTop: '20px', maxWidth: '600px' }}>
            <input 
              type="text" 
              className="input-field" 
              placeholder="Tìm kiếm nơi lưu trú, hoạt động, quán ăn, hoặc phương tiện..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ 
                paddingLeft: '54px', 
                height: '56px', 
                fontSize: '1.1rem', 
                boxShadow: 'var(--shadow-md)',
                borderRadius: '50px',
                border: '2px solid var(--primary)',
                backgroundColor: 'rgba(255, 255, 255, 0.65)',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                color: 'var(--text-main)',
                transition: 'all 0.3s ease'
              }}
            />
            <span style={{ position: 'absolute', left: '20px', top: '50%', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: 'var(--primary)' }}>
              <FiSearch size={22} />
            </span>
          </div>
        </div>
        
        {isAdmin && (
          <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
            <button 
              className="btn-premium btn-primary"
              onClick={() => setShowAddModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', fontSize: '1rem' }}
            >
              <FiPlus size={20} /> Thêm địa điểm
            </button>
            <button 
              className="btn-premium btn-secondary"
              onClick={() => setShowAddTransportModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', fontSize: '1rem', background: '#fff', border: '1px solid var(--primary)', color: 'var(--primary)' }}
            >
              <FiPlus size={20} /> Thêm phương tiện
            </button>
          </div>
        )}
      </header>
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '30px', flexWrap: 'wrap' }}>
          {filters.map(f => (
              <button 
                key={f.id} 
                onClick={() => setCategory(f.id)}
                className={category === f.id ? "btn-premium btn-primary" : "btn-premium btn-secondary"} 
                style={{ padding: '8px 20px', transition: 'all 0.2s' }}
              >
                {f.label}
              </button>
          ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          <FiRefreshCw size={32} style={{ animation: 'spin 1s linear infinite', color: 'var(--primary)' }} />
          <p style={{ marginTop: '16px' }}>Đang tải dữ liệu...</p>
          <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
        </div>
      ) : (
        <SearchResultList results={locations} />
      )}

      {/* Modal Thêm Địa Điểm cho Admin */}
      {showAddModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px'
        }}>
          <div className="card-premium" style={{ width: '100%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto', background: 'var(--bg-main)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ color: 'var(--primary)', margin: 0 }}>Thêm địa điểm mới</h2>
              <button onClick={() => setShowAddModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <FiX size={24} />
              </button>
            </div>
            
            <form onSubmit={handleAddLocation} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Tên địa điểm *</label>
                <input type="text" className="input-field" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Danh mục *</label>
                  <select className="input-field" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})}>
                    <option value="Stay">Khách sạn / Nơi ở</option>
                    <option value="Activity">Hoạt động tham quan</option>
                    <option value="Food">Quán ăn / Nhà hàng</option>
                    <option value="Transport">Di chuyển / Phương tiện</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Giá dự kiến (VNĐ)</label>
                  <input type="number" className="input-field" value={formData.estimatedPrice} onChange={e => setFormData({...formData, estimatedPrice: e.target.value})} />
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Tỉnh / Thành phố *</label>
                  <select 
                    className="input-field" 
                    required 
                    value={formData.province_name} 
                    onChange={e => setFormData({...formData, province_name: e.target.value})}
                  >
                    <option value="" disabled>-- Chọn Tỉnh / Thành phố --</option>
                    {provincesList.map(prov => (
                      <option key={prov} value={prov}>{prov}</option>
                    ))}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Phường / Xã / Huyện *</label>
                  <select 
                    className="input-field" 
                    required 
                    value={formData.ward_name} 
                    onChange={e => setFormData({...formData, ward_name: e.target.value})}
                    disabled={!formData.province_name}
                  >
                    <option value="" disabled>-- Chọn Phường / Xã --</option>
                    {wardsList.map(ward => (
                      <option key={ward} value={ward}>{ward}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Vĩ độ (Latitude)</label>
                  <input type="number" step="any" className="input-field" value={formData.latitude} onChange={e => setFormData({...formData, latitude: e.target.value})} placeholder="VD: 21.0285" />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Kinh độ (Longitude)</label>
                  <input type="number" step="any" className="input-field" value={formData.longitude} onChange={e => setFormData({...formData, longitude: e.target.value})} placeholder="VD: 105.8542" />
                </div>
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Link hình ảnh</label>
                <input type="text" className="input-field" placeholder="https://..." value={formData.img_url} onChange={e => setFormData({...formData, img_url: e.target.value})} />
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Mô tả chi tiết</label>
                <textarea className="input-field" rows="3" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})}></textarea>
              </div>
              
              <button type="submit" className="btn-premium btn-primary" style={{ marginTop: '10px' }}>Lưu vào Hệ thống</button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Thêm Phương Tiện */}
      {showAddTransportModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px'
        }}>
          <div className="card-premium" style={{ width: '100%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto', background: 'var(--bg-main)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ color: 'var(--primary)', margin: 0 }}>Thêm tuyến phương tiện</h2>
              <button onClick={() => setShowAddTransportModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <FiX size={24} />
              </button>
            </div>
            
            <form onSubmit={handleAddTransport} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Thành phố đi *</label>
                  <input type="text" className="input-field" required placeholder="VD: Hà Nội" value={transportData.from_city} onChange={e => setTransportData({...transportData, from_city: e.target.value})} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Thành phố đến *</label>
                  <input type="text" className="input-field" required placeholder="VD: Đà Nẵng" value={transportData.to_city} onChange={e => setTransportData({...transportData, to_city: e.target.value})} />
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Loại phương tiện *</label>
                  <select className="input-field" value={transportData.type} onChange={e => setTransportData({...transportData, type: e.target.value})}>
                    <option value="máy bay">Máy bay</option>
                    <option value="tàu hỏa">Tàu hỏa</option>
                    <option value="xe khách">Xe khách</option>
                    <option value="xe limousine">Xe Limousine</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Nhà cung cấp</label>
                  <input type="text" className="input-field" placeholder="VD: Vietnam Airlines, Phương Trang..." value={transportData.provider} onChange={e => setTransportData({...transportData, provider: e.target.value})} />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Giá vé (VNĐ) *</label>
                  <input type="number" className="input-field" required value={transportData.price} onChange={e => setTransportData({...transportData, price: e.target.value})} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Thời gian di chuyển (giờ)</label>
                  <input type="number" step="0.5" className="input-field" value={transportData.duration_hours} onChange={e => setTransportData({...transportData, duration_hours: e.target.value})} />
                </div>
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Giờ khởi hành (nếu có)</label>
                <input type="text" className="input-field" placeholder="VD: 08:00, 14:30, 22:00..." value={transportData.departure_times} onChange={e => setTransportData({...transportData, departure_times: e.target.value})} />
              </div>
              
              <button type="submit" className="btn-premium btn-primary" style={{ marginTop: '10px' }}>Lưu tuyến phương tiện</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
