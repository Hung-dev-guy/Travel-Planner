import React from 'react';
import { FiCpu, FiMap, FiPieChart } from 'react-icons/fi';

const FeaturesPage = () => {
  const features = [
    {
      title: 'AI Lên Kế Hoạch',
      description: 'AI tiên tiến của chúng tôi phân tích sở thích của bạn để tạo ra lịch trình hoàn hảo chỉ trong vài giây.',
      icon: <FiCpu />,
      color: 'var(--primary)'
    },
    {
      title: 'Tùy chỉnh Lộ trình',
      description: 'Thêm, xóa hoặc sắp xếp lại các hoạt động với giao diện kéo thả trực quan.',
      icon: <FiMap />,
      color: 'var(--secondary)'
    },
    {
      title: 'Tối ưu Ngân sách',
      description: 'Theo dõi chi tiêu với ước tính giá thực tế và mẹo tiết kiệm chi phí.',
      icon: <FiPieChart />,
      color: 'var(--accent)'
    },
    {
      title: 'Bản đồ Tương tác',
      description: 'Hình dung hành trình của bạn với hệ thống bản đồ tích hợp và hỗ trợ ngoại tuyến.',
      icon: '🗺️',
      color: '#10b981'
    }
  ];

  return (
    <div className="features-page" style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h1 style={{ 
          fontSize: '3.5rem', 
          marginBottom: '16px', 
          background: 'linear-gradient(to right, var(--primary), var(--secondary))', 
          WebkitBackgroundClip: 'text', 
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          color: 'transparent',
          lineHeight: '1.2',
          paddingBottom: '10px'
        }}>
          Nâng tầm Trải nghiệm Du lịch
        </h1>
        <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '700px', margin: '0 auto' }}>
          Khám phá những tính năng mạnh mẽ khiến Traplanner trở thành người bạn đồng hành lý tưởng cho chuyến đi tiếp theo của bạn.
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
        {features.map((feature, index) => (
          <div key={index} className="card-premium" style={{ borderTop: `4px solid ${feature.color}` }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '20px' }}>{feature.icon}</div>
            <h3 style={{ marginBottom: '12px' }}>{feature.title}</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>{feature.description}</p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '80px', textAlign: 'center', padding: '60px', background: 'white', borderRadius: 'var(--card-radius)', boxShadow: 'var(--shadow-premium)' }}>
          <h2 style={{ marginBottom: '20px', color: 'var(--primary)' }}>Bạn đã sẵn sàng lên kế hoạch?</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '30px' }}>Tham gia cùng hàng ngàn khách du lịch đã tin tưởng Traplanner cho hành trình của họ.</p>
          <button className="btn-premium btn-primary" style={{ padding: '16px 40px', fontSize: '1.1rem' }}>Tạo tài khoản miễn phí</button>
      </div>
    </div>
  );
};

export default FeaturesPage;
