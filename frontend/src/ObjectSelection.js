import React, { useState } from 'react';
import './ObjectSelection.css'; // Assuming you'll create this CSS file

function ObjectSelection({ objects, selectedObjectType, onObjectSelect }) {
  const [selectedObjects, setSelectedObjects] = useState([]);

  const handleCheckboxChange = (objectName) => {
    setSelectedObjects((prevSelected) => {
      const newSelected = prevSelected.includes(objectName)
        ? prevSelected.filter((name) => name !== objectName)
        : [...prevSelected, objectName];
      onObjectSelect(newSelected); // Pass selected objects up to parent
      return newSelected;
    });
  };

  if (!objects || objects.length === 0) {
    return <p>No {selectedObjectType}s found.</p>;
  }

  return (
    <div className="object-selection-container">
      <h3>Select {selectedObjectType}s for Migration</h3>
      <div className="object-list">
        {objects.map((objectName) => (
          <div key={objectName} className="object-item">
            <input
              type="checkbox"
              id={objectName}
              checked={selectedObjects.includes(objectName)}
              onChange={() => handleCheckboxChange(objectName)}
            />
            <label htmlFor={objectName}>{objectName}</label>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ObjectSelection;