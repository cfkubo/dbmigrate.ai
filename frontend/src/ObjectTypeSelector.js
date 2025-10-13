import React from 'react';
import './ObjectTypeSelector.css'; // We'll create this CSS file next

// Placeholder images - replace with actual icons later
import tableIcon from './assets/table-icon.png'; // Assuming you'll add these icons
import procedureIcon from './assets/procedure-icon.png';
import functionIcon from './assets/function-icon.png';
import viewIcon from './assets/view-icon.png';
import packageIcon from './assets/package-icon.png';
import indexIcon from './assets/index-icon.png';
import triggerIcon from './assets/trigger-icon.png';

const iconMap = {
  'TABLE': tableIcon,
  'PROCEDURE': procedureIcon,
  'FUNCTION': functionIcon,
  'VIEW': viewIcon,
  'PACKAGE': packageIcon,
  'INDEX': indexIcon,
  'TRIGGER': triggerIcon,
};

function ObjectTypeSelector({ objectTypes, selectedObjectType, onSelectObjectType }) {
  return (
    <div className="object-type-selector">
      {objectTypes.map((type) => (
        <div
          key={type}
          className={`object-type-block ${selectedObjectType === type ? 'selected' : ''}`}
          onClick={() => onSelectObjectType(type)}
        >
          <img src={iconMap[type]} alt={type} className="object-type-icon" />
          <p>{type}</p>
        </div>
      ))}
    </div>
  );
}

export default ObjectTypeSelector;
