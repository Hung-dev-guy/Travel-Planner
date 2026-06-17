import React from 'react';

const AboutPage = () => {
  return (
    <div className="about-page" style={{ maxWidth: '800px', margin: '0 auto', padding: '60px 20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '24px', color: 'var(--primary)' }}>Sứ mệnh của chúng tôi</h1>
        <div style={{ width: '80px', height: '4px', background: 'var(--primary)', margin: '0 auto 24px auto', borderRadius: '2px' }}></div>
        <p style={{ fontSize: '1.4rem', lineHeight: '1.8', color: 'var(--text-primary)', fontWeight: 500 }}>
          "Làm cho mọi hành trình trở nên liền mạch, cá nhân hóa và khó quên thông qua sức mạnh của trí tuệ nhân tạo."
        </p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '60px' }}>
        <section>
          <h2 style={{ marginBottom: '20px', color: 'var(--primary)' }}>Chúng tôi là ai</h2>
          <p style={{ fontSize: '1.1rem', lineHeight: '1.7', color: 'var(--text-secondary)' }}>
            Traplanner được thành lập bởi một nhóm những người đam mê du lịch và công nghệ, những người tin rằng việc lên kế hoạch cho một chuyến đi không nên là một gánh nặng. Chúng tôi đã thấy một thế giới với vô số thông tin phân mảnh và hàng tá tab trình duyệt, và chúng tôi quyết định xây dựng một cách tốt hơn.
          </p>
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px' }}>
            <div className="card-premium">
                <h3 style={{ marginBottom: '16px' }}>Tầm nhìn</h3>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    Một thế giới nơi việc lập kế hoạch du lịch thú vị như chính chuyến đi, và nơi AI trao quyền cho con người khám phá thế giới với sự tự tin và tò mò.
                </p>
            </div>
            <div className="card-premium">
                <h3 style={{ marginBottom: '16px' }}>Giá trị cốt lõi</h3>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    Chính trực, Đổi mới và Kết nối. Chúng tôi tin vào việc trung thực với người dùng và không ngừng vượt qua giới hạn của những gì có thể.
                </p>
            </div>
        </section>

        <section style={{ textAlign: 'center', marginTop: '40px' }}>
          <h2 style={{ marginBottom: '30px' }}>Đội ngũ của chúng tôi</h2>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '30px', flexWrap: 'wrap' }}>
            {[1, 2, 3].map(i => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: 'var(--border-light)', margin: '0 auto 16px auto', overflow: 'hidden' }}>
                    {/* Placeholder for team member image */}
                    <div style={{ width: '100%', height: '100%', background: 'var(--primary)', opacity: 0.1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem' }}>👤</div>
                </div>
                <div style={{ fontWeight: 600 }}>Thành viên {i}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Kỹ sư sáng lập</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default AboutPage;
