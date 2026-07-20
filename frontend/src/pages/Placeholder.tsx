import React from 'react';
import { Empty } from 'antd';
import { useLocation } from 'react-router-dom';

// 未实现模块的通用占位页
const Placeholder: React.FC = () => {
  const location = useLocation();
  return (
    <div style={{ padding: 48, background: '#fff', margin: 24, borderRadius: 8 }}>
      <Empty description={`该模块（${location.pathname}）待开发`} />
    </div>
  );
};

export default Placeholder;
