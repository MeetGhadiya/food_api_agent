/**
 * Frontend Registration Handler with User-Friendly Error Popups
 * 
 * This example shows how to handle the backend error messages
 * and display appropriate popups to users.
 */

// Registration function with error handling
async function registerUser(formData) {
    try {
        const response = await fetch('http://localhost:8000/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                first_name: formData.firstName || '',
                last_name: formData.lastName || ''
            })
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle different error types
            if (response.status === 400) {
                // 400 = User already exists
                const errorMessage = data.detail;
                
                if (errorMessage.includes('email is already registered')) {
                    // Email already exists
                    showErrorPopup(
                        'Already Registered!',
                        'This email is already registered. Would you like to login instead?',
                        'Login',
                        () => redirectToLogin()
                    );
                } else if (errorMessage.includes('username is already taken')) {
                    // Username already exists
                    showErrorPopup(
                        'Username Taken',
                        'This username is already taken. Please try a different username.',
                        'OK',
                        null
                    );
                } else if (errorMessage.includes('Password')) {
                    // Password validation error
                    showErrorPopup(
                        'Weak Password',
                        errorMessage,
                        'OK',
                        null
                    );
                } else {
                    // Generic error
                    showErrorPopup('Registration Error', errorMessage, 'OK', null);
                }
                
                return null;
            } else if (response.status === 422) {
                // 422 = Validation error (missing fields)
                showErrorPopup(
                    'Invalid Input',
                    'Please fill in all required fields correctly.',
                    'OK',
                    null
                );
                return null;
            } else {
                // Other errors
                throw new Error(data.detail || 'Registration failed');
            }
        }

        // Success!
        showSuccessPopup(
            'Registration Successful!',
            'Your account has been created. You can now login.',
            'Login Now',
            () => redirectToLogin()
        );
        
        return data;

    } catch (error) {
        console.error('Registration error:', error);
        showErrorPopup(
            'Network Error',
            'Unable to connect to server. Please check your internet connection.',
            'OK',
            null
        );
        return null;
    }
}

// Helper function to show error popup
function showErrorPopup(title, message, buttonText, onButtonClick) {
    // Using browser alert (replace with your custom modal)
    if (confirm(`${title}\n\n${message}\n\nClick OK to ${buttonText}`)) {
        if (onButtonClick) {
            onButtonClick();
        }
    }
}

// Helper function to show success popup
function showSuccessPopup(title, message, buttonText, onButtonClick) {
    alert(`${title}\n\n${message}`);
    if (onButtonClick) {
        onButtonClick();
    }
}

// Helper function to redirect to login
function redirectToLogin() {
    // Replace with your actual login page redirect
    window.location.href = '/login';
}

// ====================================================================
// REACT COMPONENT EXAMPLE
// ====================================================================

import React, { useState } from 'react';

function RegistrationForm() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [modalContent, setModalContent] = useState({
        title: '',
        message: '',
        type: 'error' // 'error' or 'success'
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/users/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 400) {
                    const errorMsg = data.detail;
                    
                    // Show appropriate popup based on error
                    if (errorMsg.includes('email is already registered')) {
                        setModalContent({
                            title: '⚠️ Already Registered',
                            message: 'This email is already registered. Would you like to login instead?',
                            type: 'warning',
                            showLoginButton: true
                        });
                    } else if (errorMsg.includes('username is already taken')) {
                        setModalContent({
                            title: '⚠️ Username Taken',
                            message: 'This username is already taken. Please choose a different username.',
                            type: 'error',
                            showLoginButton: false
                        });
                    } else {
                        setModalContent({
                            title: '❌ Registration Error',
                            message: errorMsg,
                            type: 'error',
                            showLoginButton: false
                        });
                    }
                    setShowModal(true);
                } else {
                    setError(data.detail || 'Registration failed');
                }
            } else {
                // Success!
                setModalContent({
                    title: '✅ Registration Successful!',
                    message: 'Your account has been created successfully. You can now login.',
                    type: 'success',
                    showLoginButton: true
                });
                setShowModal(true);
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="registration-form">
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    required
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Registering...' : 'Register'}
                </button>
            </form>

            {error && <div className="error-message">{error}</div>}

            {/* Custom Modal/Popup */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>{modalContent.title}</h2>
                        <p>{modalContent.message}</p>
                        <div className="modal-buttons">
                            <button onClick={() => setShowModal(false)}>
                                OK
                            </button>
                            {modalContent.showLoginButton && (
                                <button 
                                    onClick={() => window.location.href = '/login'}
                                    className="primary-button"
                                >
                                    Go to Login
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default RegistrationForm;

// ====================================================================
// CSS FOR MODAL (Add to your styles)
// ====================================================================

/*
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 30px;
    border-radius: 10px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-content h2 {
    margin-top: 0;
    color: #333;
}

.modal-content p {
    color: #666;
    line-height: 1.6;
}

.modal-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.modal-buttons button {
    flex: 1;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}

.modal-buttons button:first-child {
    background: #e0e0e0;
    color: #333;
}

.modal-buttons button.primary-button {
    background: #FF6B35;
    color: white;
}
*/
