import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./logincss.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
import { environment } from "../environment/environment"
const Login = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${environment.baseUrl}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,    
          password, 
        }),
      });
      if (response.status === 200) {
        const data = await response.json();
        console.log("data"+data)
        const user_id  = data.user_id; // Extract user_id from the response
        console.log("userid-----"+user_id)

        console.log(data.message); // You can handle user_id here if needed
        onLoginSuccess(user_id); // Call the function to update authentication state
        navigate('/chatbot'); // Redirect to chatbot after successful login
      } else if (response.status === 401) {
        const errorData = await response.json();
        setError(errorData.message);
      } else {
        setError('Something went wrong. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Unable to connect. Please check your network.');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev); // Toggle password visibility state
  };

//   return (
//     <div className="login-container">
//       <h2>Login to Chatbot</h2>
//       {error && <p className="error-message">{error}</p>}
//       <form onSubmit={handleLogin}>
//         <div className="form-group">
//           <label>Email:</label>
//           <input
//             type="text"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             required
//           />
//         </div>
//         <div className="form-group">
//           <label>Password:</label>
//           <input
//             type="password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             required
//           />
//         </div>
//         <button type="submit">Login</button>
//       </form>
//     </div>
//   );
return (
    <div className="login-container">
      <h2>Login to Chatbot</h2>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="input-field"
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="input-field"
          />
        </div>
        <button type="submit" className="login-button">Login</button>
      </form>
    </div>
  );
};

export default Login;
