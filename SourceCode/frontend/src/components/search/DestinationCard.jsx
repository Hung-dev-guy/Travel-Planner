import React, { useState, useEffect } from 'react';
import { FiMapPin, FiClock, FiStar, FiX, FiTag, FiMessageSquare, FiEdit2, FiTrash2 } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import destinationService from '../../services/destinationService';

const DestinationCard = ({ destination }) => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [showTripsModal, setShowTripsModal] = useState(false);
  const [tripsWithLocation, setTripsWithLocation] = useState([]);
  const [loadingTrips, setLoadingTrips] = useState(false);
  
  // Edit logic
  const [showEditModal, setShowEditModal] = useState(false);
  const [editData, setEditData] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  
  const [provincesList, setProvincesList] = useState([]);
  const [wardsList, setWardsList] = useState([]);

  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;

  useEffect(() => {
    if (showModal && destination.id) {
      destinationService.getReviews(destination.id)
        .then(res => setReviews(res.data.reviews || []))
        .catch(err => console.error("Error fetching reviews", err));
    }
  }, [showModal, destination.id]);

  useEffect(() => {
    if (showEditModal) {
      destinationService.getProvinces()
        .then(res => setProvincesList(res.data.provinces || []))
        .catch(err => console.error(err));
    }
  }, [showEditModal]);

  useEffect(() => {
    if (editData.province_name) {
      destinationService.getWards(editData.province_name)
        .then(res => setWardsList(res.data.wards || []))
        .catch(err => console.error(err));
    } else {
      setWardsList([]);
    }
  }, [editData.province_name]);

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!user) {
      alert("Vui lòng đăng nhập để đánh giá.");
      return;
    }
    setIsSubmitting(true);
    try {
      const data = {
        locationId: destination.id,
        userName: user.full_name || user.username || 'User',
        rating: newReview.rating,
        comment: newReview.comment
      };
      const res = await destinationService.addReview(data);
      if (res.data.success) {
        const reviewsRes = await destinationService.getReviews(destination.id);
        setReviews(reviewsRes.data.reviews || []);
        setNewReview({ rating: 5, comment: '' });
        destination.rating = res.data.newRating; // Update UI immediately
        alert("Cảm ơn bạn đã đánh giá!");
      }
    } catch (err) {
      alert("Lỗi khi thêm đánh giá.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleShowTrips = async () => {
    setShowTripsModal(true);
    setLoadingTrips(true);
    try {
      const res = await destinationService.getTripsByLocation(destination.name);
      setTripsWithLocation(res.data.trips || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingTrips(false);
    }
  };

  const handleEditClick = (e) => {
    e.stopPropagation();
    setEditData({
      locationId: destination.id || destination.locationId,
      name: destination.name || '',
      category: destination.category || 'Stay',
      estimatedPrice: destination.price || destination.estimatedPrice || 0,
      province_name: destination.province_name || '',
      ward_name: destination.ward_name || '',
      latitude: destination.latitude || '',
      longitude: destination.longitude || '',
      description: destination.description || '',
      image: destination.image || ''
    });
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const res = await destinationService.editLocation(editData);
      if (res.data.success) {
        alert('Cập nhật thành công!');
        setShowEditModal(false);
        window.location.reload();
      } else {
        alert('Cập nhật thất bại: ' + res.data.error);
      }
    } catch (err) {
      console.error(err);
      alert('Đã xảy ra lỗi khi cập nhật.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteClick = async (e) => {
    e.stopPropagation();
    if (!window.confirm(`Bạn có chắc muốn xóa "${destination.name}" không?`)) return;
    
    try {
      const res = await destinationService.deleteLocation({ 
        locationId: destination.id || destination.locationId,
        name: destination.name
      });
      if (res.data.success) {
        alert('Đã xóa thành công!');
        window.location.reload();
      } else {
        alert('Lỗi: ' + res.data.error);
      }
    } catch (err) {
      console.error(err);
      if (err.response?.data?.error) {
        alert('Lỗi: ' + err.response.data.error);
      } else {
        alert('Đã xảy ra lỗi khi xóa.');
      }
    }
  };

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
            <div style={{ position: 'absolute', top: '12px', right: '12px', display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
              <div style={{ background: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
                  {destination.rating || '4.8'} ★
              </div>
              {user?.role === 'admin' && (
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button 
                      onClick={handleEditClick}
                      style={{ width: 28, height: 28, borderRadius: '50%', background: 'rgba(255, 255, 255, 0.85)', color: '#0194f3', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', backdropFilter: 'blur(4px)', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', transition: 'transform 0.2s' }}
                      title="Sửa"
                      onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'}
                      onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                  >
                      <FiEdit2 size={14} />
                  </button>
                  <button 
                      onClick={handleDeleteClick}
                      style={{ width: 28, height: 28, borderRadius: '50%', background: 'rgba(255, 255, 255, 0.85)', color: '#ef4444', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', backdropFilter: 'blur(4px)', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', transition: 'transform 0.2s' }}
                      title="Xóa"
                      onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'}
                      onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                  >
                      <FiTrash2 size={14} />
                  </button>
                </div>
              )}
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
            width: '100%', maxWidth: showTripsModal ? '1000px' : '600px',
            maxHeight: '90vh',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
            position: 'relative',
            display: 'flex',
            overflow: 'hidden',
            transition: 'max-width 0.3s ease'
          }}>
            {/* Left Content (Destination Details) */}
            <div style={{ flex: '0 0 600px', maxWidth: '600px', overflowY: 'auto', position: 'relative' }}>
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
                <button onClick={handleShowTrips} className="btn-premium btn-primary" style={{ padding: '10px 20px', fontSize: '0.9rem' }}>
                   Xem các chuyến đi đã sử dụng địa điểm này
                </button>
              </div>

              <div style={{ marginTop: '20px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: 'var(--text-primary)', fontSize: '1.1rem' }}>Về địa điểm này</h4>
                <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', margin: 0 }}>
                  {destination.description || 'Chưa có mô tả chi tiết cho địa điểm này.'}
                </p>
              </div>

              {/* Reviews Section */}
              <div style={{ marginTop: '30px', borderTop: '1px solid var(--border-light)', paddingTop: '20px' }}>
                <h4 style={{ margin: '0 0 15px 0', color: 'var(--text-primary)', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FiMessageSquare /> Đánh giá từ cộng đồng
                </h4>
                
                {/* Review Form */}
                <form onSubmit={handleSubmitReview} style={{ marginBottom: '20px', background: 'var(--bg-main)', padding: '15px', borderRadius: '8px' }}>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ marginRight: '10px', fontSize: '0.9rem', fontWeight: 600 }}>Chấm điểm:</label>
                    {[1, 2, 3, 4, 5].map(star => (
                      <FiStar 
                        key={star} 
                        size={20} 
                        style={{ cursor: 'pointer', fill: star <= newReview.rating ? '#FFD700' : 'none', color: star <= newReview.rating ? '#FFD700' : 'var(--text-muted)' }}
                        onClick={() => setNewReview({ ...newReview, rating: star })}
                      />
                    ))}
                  </div>
                  <textarea 
                    rows="3" 
                    className="input-field" 
                    placeholder="Chia sẻ trải nghiệm của bạn..."
                    value={newReview.comment}
                    onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
                    required
                    style={{ marginBottom: '10px' }}
                  ></textarea>
                  <button type="submit" className="btn-premium btn-primary" disabled={isSubmitting} style={{ padding: '8px 16px', fontSize: '0.9rem' }}>
                    {isSubmitting ? 'Đang gửi...' : 'Gửi đánh giá'}
                  </button>
                </form>

                {/* Reviews List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                  {reviews.length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontStyle: 'italic' }}>Chưa có đánh giá nào. Hãy là người đầu tiên!</div>
                  ) : (
                    reviews.map((rv) => (
                      <div key={rv.id} style={{ padding: '12px', background: 'var(--bg-main)', borderRadius: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                          <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{rv.userName}</span>
                          <span style={{ color: '#FFD700', fontSize: '0.85rem' }}>
                            {"★".repeat(rv.rating)}{"☆".repeat(5 - rv.rating)}
                          </span>
                        </div>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{rv.comment}</p>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                          {new Date(rv.createdAt).toLocaleDateString('vi-VN')}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            </div>

            {/* Right Panel (Trips List) */}
            {showTripsModal && (
              <div style={{
                flex: 1,
                borderLeft: '1px solid var(--border-light)',
                background: 'var(--bg-main)',
                display: 'flex', flexDirection: 'column',
                overflowY: 'auto', minWidth: '400px'
              }}>
                <div style={{ padding: '20px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, background: 'var(--bg-main)', zIndex: 10 }}>
                  <h3 style={{ margin: 0, color: 'var(--primary)', fontSize: '1.2rem' }}>Chuyến đi sử dụng địa điểm này</h3>
                  <button onClick={() => setShowTripsModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                    <FiX size={24} />
                  </button>
                </div>
                <div style={{ padding: '20px', flex: 1 }}>
                  {loadingTrips ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Đang tải danh sách chuyến đi...</div>
                  ) : tripsWithLocation.length === 0 ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>Chưa có chuyến đi nào sử dụng địa điểm này.</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {tripsWithLocation.map((trip, idx) => (
                        <div 
                          key={idx} 
                          onClick={() => navigate('/trip-plan', { state: { tripId: trip.tripId } })}
                          style={{ 
                            padding: '16px', background: 'var(--bg-card)', borderRadius: '8px', 
                            border: '1px solid var(--border-light)', cursor: 'pointer',
                            transition: 'all 0.2s', boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--primary)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
                          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-light)'; e.currentTarget.style.transform = 'translateY(0)' }}
                        >
                          <h4 style={{ margin: '0 0 8px 0', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <FiMapPin size={16} /> Đến {trip.destination}
                          </h4>
                          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                            Thời gian: {trip.durationDays} ngày
                          </div>
                          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                            Dự kiến: {trip.totalBudget ? `${Number(trip.totalBudget).toLocaleString('vi-VN')} ₫` : 'Không xác định'}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 10000,
          display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px'
        }}>
          <div className="card-premium" style={{ width: '100%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto', background: 'var(--bg-main)', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ color: 'var(--primary)', margin: 0 }}>Sửa thông tin địa điểm</h2>
              <button onClick={() => setShowEditModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <FiX size={24} />
              </button>
            </div>
            
            <form onSubmit={handleSaveEdit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Tên địa điểm / Phương tiện *</label>
                <input type="text" className="input-field" required value={editData.name} onChange={e => setEditData({...editData, name: e.target.value})} />
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Danh mục *</label>
                  <select className="input-field" value={editData.category} onChange={e => setEditData({...editData, category: e.target.value})}>
                    <option value="Stay">Khách sạn / Nơi ở</option>
                    <option value="Activity">Hoạt động tham quan</option>
                    <option value="Food">Quán ăn / Nhà hàng</option>
                    <option value="Transport">Di chuyển / Phương tiện</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Giá dự kiến (VNĐ)</label>
                  <input type="number" className="input-field" value={editData.estimatedPrice} onChange={e => setEditData({...editData, estimatedPrice: e.target.value})} />
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Tỉnh / Thành phố *</label>
                  <select 
                    className="input-field" 
                    required 
                    value={editData.province_name} 
                    onChange={e => setEditData({...editData, province_name: e.target.value, ward_name: ''})}
                  >
                    <option value="" disabled>-- Chọn Tỉnh / Thành phố --</option>
                    {provincesList.map(prov => (
                      <option key={prov} value={prov}>{prov}</option>
                    ))}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Phường / Xã</label>
                  <select 
                    className="input-field" 
                    value={editData.ward_name} 
                    onChange={e => setEditData({...editData, ward_name: e.target.value})}
                    disabled={!editData.province_name}
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
                  <input type="number" step="any" className="input-field" value={editData.latitude} onChange={e => setEditData({...editData, latitude: e.target.value})} placeholder="VD: 21.0285" />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Kinh độ (Longitude)</label>
                  <input type="number" step="any" className="input-field" value={editData.longitude} onChange={e => setEditData({...editData, longitude: e.target.value})} placeholder="VD: 105.8542" />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Link hình ảnh</label>
                <input type="text" className="input-field" value={editData.image} onChange={e => setEditData({...editData, image: e.target.value})} placeholder="https://..." />
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Mô tả</label>
                <textarea className="input-field" rows="4" value={editData.description} onChange={e => setEditData({...editData, description: e.target.value})}></textarea>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '10px' }}>
                <button type="button" onClick={() => setShowEditModal(false)} className="btn-premium btn-secondary" style={{ padding: '10px 20px' }}>Hủy</button>
                <button type="submit" className="btn-premium btn-primary" style={{ padding: '10px 20px' }} disabled={isSaving}>
                  {isSaving ? 'Đang lưu...' : 'Lưu thay đổi'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default DestinationCard;
