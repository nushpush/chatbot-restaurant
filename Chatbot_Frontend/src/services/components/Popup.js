import React, { useEffect } from 'react';
import './popup.css';

const Popup = ({ message, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 1000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="popup-component">
      <div className="popup-overlay">
        <div className="popup">
          <h2>{message}</h2>
        </div>
      </div>
    </div>
  );
};

export default Popup;
