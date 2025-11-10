import React, { useState } from 'react';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
    const [url, setUrl] = useState('');
    const [shortUrl, setShortUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [copied, setCopied] = useState(false);

    const validateUrl = (urlString) => {
        try {
            if (!urlString.startsWith('http://') && !urlString.startsWith('https://')) {
                urlString = 'https://' + urlString;
            }

            const url = new URL(urlString);

            if (!url.hostname || url.hostname.length < 3) {
                return { valid: false, error: 'Invalid website address' };
            }

            return { valid: true, url: urlString };
        } catch (e) {
            return { valid: false, error: 'Invalid website address' };
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError('');
        setShortUrl('');
        setCopied(false);

        const trimmedUrl = url.trim();

        if (!trimmedUrl) {
            setError('Enter the URL');
            return;
        }

        const validation = validateUrl(trimmedUrl);
        if (!validation.valid) {
            setError(validation.error);
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/shorten/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: validation.url }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error in shortening the URL');
            }

            setShortUrl(data.short_url);

        } catch (err) {
            console.error('Error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setUrl('');
        setShortUrl('');
        setError('');
        setCopied(false);
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(shortUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="app">
            <div className="container">
                <header className="header">
                    <div className="logo">
                        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                            <rect x="5" y="5" width="30" height="30" rx="6" fill="url(#gradient)" />
                            <path d="M15 20L20 15L25 20M20 15V28" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                            <defs>
                                <linearGradient id="gradient" x1="5" y1="5" x2="35" y2="35">
                                    <stop offset="0%" stopColor="#667eea" />
                                    <stop offset="100%" stopColor="#764ba2" />
                                </linearGradient>
                            </defs>
                        </svg>
                        <h1>URL Shortener</h1>
                    </div>
                    <p className="subtitle">The best tool for shortening your long URLs</p>
                </header>

                <div className="card">
                    <form onSubmit={handleSubmit} className="form">
                        <div className="input-wrapper">
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="Enter your long URL here..."
                                className={`input ${error ? 'input-error' : ''}`}
                                disabled={loading}
                            />
                            {url && (
                                <button
                                    type="button"
                                    onClick={handleReset}
                                    className="clear-button"
                                    disabled={loading}
                                >
                                    ×
                                </button>
                            )}
                        </div>

                        {error && (
                            <div className="error-message">
                                <span>⚠️</span>
                                <span>{error}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            className="submit-button"
                            disabled={loading || !url}
                        >
                            {loading ? (
                                <>
                                    <div className="spinner"></div>
                                    <span>Shortening...</span>
                                </>
                            ) : (
                                <>
                                    <span>✨</span>
                                    <span>Shorten URL</span>
                                </>
                            )}
                        </button>
                    </form>

                    {shortUrl && (
                        <div className="result">
                            <div className="result-header">
                                <span>✅</span>
                                <span>Your shortened URL is ready!</span>
                            </div>
                            <div className="result-content">
                                <div className="short-url-display">
                                    <a
                                        href={shortUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="short-url-link"
                                    >
                                        {shortUrl}
                                    </a>
                                </div>
                                <button
                                    onClick={copyToClipboard}
                                    className="submit-button"
                                    style={{ width: 'auto', padding: '0.875rem 1.5rem' }}
                                >
                                    {copied ? '✓ Copied!' : '📋 Copy'}
                                </button>
                            </div>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}

export default App;