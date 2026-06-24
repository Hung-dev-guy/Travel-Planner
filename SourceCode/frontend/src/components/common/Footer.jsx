import React from 'react';
import { Link } from 'react-router-dom';
import { FiFacebook, FiInstagram, FiYoutube } from 'react-icons/fi';
import { FaTiktok, FaTelegramPlane } from 'react-icons/fa';

const Footer = () => {
  return (
    <footer style={{ background: 'var(--primary)', color: '#fff', padding: '60px 24px', fontSize: '0.9rem', marginTop: 'auto' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '40px' }}>
        
        {/* Col 1 */}
        <div>
          <img src="/logo_traveloka.png" alt="Traplanner" style={{ height: '40px', marginBottom: '20px', filter: 'brightness(0) invert(1)' }} />
          {/* Mock badges */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
             <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.2)', borderRadius: '24px', fontSize: '0.75rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
               <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/IATA_logo.svg/1200px-IATA_logo.svg.png" style={{ height: '14px', filter: 'brightness(0) invert(1)' }} alt="IATA" />
             </div>
             <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.2)', borderRadius: '24px', fontSize: '0.75rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px', color: '#fff' }}>
                ĐÃ ĐĂNG KÝ
             </div>
          </div>
          
          <button style={{ background: '#fff', color: 'var(--primary)', border: 'none', borderRadius: '24px', padding: '12px 24px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginBottom: '30px' }}>
            Hợp tác với Traplanner
          </button>
          
          <h4 style={{ marginBottom: '16px', fontSize: '1rem', fontWeight: 600 }}>Đối tác thanh toán</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {Array.from({ length: 16 }).map((_, i) => (
              <div key={i} style={{ width: '45px', height: '30px', background: '#fff', borderRadius: '4px', opacity: 0.9 }} />
            ))}
          </div>
        </div>
        
        {/* Col 2 */}
        <div>
          <h4 style={{ marginBottom: '20px', fontSize: '1rem', fontWeight: 600 }}>Về Traplanner</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Cách đặt chỗ</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Liên hệ chúng tôi</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Trợ giúp</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Tuyển dụng</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Về chúng tôi</Link>
          </div>
          
          <h4 style={{ margin: '40px 0 20px 0', fontSize: '1rem', fontWeight: 600 }}>Theo dõi chúng tôi trên</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}><FiFacebook size={18} /> Facebook</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}><FiInstagram size={18} /> Instagram</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}><FaTiktok size={18} /> TikTok</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}><FiYoutube size={18} /> Youtube</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}><FaTelegramPlane size={18} /> Telegram</Link>
          </div>
        </div>

        {/* Col 3 */}
        <div>
          <h4 style={{ marginBottom: '20px', fontSize: '1rem', fontWeight: 600 }}>Sản phẩm</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Khách sạn</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Vé máy bay</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Vé xe khách</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Đưa đón sân bay</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Cho thuê xe</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Hoạt động & Vui chơi</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Du thuyền</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Biệt thự</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Căn hộ</Link>
          </div>
        </div>

        {/* Col 4 */}
        <div>
          <h4 style={{ marginBottom: '20px', fontSize: '1rem', fontWeight: 600 }}>Khác</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Traplanner Affiliate</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Giới thiệu bạn bè</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Traplanner Blog</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Chính Sách Quyền Riêng</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Điều khoản & Điều kiện</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Đăng ký nơi nghỉ của bạn</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Đăng ký doanh nghiệp hoạt động du lịch của bạn</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Khu vực báo chí</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Quy chế hoạt động</Link>
            <Link to="#" style={{ color: '#e2e8f0', textDecoration: 'none', fontWeight: 500 }}>Vulnerability Disclosure Program</Link>
          </div>
          
          <h4 style={{ margin: '40px 0 20px 0', fontSize: '1rem', fontWeight: 600 }}>Tải ứng dụng Traplanner</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ background: '#000', padding: '8px 16px', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', width: 'fit-content', border: '1px solid #334155' }}>
               <img src="https://upload.wikimedia.org/wikipedia/commons/7/78/Google_Play_Store_badge_EN.svg" alt="Google Play" style={{ height: '30px' }} />
            </div>
            <div style={{ background: '#000', padding: '8px 16px', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', width: 'fit-content', border: '1px solid #334155' }}>
               <img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Download_on_the_App_Store_Badge.svg" alt="App Store" style={{ height: '30px' }} />
            </div>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
