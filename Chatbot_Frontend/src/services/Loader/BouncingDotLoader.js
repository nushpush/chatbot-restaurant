import React from "react";
import "./BouncingDotLoader.css";
const BouncingDotsLoader = (props) => {
  return (
      <div className="bouncing-loader" role="presentation" aria-label="Loading">
        <div></div>
        <div></div>
        <div></div>
      </div>
  );
};

export default BouncingDotsLoader;