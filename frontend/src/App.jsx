import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  // API Configuration
  const [apiUrl, setApiUrl] = useState('https://2dkg00hb3h.execute-api.eu-west-2.amazonaws.com/dev')
  
  // Form states
  const [getCategory, setGetCategory] = useState('')
  const [getItemId, setGetItemId] = useState('')
  const [postData, setPostData] = useState({
    name: '',
    description: '',
    category: '',
    price: ''
  })
  const [putItemId, setPutItemId] = useState('')
  const [putData, setPutData] = useState({
    name: '',
    description: '',
    category: '',
    price: ''
  })
  const [deleteItemId, setDeleteItemId] = useState('')
  
  // Response states
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [items, setItems] = useState([])

  // Axios instance with base configuration
  const api = axios.create({
    baseURL: apiUrl,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    }
  })

  // Update API instance when URL changes
  useEffect(() => {
    api.defaults.baseURL = apiUrl
  }, [apiUrl])

  const handleRequest = async (method, endpoint, data = null, params = null) => {
    setLoading(true)
    setError(null)
    
    try {
      const config = {
        method,
        url: endpoint,
        ...(data && { data }),
        ...(params && { params })
      }
      
      const result = await api.request(config)
      setResponse({
        status: result.status,
        statusText: result.statusText,
        data: result.data,
        timestamp: new Date().toISOString()
      })
      
      // If it's a GET /items request, update the items list
      if (method === 'get' && endpoint === '/items') {
        setItems(result.data.items || [])
      }
      
    } catch (err) {
      const errorResponse = {
        status: err.response?.status || 'Network Error',
        statusText: err.response?.statusText || 'Request Failed',
        data: err.response?.data || { error: err.message },
        timestamp: new Date().toISOString()
      }
      setError(errorResponse)
      setResponse(errorResponse)
    } finally {
      setLoading(false)
    }
  }

  // Health Check
  const testHealth = () => {
    handleRequest('get', '/health')
  }

  // GET all items
  const getAllItems = () => {
    const params = getCategory ? { category: getCategory } : null
    handleRequest('get', '/items', null, params)
  }

  // GET single item
  const getSingleItem = () => {
    if (!getItemId.trim()) {
      setError({ data: { error: 'Please enter an item ID' } })
      return
    }
    handleRequest('get', `/items/${getItemId.trim()}`)
  }

  // POST new item
  const createItem = () => {
    if (!postData.name.trim()) {
      setError({ data: { error: 'Name is required' } })
      return
    }
    
    const payload = {
      name: postData.name,
      description: postData.description,
      category: postData.category || 'general',
      price: parseFloat(postData.price) || 0
    }
    
    handleRequest('post', '/items', payload)
  }

  // PUT update item
  const updateItem = () => {
    if (!putItemId.trim()) {
      setError({ data: { error: 'Please enter an item ID' } })
      return
    }
    if (!putData.name.trim()) {
      setError({ data: { error: 'Name is required' } })
      return
    }
    
    const payload = {
      name: putData.name,
      description: putData.description,
      category: putData.category || 'general',
      price: parseFloat(putData.price) || 0
    }
    
    handleRequest('put', `/items/${putItemId.trim()}`, payload)
  }

  // DELETE item
  const deleteItem = () => {
    if (!deleteItemId.trim()) {
      setError({ data: { error: 'Please enter an item ID' } })
      return
    }
    handleRequest('delete', `/items/${deleteItemId.trim()}`)
  }

  return (
    <div className="app">
      <div className="header">
        <h1>🚀 AWS Gateway Testing App</h1>
        <p>Test your Lambda backend through API Gateway with all HTTP methods</p>
      </div>

      {/* API Configuration */}
      <div className="api-config">
        <h3>API Configuration</h3>
        <input
          type="text"
          placeholder="Enter your API Gateway URL"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
        />
        <div style={{ marginTop: '1rem' }}>
          <button onClick={testHealth} className="method-button">
            🏥 Test Health Check
          </button>
        </div>
      </div>

      {/* HTTP Methods Testing */}
      <div className="methods-container">
        
        {/* GET Methods */}
        <div className="method-section">
          <h3>📥 GET Methods</h3>
          
          <div className="form-group">
            <label>Filter by Category (optional):</label>
            <input
              type="text"
              placeholder="electronics, books, etc."
              value={getCategory}
              onChange={(e) => setGetCategory(e.target.value)}
            />
          </div>
          <button 
            onClick={getAllItems} 
            className="method-button get"
            disabled={loading}
          >
            GET /items - Get All Items
          </button>

          <div className="form-group" style={{ marginTop: '1rem' }}>
            <label>Item ID:</label>
            <input
              type="text"
              placeholder="Enter item ID"
              value={getItemId}
              onChange={(e) => setGetItemId(e.target.value)}
            />
          </div>
          <button 
            onClick={getSingleItem} 
            className="method-button get"
            disabled={loading}
          >
            GET /items/:id - Get Single Item
          </button>
        </div>

        {/* POST Method */}
        <div className="method-section">
          <h3>📤 POST Method</h3>
          
          <div className="form-group">
            <label>Name (required):</label>
            <input
              type="text"
              placeholder="Item name"
              value={postData.name}
              onChange={(e) => setPostData({...postData, name: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label>Description:</label>
            <textarea
              placeholder="Item description"
              value={postData.description}
              onChange={(e) => setPostData({...postData, description: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label>Category:</label>
            <input
              type="text"
              placeholder="electronics, books, etc."
              value={postData.category}
              onChange={(e) => setPostData({...postData, category: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label>Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={postData.price}
              onChange={(e) => setPostData({...postData, price: e.target.value})}
            />
          </div>
          
          <button 
            onClick={createItem} 
            className="method-button post"
            disabled={loading}
          >
            POST /items - Create Item
          </button>
        </div>

        {/* PUT Method */}
        <div className="method-section">
          <h3>✏️ PUT Method</h3>
          
          <div className="form-group">
            <label>Item ID to Update:</label>
            <input
              type="text"
              placeholder="Enter item ID"
              value={putItemId}
              onChange={(e) => setPutItemId(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label>Name (required):</label>
            <input
              type="text"
              placeholder="Updated name"
              value={putData.name}
              onChange={(e) => setPutData({...putData, name: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label>Description:</label>
            <textarea
              placeholder="Updated description"
              value={putData.description}
              onChange={(e) => setPutData({...putData, description: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label>Category:</label>
            <input
              type="text"
              placeholder="Updated category"
              value={putData.category}
              onChange={(e) => setPutData({...putData, category: e.target.value})}
            />
          </div>
          
          <div className="form-group">
            <label>Price:</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={putData.price}
              onChange={(e) => setPutData({...putData, price: e.target.value})}
            />
          </div>
          
          <button 
            onClick={updateItem} 
            className="method-button put"
            disabled={loading}
          >
            PUT /items/:id - Update Item
          </button>
        </div>

        {/* DELETE Method */}
        <div className="method-section">
          <h3>🗑️ DELETE Method</h3>
          
          <div className="form-group">
            <label>Item ID to Delete:</label>
            <input
              type="text"
              placeholder="Enter item ID"
              value={deleteItemId}
              onChange={(e) => setDeleteItemId(e.target.value)}
            />
          </div>
          
          <button 
            onClick={deleteItem} 
            className="method-button delete"
            disabled={loading}
          >
            DELETE /items/:id - Delete Item
          </button>
        </div>
      </div>

      {/* Current Items */}
      {items.length > 0 && (
        <div className="items-list">
          <h3>📋 Current Items ({items.length})</h3>
          {items.map((item) => (
            <div key={item.id} className="item">
              <h4>{item.name}</h4>
              <p><strong>ID:</strong> {item.id}</p>
              <p><strong>Description:</strong> {item.description || 'No description'}</p>
              <p><strong>Category:</strong> {item.category}</p>
              <p><strong>Price:</strong> ${item.price}</p>
              <p><strong>Created:</strong> {new Date(item.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}

      {/* Response Section */}
      <div className="response-section">
        <h3>📡 API Response</h3>
        
        {loading && <div className="loading">Making request...</div>}
        
        {error && (
          <div className="error">
            <strong>Error {error.status}:</strong> {error.statusText}
            <div className="response-content">
              {JSON.stringify(error.data, null, 2)}
            </div>
          </div>
        )}
        
        {response && !error && (
          <div className="success">
            <strong>Success {response.status}:</strong> {response.statusText}
            <div className="response-content">
              {JSON.stringify(response.data, null, 2)}
            </div>
          </div>
        )}
        
        {!response && !loading && !error && (
          <div style={{ color: '#888' }}>
            No requests made yet. Try testing the health check first!
          </div>
        )}
      </div>
    </div>
  )
}

export default App