'use client';
import { useState, useRef } from 'react';

export default function ImageEditor() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);
  const [enableCrop, setEnableCrop] = useState(false);

  const [settings, setSettings] = useState({
    width: 0,
    height: 0,
    rotation: 0,
    flip: 'none',
    crop: {
      x: 0,
      y: 0,
      width: 0,
      height: 0
    }
  });

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setImage(file);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) return;

    const formData = new FormData();
    formData.append('image', image);
    
    // Kırpma ayarlarını yalnızca etkinse dahil et
    const requestSettings = {
      ...settings,
      cropEnabled: enableCrop
    };
    
    formData.append('settings', JSON.stringify(requestSettings));

    try {
      const response = await fetch('http://localhost:8000/process-image', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Server error');
      }

      const blob = await response.blob();
      setPreview(URL.createObjectURL(blob));
    } catch (error) {
      console.error('Error:', error.message);
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="container">
      <h1 className="pageTitle">Image Editor</h1>
      
      <div className="editor-container">
        {/* Form Section */}
        <div className="form-section">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Select Image</label>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageChange}
                accept="image/*"
              />
            </div>

            <div className="form-group">
              <label>Width</label>
              <input
                type="number"
                value={settings.width}
                onChange={(e) => setSettings({...settings, width: parseInt(e.target.value || 0)})}
                min="1"
              />
            </div>

            <div className="form-group">
              <label>Height</label>
              <input
                type="number"
                value={settings.height}
                onChange={(e) => setSettings({...settings, height: parseInt(e.target.value || 0)})}
                min="1"
              />
            </div>

            <div className="form-group">
              <label>Rotation: {settings.rotation}°</label>
              <input
                type="range"
                min="0"
                max="360"
                value={settings.rotation}
                onChange={(e) => setSettings({...settings, rotation: parseInt(e.target.value)})}
              />
            </div>

            <div className="form-group">
              <label>Flip</label>
              <select
                value={settings.flip}
                onChange={(e) => setSettings({...settings, flip: e.target.value})}
              >
                <option value="none">None</option>
                <option value="horizontal">Horizontal</option>
                <option value="vertical">Vertical</option>
                <option value="both">Both</option>
              </select>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={enableCrop}
                  onChange={(e) => setEnableCrop(e.target.checked)}
                />
                Enable Crop
              </label>
            </div>

            {enableCrop && (
              <div className="crop-settings">
                <h3>Crop Settings</h3>
                <div className="crop-grid">
                  <div>
                    <label>X</label>
                    <input
                      type="number"
                      value={settings.crop.x}
                      onChange={(e) => setSettings({...settings, crop: {...settings.crop, x: parseInt(e.target.value || 0)}})}
                      min="0"
                    />
                  </div>
                  <div>
                    <label>Y</label>
                    <input
                      type="number"
                      value={settings.crop.y}
                      onChange={(e) => setSettings({...settings, crop: {...settings.crop, y: parseInt(e.target.value || 0)}})}
                      min="0"
                    />
                  </div>
                  <div>
                    <label>Width</label>
                    <input
                      type="number"
                      value={settings.crop.width}
                      onChange={(e) => setSettings({...settings, crop: {...settings.crop, width: parseInt(e.target.value || 0)}})}
                      min="1"
                    />
                  </div>
                  <div>
                    <label>Height</label>
                    <input
                      type="number"
                      value={settings.crop.height}
                      onChange={(e) => setSettings({...settings, crop: {...settings.crop, height: parseInt(e.target.value || 0)}})}
                      min="1"
                    />
                  </div>
                </div>
              </div>
            )}

            <button type="submit" disabled={!image}>
              Process Image
            </button>
          </form>
        </div>

        {/* Preview Section */}
        <div className="preview-section">
          <h2>Preview</h2>
          {preview ? (
            <img src={preview} alt="Preview" />
          ) : (
            <div className="empty-preview">
              <p>No image selected</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}